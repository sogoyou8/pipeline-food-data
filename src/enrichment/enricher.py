from datetime import datetime, timezone
from typing import Optional
import re

from src.config.database import MongoDatabase


class ProductEnricher:
    """
    Enrichit les données brutes des produits alimentaires.
    
    Enrichissements implémentés :
    1. Normalisation du Nutriscore (calcul d'un score numérique)
    2. Extraction et catégorisation des nutriments
    3. Détection des allergènes potentiels
    4. Calcul d'un score de qualité interne
    """
    
    # Allergènes courants à détecter
    ALLERGENS = [
        'gluten', 'wheat', 'milk', 'dairy', 'eggs', 'egg', 'nuts', 'peanuts',
        'soy', 'soja', 'fish', 'shellfish', 'sesame', 'mustard', 'celery',
        'lupin', 'molluscs', 'sulphites', 'lait', 'oeufs', 'noix', 'arachides'
    ]
    
    # Mapping Nutriscore vers score numérique
    NUTRISCORE_VALUES = {
        'a': 5,
        'b': 4,
        'c': 3,
        'd': 2,
        'e': 1,
        'unknown': 0
    }
    
    def __init__(self):
        self.db = MongoDatabase().connect()
        self.raw_collection = self.db.get_raw_collection()
        self.enriched_collection = self.db.get_enriched_collection()
        
        # Index pour éviter les doublons
        self.enriched_collection.create_index("raw_id", unique=True)
    
    def enrich_all(self, limit: Optional[int] = None) -> dict:
        """
        Enrichit tous les documents RAW non encore traités.
        
        Args:
            limit: Nombre maximum de documents à traiter (None = tous)
            
        Returns:
            Statistiques d'enrichissement
        """
        # Récupère les IDs déjà enrichis
        enriched_ids = set(
            doc['raw_id'] for doc in self.enriched_collection.find({}, {'raw_id': 1})
        )
        
        # Récupère les documents RAW à enrichir
        query = {}
        cursor = self.raw_collection.find(query)
        if limit:
            cursor = cursor.limit(limit)
        
        stats = {'success': 0, 'failed': 0, 'skipped': 0}
        
        print(f"🔄 Démarrage de l'enrichissement...")
        print("-" * 50)
        
        for raw_doc in cursor:
            raw_id = str(raw_doc['_id'])
            
            # Skip si déjà enrichi
            if raw_id in enriched_ids:
                stats['skipped'] += 1
                continue
            
            try:
                enriched_data = self._enrich_product(raw_doc['payload'])
                self._save_enriched(raw_id, enriched_data)
                stats['success'] += 1
                
                if stats['success'] % 50 == 0:
                    print(f"✅ {stats['success']} produits enrichis")
                    
            except Exception as e:
                self._save_failed(raw_id, str(e))
                stats['failed'] += 1
        
        print("-" * 50)
        print(f"🎉 Enrichissement terminé !")
        print(f"   ✅ Succès : {stats['success']}")
        print(f"   ❌ Échecs : {stats['failed']}")
        print(f"   ⏭️ Ignorés : {stats['skipped']}")
        
        return stats
    
    def _enrich_product(self, payload: dict) -> dict:
        """
        Applique tous les enrichissements à un produit.
        
        Args:
            payload: Données brutes du produit
            
        Returns:
            Données enrichies
        """
        enriched = {
            # Données normalisées
            'product_name': self._clean_string(payload.get('product_name', '')),
            'brand': self._clean_string(payload.get('brands', '')),
            'categories': self._parse_categories(payload.get('categories', '')),
            'countries': self._parse_list(payload.get('countries', '')),
            
            # Enrichissement 1 : Score Nutriscore normalisé
            'nutriscore_grade': self._normalize_nutriscore(payload.get('nutriscore_grade')),
            'nutriscore_score': self._calculate_nutriscore_value(payload.get('nutriscore_grade')),
            
            # Enrichissement 2 : Extraction des nutriments clés
            'nutrients': self._extract_nutrients(payload.get('nutriments', {})),
            
            # Enrichissement 3 : Détection des allergènes
            'detected_allergens': self._detect_allergens(payload.get('ingredients_text', '')),
            
            # Enrichissement 4 : Score de qualité interne
            'quality_score': self._calculate_quality_score(payload),
            
            # Métadonnées
            'has_image': bool(payload.get('image_url')),
            'image_url': payload.get('image_url', ''),
            'barcode': payload.get('code', '')
        }
        
        return enriched
    
    def _clean_string(self, value: str) -> str:
        """Nettoie une chaîne de caractères"""
        if not value:
            return ''
        return str(value).strip()
    
    def _parse_categories(self, categories_str: str) -> list:
        """Parse et nettoie les catégories"""
        if not categories_str:
            return []
        
        categories = [
            cat.strip() 
            for cat in categories_str.split(',') 
            if cat.strip()
        ]
        return categories[:5]  # Limite à 5 catégories principales
    
    def _parse_list(self, value: str) -> list:
        """Parse une chaîne en liste"""
        if not value:
            return []
        return [item.strip() for item in str(value).split(',') if item.strip()]
    
    def _normalize_nutriscore(self, grade: Optional[str]) -> str:
        """Normalise le Nutriscore en minuscule"""
        if not grade:
            return 'unknown'
        grade = str(grade).lower().strip()
        if grade in ['a', 'b', 'c', 'd', 'e']:
            return grade
        return 'unknown'
    
    def _calculate_nutriscore_value(self, grade: Optional[str]) -> int:
        """Convertit le Nutriscore en valeur numérique (1-5)"""
        normalized = self._normalize_nutriscore(grade)
        return self.NUTRISCORE_VALUES.get(normalized, 0)
    
    def _extract_nutrients(self, nutriments: dict) -> dict:
        """Extrait et normalise les nutriments clés"""
        if not nutriments:
            return {}
        
        nutrients = {}
        
        # Nutriments clés à extraire (pour 100g)
        key_nutrients = [
            ('energy_kcal', 'energy-kcal_100g', 'kcal'),
            ('fat', 'fat_100g', 'g'),
            ('saturated_fat', 'saturated-fat_100g', 'g'),
            ('sugars', 'sugars_100g', 'g'),
            ('salt', 'salt_100g', 'g'),
            ('proteins', 'proteins_100g', 'g'),
            ('fiber', 'fiber_100g', 'g')
        ]
        
        for name, key, unit in key_nutrients:
            value = nutriments.get(key)
            if value is not None:
                try:
                    nutrients[name] = {
                        'value': round(float(value), 2),
                        'unit': unit
                    }
                except (ValueError, TypeError):
                    pass
        
        return nutrients
    
    def _detect_allergens(self, ingredients_text: str) -> list:
        """Détecte les allergènes potentiels dans les ingrédients"""
        if not ingredients_text:
            return []
        
        text_lower = ingredients_text.lower()
        detected = []
        
        for allergen in self.ALLERGENS:
            if allergen in text_lower:
                # Normalise le nom de l'allergène
                normalized = allergen.replace('é', 'e').replace('è', 'e')
                if normalized not in detected:
                    detected.append(normalized)
        
        return detected
    
    def _calculate_quality_score(self, payload: dict) -> int:
        """
        Calcule un score de qualité interne (0-100).
        
        Critères :
        - Nutriscore (40 points max)
        - Complétude des données (30 points max)
        - Faible teneur en sucre/sel (30 points max)
        """
        score = 0
        
        # 1. Score Nutriscore (40 points)
        nutriscore = self._normalize_nutriscore(payload.get('nutriscore_grade'))
        nutriscore_points = {
            'a': 40, 'b': 32, 'c': 24, 'd': 16, 'e': 8, 'unknown': 0
        }
        score += nutriscore_points.get(nutriscore, 0)
        
        # 2. Complétude des données (30 points)
        completeness = 0
        if payload.get('product_name'):
            completeness += 6
        if payload.get('brands'):
            completeness += 6
        if payload.get('categories'):
            completeness += 6
        if payload.get('ingredients_text'):
            completeness += 6
        if payload.get('nutriments'):
            completeness += 6
        score += completeness
        
        # 3. Qualité nutritionnelle (30 points)
        nutriments = payload.get('nutriments', {})
        nutrition_score = 30
        
        # Pénalité pour sucres élevés (>15g/100g)
        sugars = nutriments.get('sugars_100g', 0)
        if sugars and float(sugars) > 15:
            nutrition_score -= 10
        
        # Pénalité pour sel élevé (>1.5g/100g)
        salt = nutriments.get('salt_100g', 0)
        if salt and float(salt) > 1.5:
            nutrition_score -= 10
        
        # Pénalité pour graisses saturées (>5g/100g)
        sat_fat = nutriments.get('saturated-fat_100g', 0)
        if sat_fat and float(sat_fat) > 5:
            nutrition_score -= 10
        
        score += max(0, nutrition_score)
        
        return min(100, max(0, score))
    
    def _save_enriched(self, raw_id: str, data: dict):
        """Sauvegarde un document enrichi avec succès"""
        document = {
            'raw_id': raw_id,
            'status': 'success',
            'enriched_at': datetime.now(timezone.utc).isoformat(),
            'data': data,
            'error': None
        }
        
        self.enriched_collection.update_one(
            {'raw_id': raw_id},
            {'$set': document},
            upsert=True
        )
    
    def _save_failed(self, raw_id: str, error_message: str):
        """Sauvegarde un document en échec"""
        document = {
            'raw_id': raw_id,
            'status': 'failed',
            'enriched_at': datetime.now(timezone.utc).isoformat(),
            'data': None,
            'error': error_message
        }
        
        self.enriched_collection.update_one(
            {'raw_id': raw_id},
            {'$set': document},
            upsert=True
        )
    
    def get_statistics(self) -> dict:
        """Retourne les statistiques d'enrichissement"""
        total = self.enriched_collection.count_documents({})
        success = self.enriched_collection.count_documents({'status': 'success'})
        failed = self.enriched_collection.count_documents({'status': 'failed'})
        
        stats = {
            'total': total,
            'success': success,
            'failed': failed
        }
        
        print(f"\n📊 Statistiques collection ENRICHED :")
        print(f"   Total : {total}")
        print(f"   Succès : {success}")
        print(f"   Échecs : {failed}")
        
        return stats
    
    def close(self):
        """Ferme la connexion"""
        self.db.close()


def main():
    """Point d'entrée pour l'enrichissement"""
    enricher = ProductEnricher()
    try:
        enricher.enrich_all()
        enricher.get_statistics()
    finally:
        enricher.close()


if __name__ == '__main__':
    main()