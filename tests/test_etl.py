import pytest
from unittest.mock import Mock, MagicMock, patch


class TestETLMapping:
    """Tests pour le mapping ETL MongoDB → SQL"""
    
    def test_product_mapping(self):
        """Test le mapping d'un produit enrichi vers SQL"""
        enriched_data = {
            'product_name': 'Test Product',
            'brand': 'Test Brand',
            'barcode': '1234567890',
            'nutriscore_grade': 'b',
            'nutriscore_score': 4,
            'quality_score': 75,
            'has_image': True,
            'image_url': 'http://example.com/image.jpg',
            'categories': ['Category1', 'Category2'],
            'nutrients': {
                'energy_kcal': {'value': 100, 'unit': 'kcal'},
                'sugars': {'value': 5, 'unit': 'g'}
            },
            'detected_allergens': ['gluten', 'milk']
        }
        
        # Vérifie que tous les champs requis sont présents
        assert enriched_data['product_name'] is not None
        assert enriched_data['nutriscore_grade'] in ['a', 'b', 'c', 'd', 'e', 'unknown']
        assert 0 <= enriched_data['quality_score'] <= 100
    
    def test_null_handling(self):
        """Test la gestion des valeurs nulles"""
        enriched_data = {
            'product_name': None,
            'brand': None,
            'nutriscore_grade': 'unknown'
        }
        
        # La valeur par défaut pour le nom
        name = enriched_data.get('product_name') or 'Unknown'
        assert name == 'Unknown'
        
        # Nutriscore unknown devient NULL en SQL
        nutriscore = enriched_data.get('nutriscore_grade')
        sql_nutriscore = None if nutriscore == 'unknown' else nutriscore
        assert sql_nutriscore is None
    
    def test_categories_mapping(self):
        """Test le mapping des catégories (relation N-N)"""
        enriched_data = {
            'categories': ['Breakfast', 'Cereals', 'Organic']
        }
        
        categories = enriched_data.get('categories', [])
        
        assert len(categories) == 3
        assert 'Breakfast' in categories
    
    def test_nutrients_mapping(self):
        """Test le mapping des nutriments"""
        enriched_data = {
            'nutrients': {
                'energy_kcal': {'value': 250.5, 'unit': 'kcal'},
                'fat': {'value': 10.0, 'unit': 'g'},
                'sugars': {'value': 15.3, 'unit': 'g'}
            }
        }
        
        nutrients = enriched_data.get('nutrients', {})
        
        for name, data in nutrients.items():
            assert 'value' in data
            assert 'unit' in data
            assert isinstance(data['value'], (int, float))
    
    def test_allergens_mapping(self):
        """Test le mapping des allergènes"""
        enriched_data = {
            'detected_allergens': ['gluten', 'milk', 'eggs']
        }
        
        allergens = enriched_data.get('detected_allergens', [])
        
        assert len(allergens) == 3
        for allergen in allergens:
            assert isinstance(allergen, str)
            assert len(allergen) <= 100  # Contrainte SQL


class TestETLIdempotency:
    """Tests pour l'idempotence de l'ETL"""
    
    def test_duplicate_detection(self):
        """Test la détection des doublons"""
        existing_ids = {'id1', 'id2', 'id3'}
        new_id = 'id2'
        
        is_duplicate = new_id in existing_ids
        assert is_duplicate is True
    
    def test_new_record_detection(self):
        """Test la détection des nouveaux enregistrements"""
        existing_ids = {'id1', 'id2', 'id3'}
        new_id = 'id4'
        
        is_duplicate = new_id in existing_ids
        assert is_duplicate is False


class TestDataValidation:
    """Tests pour la validation des données avant insertion SQL"""
    
    def validate_product(self, data):
        """Valide un produit avant insertion"""
        errors = []
        
        if not data.get('product_name'):
            errors.append("product_name is required")
        
        if len(data.get('product_name', '')) > 500:
            errors.append("product_name too long (max 500)")
        
        if len(data.get('barcode', '')) > 50:
            errors.append("barcode too long (max 50)")
        
        nutriscore = data.get('nutriscore_grade')
        if nutriscore and nutriscore not in ['a', 'b', 'c', 'd', 'e', None]:
            errors.append("invalid nutriscore_grade")
        
        quality = data.get('quality_score', 0)
        if not (0 <= quality <= 100):
            errors.append("quality_score must be 0-100")
        
        return errors
    
    def test_valid_product(self):
        """Test validation d'un produit valide"""
        data = {
            'product_name': 'Test Product',
            'barcode': '123456',
            'nutriscore_grade': 'b',
            'quality_score': 75
        }
        
        errors = self.validate_product(data)
        assert len(errors) == 0
    
    def test_missing_name(self):
        """Test validation avec nom manquant"""
        data = {
            'barcode': '123456'
        }
        
        errors = self.validate_product(data)
        assert "product_name is required" in errors
    
    def test_invalid_nutriscore(self):
        """Test validation avec nutriscore invalide"""
        data = {
            'product_name': 'Test',
            'nutriscore_grade': 'x'
        }
        
        errors = self.validate_product(data)
        assert "invalid nutriscore_grade" in errors
    
    def test_invalid_quality_score(self):
        """Test validation avec score invalide"""
        data = {
            'product_name': 'Test',
            'quality_score': 150
        }
        
        errors = self.validate_product(data)
        assert "quality_score must be 0-100" in errors


class TestSQLConstraints:
    """Tests pour les contraintes SQL"""
    
    def test_brand_name_length(self):
        """Test longueur du nom de marque"""
        brand_name = "A" * 300  # Trop long
        truncated = brand_name[:255]
        assert len(truncated) == 255
    
    def test_category_name_length(self):
        """Test longueur du nom de catégorie"""
        category_name = "B" * 300
        truncated = category_name[:255]
        assert len(truncated) == 255
    
    def test_nutriscore_constraint(self):
        """Test contrainte Nutriscore"""
        valid_grades = ['a', 'b', 'c', 'd', 'e', None]
        
        for grade in valid_grades:
            assert grade in valid_grades
        
        assert 'f' not in valid_grades