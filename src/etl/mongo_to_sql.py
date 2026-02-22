from datetime import datetime
from typing import Optional, Dict, Any
import os
from sqlalchemy import text

from src.config.database import MongoDatabase, PostgresDatabase


class MongoToSqlETL:
    """
    ETL pour transférer les données enrichies de MongoDB vers PostgreSQL.
    Script idempotent : peut être rejoué sans créer de doublons.
    """
    
    def __init__(self):
        self.mongo = MongoDatabase().connect()
        self.postgres = PostgresDatabase().connect()
        self.enriched_collection = self.mongo.get_enriched_collection()
        
        # Cache pour éviter les requêtes répétées
        self._brand_cache: Dict[str, int] = {}
        self._category_cache: Dict[str, int] = {}
    
    def run(self, limit: Optional[int] = None) -> dict:
        """
        Exécute le transfert ETL.
        
        Args:
            limit: Nombre maximum de documents à transférer
            
        Returns:
            Statistiques du transfert
        """
        stats = {'transferred': 0, 'skipped': 0, 'errors': 0}
        
        print("🚀 Démarrage de l'ETL MongoDB → PostgreSQL...")
        print("-" * 50)
        
        # Récupère les documents enrichis avec succès
        query = {'status': 'success'}
        cursor = self.enriched_collection.find(query)
        if limit:
            cursor = cursor.limit(limit)
        
        session = self.postgres.get_session()
        
        try:
            for doc in cursor:
                raw_id = doc['raw_id']
                
                try:
                    # Vérifie si déjà transféré
                    if self._product_exists(session, raw_id):
                        stats['skipped'] += 1
                        continue
                    
                    # Transfère le produit
                    self._transfer_product(session, raw_id, doc['data'])
                    stats['transferred'] += 1
                    
                    if stats['transferred'] % 50 == 0:
                        session.commit()
                        print(f"✅ {stats['transferred']} produits transférés")
                        
                except Exception as e:
                    print(f"❌ Erreur pour {raw_id}: {e}")
                    stats['errors'] += 1
                    session.rollback()
            
            session.commit()
            
        finally:
            session.close()
        
        print("-" * 50)
        print(f"🎉 ETL terminé !")
        print(f"   ✅ Transférés : {stats['transferred']}")
        print(f"   ⏭️ Ignorés : {stats['skipped']}")
        print(f"   ❌ Erreurs : {stats['errors']}")
        
        return stats
    
    def _product_exists(self, session, raw_id: str) -> bool:
        """Vérifie si un produit existe déjà dans PostgreSQL"""
        result = session.execute(
            text("SELECT 1 FROM products WHERE mongo_raw_id = :raw_id"),
            {'raw_id': raw_id}
        )
        return result.fetchone() is not None
    
    def _transfer_product(self, session, raw_id: str, data: dict):
        """Transfère un produit et ses relations"""
        
        # 1. Récupère ou crée la marque
        brand_id = None
        if data.get('brand'):
            brand_id = self._get_or_create_brand(session, data['brand'])
        
        # 2. Insère le produit
        product_id = self._insert_product(session, raw_id, data, brand_id)
        
        # 3. Insère les catégories
        for category_name in data.get('categories', []):
            if category_name:
                category_id = self._get_or_create_category(session, category_name)
                self._link_product_category(session, product_id, category_id)
        
        # 4. Insère les nutriments
        for nutrient_name, nutrient_data in data.get('nutrients', {}).items():
            self._insert_nutrient(session, product_id, nutrient_name, nutrient_data)
        
        # 5. Insère les allergènes
        for allergen in data.get('detected_allergens', []):
            self._insert_allergen(session, product_id, allergen)
    
    def _get_or_create_brand(self, session, brand_name: str) -> int:
        """Récupère ou crée une marque"""
        brand_name = brand_name[:255]  # Limite la longueur
        
        if brand_name in self._brand_cache:
            return self._brand_cache[brand_name]
        
        # Cherche si existe
        result = session.execute(
            text("SELECT id FROM brands WHERE name = :name"),
            {'name': brand_name}
        )
        row = result.fetchone()
        
        if row:
            brand_id = row[0]
        else:
            # Crée la marque
            result = session.execute(
                text("INSERT INTO brands (name) VALUES (:name) RETURNING id"),
                {'name': brand_name}
            )
            brand_id = result.fetchone()[0]
        
        self._brand_cache[brand_name] = brand_id
        return brand_id
    
    def _get_or_create_category(self, session, category_name: str) -> int:
        """Récupère ou crée une catégorie"""
        category_name = category_name[:255]
        
        if category_name in self._category_cache:
            return self._category_cache[category_name]
        
        result = session.execute(
            text("SELECT id FROM categories WHERE name = :name"),
            {'name': category_name}
        )
        row = result.fetchone()
        
        if row:
            category_id = row[0]
        else:
            result = session.execute(
                text("INSERT INTO categories (name) VALUES (:name) RETURNING id"),
                {'name': category_name}
            )
            category_id = result.fetchone()[0]
        
        self._category_cache[category_name] = category_id
        return category_id
    
    def _insert_product(self, session, raw_id: str, data: dict, brand_id: Optional[int]) -> int:
        """Insère un produit"""
        nutriscore = data.get('nutriscore_grade')
        if nutriscore == 'unknown':
            nutriscore = None
        
        result = session.execute(
            text("""
            INSERT INTO products (
                mongo_raw_id, barcode, product_name, brand_id,
                nutriscore_grade, nutriscore_score, quality_score,
                has_image, image_url
            ) VALUES (
                :raw_id, :barcode, :name, :brand_id,
                :nutriscore, :nutriscore_score, :quality,
                :has_image, :image_url
            ) RETURNING id
            """),
            {
                'raw_id': raw_id,
                'barcode': data.get('barcode', '')[:50],
                'name': (data.get('product_name', 'Unknown') or 'Unknown')[:500],
                'brand_id': brand_id,
                'nutriscore': nutriscore,
                'nutriscore_score': data.get('nutriscore_score', 0),
                'quality': data.get('quality_score', 0),
                'has_image': data.get('has_image', False),
                'image_url': data.get('image_url', '')
            }
        )
        return result.fetchone()[0]
    
    def _link_product_category(self, session, product_id: int, category_id: int):
        """Lie un produit à une catégorie"""
        try:
            session.execute(
                text("""
                INSERT INTO product_categories (product_id, category_id)
                VALUES (:pid, :cid)
                ON CONFLICT DO NOTHING
                """),
                {'pid': product_id, 'cid': category_id}
            )
        except Exception:
            pass
    
    def _insert_nutrient(self, session, product_id: int, name: str, data: dict):
        """Insère un nutriment"""
        try:
            session.execute(
                text("""
                INSERT INTO product_nutrients (product_id, nutrient_name, value, unit)
                VALUES (:pid, :name, :value, :unit)
                ON CONFLICT DO NOTHING
                """),
                {
                    'pid': product_id,
                    'name': name,
                    'value': data.get('value'),
                    'unit': data.get('unit', '')
                }
            )
        except Exception:
            pass
    
    def _insert_allergen(self, session, product_id: int, allergen: str):
        """Insère un allergène"""
        try:
            session.execute(
                text("""
                INSERT INTO product_allergens (product_id, allergen_name)
                VALUES (:pid, :name)
                ON CONFLICT DO NOTHING
                """),
                {'pid': product_id, 'name': allergen}
            )
        except Exception:
            pass
    
    def close(self):
        """Ferme les connexions"""
        self.mongo.close()
        self.postgres.close()


def main():
    """Point d'entrée ETL"""
    etl = MongoToSqlETL()
    try:
        etl.run()
    finally:
        etl.close()


if __name__ == '__main__':
    main()