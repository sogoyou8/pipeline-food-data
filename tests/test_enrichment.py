import pytest
from unittest.mock import Mock, patch

# Simulation des fonctions d'enrichissement pour les tests
class TestNutriscoreNormalization:
    """Tests pour la normalisation du Nutriscore"""
    
    NUTRISCORE_VALUES = {
        'a': 5, 'b': 4, 'c': 3, 'd': 2, 'e': 1, 'unknown': 0
    }
    
    def normalize_nutriscore(self, grade):
        """Fonction de normalisation à tester"""
        if not grade:
            return 'unknown'
        grade = str(grade).lower().strip()
        if grade in ['a', 'b', 'c', 'd', 'e']:
            return grade
        return 'unknown'
    
    def calculate_nutriscore_value(self, grade):
        """Calcule la valeur numérique du Nutriscore"""
        normalized = self.normalize_nutriscore(grade)
        return self.NUTRISCORE_VALUES.get(normalized, 0)
    
    def test_normalize_valid_grades(self):
        """Test normalisation des grades valides"""
        assert self.normalize_nutriscore('A') == 'a'
        assert self.normalize_nutriscore('b') == 'b'
        assert self.normalize_nutriscore('C') == 'c'
        assert self.normalize_nutriscore('D') == 'd'
        assert self.normalize_nutriscore('e') == 'e'
    
    def test_normalize_invalid_grades(self):
        """Test normalisation des grades invalides"""
        assert self.normalize_nutriscore('F') == 'unknown'
        assert self.normalize_nutriscore('X') == 'unknown'
        assert self.normalize_nutriscore('123') == 'unknown'
    
    def test_normalize_empty_values(self):
        """Test normalisation des valeurs vides"""
        assert self.normalize_nutriscore(None) == 'unknown'
        assert self.normalize_nutriscore('') == 'unknown'
        assert self.normalize_nutriscore('  ') == 'unknown'
    
    def test_nutriscore_value_calculation(self):
        """Test calcul de la valeur numérique"""
        assert self.calculate_nutriscore_value('a') == 5
        assert self.calculate_nutriscore_value('b') == 4
        assert self.calculate_nutriscore_value('c') == 3
        assert self.calculate_nutriscore_value('d') == 2
        assert self.calculate_nutriscore_value('e') == 1
        assert self.calculate_nutriscore_value(None) == 0


class TestAllergenDetection:
    """Tests pour la détection des allergènes"""
    
    ALLERGENS = [
        'gluten', 'wheat', 'milk', 'dairy', 'eggs', 'egg', 'nuts', 'peanuts',
        'soy', 'soja', 'fish', 'shellfish', 'sesame', 'mustard', 'celery',
        'lupin', 'molluscs', 'sulphites', 'lait', 'oeufs', 'noix', 'arachides'
    ]
    
    def detect_allergens(self, ingredients_text):
        """Détecte les allergènes dans le texte"""
        if not ingredients_text:
            return []
        
        text_lower = ingredients_text.lower()
        detected = []
        
        for allergen in self.ALLERGENS:
            if allergen in text_lower:
                normalized = allergen.replace('é', 'e').replace('è', 'e')
                if normalized not in detected:
                    detected.append(normalized)
        
        return detected
    
    def test_detect_single_allergen(self):
        """Test détection d'un seul allergène"""
        text = "Contains wheat flour and water"
        allergens = self.detect_allergens(text)
        assert 'wheat' in allergens
    
    def test_detect_multiple_allergens(self):
        """Test détection de plusieurs allergènes"""
        text = "Ingredients: milk, eggs, wheat flour, soy lecithin"
        allergens = self.detect_allergens(text)
        assert 'milk' in allergens
        assert 'eggs' in allergens
        assert 'wheat' in allergens
        assert 'soy' in allergens
    
    def test_detect_no_allergens(self):
        """Test avec texte sans allergènes"""
        text = "Water, sugar, natural flavors"
        allergens = self.detect_allergens(text)
        assert len(allergens) == 0
    
    def test_detect_empty_text(self):
        """Test avec texte vide"""
        assert self.detect_allergens("") == []
        assert self.detect_allergens(None) == []
    
    def test_detect_french_allergens(self):
        """Test détection des allergènes en français"""
        text = "Contient du lait et des oeufs"
        allergens = self.detect_allergens(text)
        assert 'lait' in allergens
        assert 'oeufs' in allergens


