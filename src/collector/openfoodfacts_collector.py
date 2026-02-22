import requests
import time
from datetime import datetime, timezone
from typing import Optional

from src.config.database import MongoDatabase
from src.utils.hash_utils import generate_hash


class OpenFoodFactsCollector:
    """
    Collecteur de données depuis l'API OpenFoodFacts.
    Stocke les données brutes dans MongoDB sans aucune transformation.
    """
    
    BASE_URL = "https://world.openfoodfacts.org/cgi/search.pl"
    
    def __init__(self):
        self.db = MongoDatabase().connect()
        self.raw_collection = self.db.get_raw_collection()
        # Création d'un index unique sur raw_hash pour éviter les doublons
        self.raw_collection.create_index("raw_hash", unique=True)
    
    def fetch_products(self, total_needed: int = 300, page_size: int = 100) -> int:
        """
        Collecte des produits depuis OpenFoodFacts.
        
        Args:
            total_needed: Nombre total de produits à collecter
            page_size: Nombre de produits par page API
            
        Returns:
            Nombre de produits effectivement collectés
        """
        collected = 0
        page = 1
        duplicates = 0
        errors = 0
        
        print(f"🚀 Démarrage de la collecte de {total_needed} produits...")
        print(f"📦 Taille de page : {page_size}")
        print("-" * 50)
        
        while collected < total_needed:
            try:
                products = self._fetch_page(page, page_size)
                
                if not products:
                    print(f"⚠️ Page {page} vide, arrêt de la collecte")
                    break
                
                for product in products:
                    if collected >= total_needed:
                        break
                    
                    result = self._save_raw_product(product)
                    if result == "saved":
                        collected += 1
                    elif result == "duplicate":
                        duplicates += 1
                    
                    # Affichage progression
                    if collected % 50 == 0 and collected > 0:
                        print(f"✅ Progression : {collected}/{total_needed} produits")
                
                page += 1
                time.sleep(0.5)  # Rate limiting respectueux
                
            except requests.exceptions.Timeout:
                print(f"⏱️ Timeout page {page}, nouvelle tentative...")
                errors += 1
                time.sleep(2)
                if errors > 5:
                    print("❌ Trop d'erreurs, arrêt")
                    break
                continue
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Erreur réseau : {e}")
                errors += 1
                if errors > 5:
                    break
                time.sleep(2)
                continue
        
        print("-" * 50)
        print(f"🎉 Collecte terminée !")
        print(f"   ✅ Produits collectés : {collected}")
        print(f"   🔄 Doublons ignorés : {duplicates}")
        print(f"   ❌ Erreurs : {errors}")
        
        return collected
    
    def _fetch_page(self, page: int, page_size: int) -> list:
        """
        Récupère une page de produits depuis l'API.
        
        Args:
            page: Numéro de page
            page_size: Taille de la page
            
        Returns:
            Liste des produits
        """
        params = {
            'action': 'process',
            'json': 1,
            'page_size': page_size,
            'page': page,
            'fields': 'code,product_name,brands,categories,nutriscore_grade,ingredients_text,nutriments,image_url,countries,stores'
        }
        
        print(f"📡 Récupération page {page}...")
        
        response = requests.get(
            self.BASE_URL,
            params=params,
            timeout=15,
            headers={'User-Agent': 'FoodDataProject/1.0'}
        )
        response.raise_for_status()
        
        data = response.json()
        return data.get('products', [])
    
    def _save_raw_product(self, product: dict) -> str:
        """
        Sauvegarde un produit brut dans MongoDB.
        
        Args:
            product: Données brutes du produit
            
        Returns:
            "saved", "duplicate" ou "error"
        """
        raw_hash = generate_hash(product)
        
        document = {
            'source': 'openfoodfacts',
            'fetched_at': datetime.now(timezone.utc).isoformat(),
            'raw_hash': raw_hash,
            'payload': product
        }
        
        try:
            self.raw_collection.insert_one(document)
            return "saved"
        except Exception as e:
            if "duplicate" in str(e).lower():
                return "duplicate"
            print(f"❌ Erreur insertion : {e}")
            return "error"
    
    def get_statistics(self) -> dict:
        """Retourne les statistiques de la collection RAW"""
        total = self.raw_collection.count_documents({})
        
        stats = {
            'total_documents': total,
            'source': 'openfoodfacts'
        }
        
        print(f"\n📊 Statistiques collection RAW :")
        print(f"   Total documents : {total}")
        
        return stats
    
    def close(self):
        """Ferme la connexion à la base de données"""
        self.db.close()


def main():
    """Point d'entrée principal pour la collecte"""
    collector = OpenFoodFactsCollector()
    try:
        collector.fetch_products(total_needed=300, page_size=100)
        collector.get_statistics()
    finally:
        collector.close()


if __name__ == '__main__':
    main()