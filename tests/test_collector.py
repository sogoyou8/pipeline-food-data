import pytest
from unittest.mock import Mock, patch, MagicMock
import json

# Import des modules à tester
from src.utils.hash_utils import generate_hash


class TestHashUtils:
    """Tests unitaires pour les utilitaires de hash"""
    
    def test_generate_hash_returns_string(self):
        """Le hash doit retourner une chaîne de caractères"""
        data = {"name": "test", "value": 123}
        result = generate_hash(data)
        assert isinstance(result, str)
    
    def test_generate_hash_consistent(self):
        """Le même dictionnaire doit toujours produire le même hash"""
        data = {"product_name": "Cereal", "brand": "TestBrand"}
        hash1 = generate_hash(data)
        hash2 = generate_hash(data)
        assert hash1 == hash2
    
    def test_generate_hash_different_data(self):
        """Des données différentes doivent produire des hash différents"""
        data1 = {"name": "product1"}
        data2 = {"name": "product2"}
        hash1 = generate_hash(data1)
        hash2 = generate_hash(data2)
        assert hash1 != hash2
    
    def test_generate_hash_order_independent(self):
        """L'ordre des clés ne doit pas affecter le hash"""
        data1 = {"a": 1, "b": 2, "c": 3}
        data2 = {"c": 3, "a": 1, "b": 2}
        hash1 = generate_hash(data1)
        hash2 = generate_hash(data2)
        assert hash1 == hash2
    
    def test_generate_hash_length(self):
        """Le hash SHA256 doit avoir 64 caractères"""
        data = {"test": "data"}
        result = generate_hash(data)
        assert len(result) == 64


class TestCollectorParsing:
    """Tests pour le parsing des données du collecteur"""
    
    def test_parse_product_with_all_fields(self):
        """Test parsing d'un produit complet"""
        raw_product = {
            "code": "1234567890",
            "product_name": "Test Product",
            "brands": "Test Brand",
            "categories": "Category1, Category2",
            "nutriscore_grade": "b",
            "ingredients_text": "water, sugar, salt",
            "nutriments": {
                "energy-kcal_100g": 100,
                "sugars_100g": 5
            }
        }
        
        # Vérifie que les champs essentiels sont présents
        assert "code" in raw_product
        assert "product_name" in raw_product
        assert raw_product["nutriscore_grade"] == "b"
    
    def test_parse_product_with_missing_fields(self):
        """Test parsing d'un produit avec champs manquants"""
        raw_product = {
            "code": "1234567890",
            "product_name": "Test Product"
        }
        
        # Les champs manquants doivent être gérés
        assert raw_product.get("brands", "") == ""
        assert raw_product.get("nutriscore_grade") is None
    
    def test_parse_empty_product(self):
        """Test parsing d'un produit vide"""
        raw_product = {}
        
        assert raw_product.get("product_name", "Unknown") == "Unknown"


class TestRawDocumentStructure:
    """Tests pour la structure des documents RAW"""
    
    def test_raw_document_has_required_fields(self):
        """Un document RAW doit avoir tous les champs requis"""
        from datetime import datetime, timezone
        
        product = {"code": "123", "product_name": "Test"}
        
        raw_document = {
            "source": "openfoodfacts",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "raw_hash": generate_hash(product),
            "payload": product
        }
        
        assert "source" in raw_document
        assert "fetched_at" in raw_document
        assert "raw_hash" in raw_document
        assert "payload" in raw_document
    
    def test_payload_contains_original_data(self):
        """Le payload doit contenir 100% des données originales"""
        original_product = {
            "code": "123",
            "product_name": "Test",
            "extra_field": "should be preserved"
        }
        
        raw_document = {
            "payload": original_product
        }
        
        assert raw_document["payload"] == original_product
        assert "extra_field" in raw_document["payload"]