class TestQualityScore:
    """Tests pour le calcul du score de qualité"""
    
    def calculate_quality_score(self, payload):
        """Calcule le score de qualité (0-100)"""
        score = 0
        
        # Nutriscore (40 points max)
        nutriscore = payload.get('nutriscore_grade', '').lower()
        nutriscore_points = {'a': 40, 'b': 32, 'c': 24, 'd': 16, 'e': 8}
        score += nutriscore_points.get(nutriscore, 0)
        
        # Complétude (30 points max)
        if payload.get('product_name'):
            score += 6
        if payload.get('brands'):
            score += 6
        if payload.get('categories'):
            score += 6
        if payload.get('ingredients_text'):
            score += 6
        if payload.get('nutriments'):
            score += 6
        
        # Qualité nutritionnelle (30 points max)
        nutrition_score = 30
        nutriments = payload.get('nutriments', {})
        
        sugars = nutriments.get('sugars_100g', 0)
        if sugars and float(sugars) > 15:
            nutrition_score -= 10
        
        salt = nutriments.get('salt_100g', 0)
        if salt and float(salt) > 1.5:
            nutrition_score -= 10
        
        sat_fat = nutriments.get('saturated-fat_100g', 0)
        if sat_fat and float(sat_fat) > 5:
            nutrition_score -= 10
        
        score += max(0, nutrition_score)
        
        return min(100, max(0, score))
    
    def test_quality_score_perfect_product(self):
        """Test score pour un produit parfait"""
        payload = {
            'nutriscore_grade': 'a',
            'product_name': 'Test Product',
            'brands': 'Test Brand',
            'categories': 'Test Category',
            'ingredients_text': 'water',
            'nutriments': {
                'sugars_100g': 5,
                'salt_100g': 0.5,
                'saturated-fat_100g': 2
            }
        }
        score = self.calculate_quality_score(payload)
        assert score == 100
    
    def test_quality_score_poor_product(self):
        """Test score pour un produit de mauvaise qualité"""
        payload = {
            'nutriscore_grade': 'e',
            'product_name': 'Bad Product',
            'nutriments': {
                'sugars_100g': 30,
                'salt_100g': 3,
                'saturated-fat_100g': 10
            }
        }
        score = self.calculate_quality_score(payload)
        assert score < 50
    
    def test_quality_score_empty_product(self):
        """Test score pour un produit vide"""
        payload = {}
        score = self.calculate_quality_score(payload)
        assert score == 30  # Seulement les 30 points nutritionnels de base
    
    def test_quality_score_range(self):
        """Test que le score reste dans [0, 100]"""
        payloads = [
            {},
            {'nutriscore_grade': 'a'},
            {'nutriscore_grade': 'e', 'nutriments': {'sugars_100g': 100}}
        ]
        
        for payload in payloads:
            score = self.calculate_quality_score(payload)
            assert 0 <= score <= 100


class TestNutrientExtraction:
    """Tests pour l'extraction des nutriments"""
    
    def extract_nutrients(self, nutriments):
        """Extrait les nutriments clés"""
        if not nutriments:
            return {}
        
        nutrients = {}
        key_nutrients = [
            ('energy_kcal', 'energy-kcal_100g', 'kcal'),
            ('fat', 'fat_100g', 'g'),
            ('sugars', 'sugars_100g', 'g'),
            ('salt', 'salt_100g', 'g'),
            ('proteins', 'proteins_100g', 'g')
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
    
    def test_extract_all_nutrients(self):
        """Test extraction de tous les nutriments"""
        nutriments = {
            'energy-kcal_100g': 250,
            'fat_100g': 10.5,
            'sugars_100g': 15.3,
            'salt_100g': 1.2,
            'proteins_100g': 8.0
        }
        
        result = self.extract_nutrients(nutriments)
        
        assert 'energy_kcal' in result
        assert result['energy_kcal']['value'] == 250
        assert result['sugars']['value'] == 15.3
    
    def test_extract_partial_nutrients(self):
        """Test extraction avec nutriments partiels"""
        nutriments = {
            'energy-kcal_100g': 100,
            'sugars_100g': 5
        }
        
        result = self.extract_nutrients(nutriments)
        
        assert 'energy_kcal' in result
        assert 'sugars' in result
        assert 'fat' not in result
    
    def test_extract_empty_nutrients(self):
        """Test extraction avec nutriments vides"""
        assert self.extract_nutrients({}) == {}
        assert self.extract_nutrients(None) == {}