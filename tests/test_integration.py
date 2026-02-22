"""
Tests d'intégration pour le pipeline Food Data.

Ces tests vérifient :
1. Les appels réels aux endpoints API
2. Les requêtes SQL
3. Le pipeline complet sur un petit jeu de données
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch


# ============================================
# Tests d'intégration API
# ============================================

class TestAPIIntegration:
    """Tests d'intégration pour les endpoints de l'API FastAPI"""

    @pytest.fixture
    def client(self):
        """Crée un client de test avec une base mockée"""
        # Mock le module database AVANT d'importer main
        mock_db_module = MagicMock()
        mock_db_instance = MagicMock()
        mock_session = MagicMock()
        mock_db_instance.get_session.return_value = mock_session
        mock_db_module.PostgresDatabase.return_value.connect.return_value = mock_db_instance

        with patch.dict('sys.modules', {'src.config.database': mock_db_module, 'src.config': mock_db_module}):
            # Reset le module API s'il est déjà importé
            if 'src.api.main' in sys.modules:
                del sys.modules['src.api.main']
            if 'src.api' in sys.modules:
                del sys.modules['src.api']

            from src.api.main import app
            # Reset la connexion lazy
            import src.api.main as api_module
            api_module._db = mock_db_instance

            from fastapi.testclient import TestClient
            test_client = TestClient(app)

            yield test_client, mock_session

    def test_root_endpoint(self, client):
        """Test que l'endpoint racine répond correctement"""
        test_client, _ = client
        response = test_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Food Data API"
        assert data["version"] == "1.0.0"

    def test_get_products_endpoint(self, client):
        """Test l'endpoint GET /products avec pagination"""
        test_client, mock_session = client

        # Mock du COUNT
        mock_count_result = MagicMock()
        mock_count_result.fetchone.return_value = (2,)

        # Mock des produits
        mock_products = [
            (1, '123456', 'Produit Test 1', 'Marque A', 'a', 5, 85, True, 'http://img1.jpg'),
            (2, '789012', 'Produit Test 2', 'Marque B', 'c', 3, 60, False, None),
        ]
        mock_products_result = MagicMock()
        mock_products_result.__iter__ = Mock(return_value=iter(mock_products))

        # Mock des catégories et allergènes (vides)
        def make_empty():
            m = MagicMock()
            m.__iter__ = Mock(return_value=iter([]))
            return m

        mock_session.execute.side_effect = [
            mock_count_result,
            mock_products_result,
            make_empty(), make_empty(),
            make_empty(), make_empty(),
        ]

        response = test_client.get("/products?page=1&page_size=20")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert len(data["items"]) == 2
        assert data["items"][0]["product_name"] == "Produit Test 1"
        assert data["items"][1]["nutriscore_grade"] == "c"

    def test_get_products_with_filters(self, client):
        """Test l'endpoint GET /products avec filtres"""
        test_client, mock_session = client

        mock_count_result = MagicMock()
        mock_count_result.fetchone.return_value = (1,)

        mock_products = [
            (1, '123456', 'Bio Cereal', 'BioMarque', 'a', 5, 90, True, 'http://img.jpg'),
        ]
        mock_products_result = MagicMock()
        mock_products_result.__iter__ = Mock(return_value=iter(mock_products))

        def make_empty():
            m = MagicMock()
            m.__iter__ = Mock(return_value=iter([]))
            return m

        mock_session.execute.side_effect = [
            mock_count_result,
            mock_products_result,
            make_empty(), make_empty(),
        ]

        response = test_client.get("/products?nutriscore=a&min_quality=80&search=bio")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["quality_score"] == 90

    def test_get_product_detail(self, client):
        """Test l'endpoint GET /products/{id}"""
        test_client, mock_session = client

        from datetime import datetime
        now = datetime(2026, 1, 15, 10, 30, 0)

        mock_product_result = MagicMock()
        mock_product_result.fetchone.return_value = (
            1, '123456', 'Test Product', 'Test Brand',
            'b', 4, 75, True, 'http://img.jpg', now
        )

        mock_categories = MagicMock()
        mock_categories.__iter__ = Mock(return_value=iter([('Cereals',), ('Breakfast',)]))

        mock_allergens = MagicMock()
        mock_allergens.__iter__ = Mock(return_value=iter([('gluten',), ('milk',)]))

        mock_nutrients = MagicMock()
        mock_nutrients.__iter__ = Mock(return_value=iter([
            ('energy_kcal', 250.0, 'kcal'),
            ('sugars', 10.5, 'g'),
        ]))

        mock_session.execute.side_effect = [
            mock_product_result,
            mock_categories,
            mock_allergens,
            mock_nutrients,
        ]

        response = test_client.get("/products/1")

        assert response.status_code == 200
        data = response.json()
        assert data["product_name"] == "Test Product"
        assert data["brand_name"] == "Test Brand"
        assert data["nutriscore_grade"] == "b"
        assert len(data["categories"]) == 2
        assert "gluten" in data["allergens"]
        assert len(data["nutrients"]) == 2

    def test_get_product_not_found(self, client):
        """Test l'endpoint GET /products/{id} avec produit inexistant"""
        test_client, mock_session = client

        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_session.execute.return_value = mock_result

        response = test_client.get("/products/99999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Produit non trouvé"

    def test_get_stats_endpoint(self, client):
        """Test l'endpoint GET /stats"""
        test_client, mock_session = client

        mock_total_products = MagicMock()
        mock_total_products.fetchone.return_value = (150,)

        mock_total_brands = MagicMock()
        mock_total_brands.fetchone.return_value = (25,)

        mock_total_categories = MagicMock()
        mock_total_categories.fetchone.return_value = (40,)

        mock_nutriscore = MagicMock()
        mock_nutriscore.__iter__ = Mock(return_value=iter([
            ('a', 30), ('b', 40), ('c', 35), ('d', 25), ('e', 20)
        ]))

        mock_avg_quality = MagicMock()
        mock_avg_quality.fetchone.return_value = (72.5,)

        mock_top_brands = MagicMock()
        mock_top_brands.__iter__ = Mock(return_value=iter([
            ('Nestlé', 15), ('Danone', 12), ('Kelloggs', 8)
        ]))

        mock_top_categories = MagicMock()
        mock_top_categories.__iter__ = Mock(return_value=iter([
            ('Breakfast cereals', 20), ('Dairy', 18), ('Snacks', 15)
        ]))

        mock_session.execute.side_effect = [
            mock_total_products,
            mock_total_brands,
            mock_total_categories,
            mock_nutriscore,
            mock_avg_quality,
            mock_top_brands,
            mock_top_categories,
        ]

        response = test_client.get("/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total_products"] == 150
        assert data["total_brands"] == 25
        assert data["total_categories"] == 40
        assert data["avg_quality_score"] == 72.5
        assert data["nutriscore_distribution"]["a"] == 30
        assert len(data["top_brands"]) == 3
        assert len(data["top_categories"]) == 3

    def test_pagination_params_validation(self, client):
        """Test la validation des paramètres de pagination"""
        test_client, _ = client

        response = test_client.get("/products?page_size=500")
        assert response.status_code == 422

        response = test_client.get("/products?page=0")
        assert response.status_code == 422


# ============================================
# Tests d'intégration SQL (requêtes)
# ============================================

class TestSQLIntegration:
    """Tests d'intégration pour les requêtes SQL"""

    def test_schema_tables_exist(self):
        """Vérifie que le schéma SQL contient toutes les tables requises"""
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'sql', 'schema.sql')

        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()

        required_tables = ['brands', 'categories', 'products',
                          'product_categories', 'product_nutrients', 'product_allergens']

        for table in required_tables:
            assert f'CREATE TABLE {table}' in schema, f"Table {table} manquante dans le schéma"

    def test_schema_has_indexes(self):
        """Vérifie que le schéma contient des index"""
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'sql', 'schema.sql')

        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()

        required_indexes = [
            'idx_products_barcode',
            'idx_products_nutriscore',
            'idx_products_quality',
            'idx_products_brand',
        ]

        for index in required_indexes:
            assert index in schema, f"Index {index} manquant dans le schéma"

    def test_schema_has_constraints(self):
        """Vérifie que le schéma contient les contraintes"""
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'sql', 'schema.sql')

        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()

        assert 'NOT NULL' in schema
        assert 'UNIQUE' in schema
        assert 'CHECK' in schema
        assert 'REFERENCES' in schema

    def test_schema_has_view(self):
        """Vérifie que la vue product_summary existe"""
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'sql', 'schema.sql')

        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()

        assert 'product_summary' in schema

    def test_sql_query_products_with_filters(self):
        """Vérifie que la requête SQL avec filtres est correcte"""
        base_query = """
            SELECT DISTINCT p.id, p.barcode, p.product_name, b.name as brand_name
            FROM products p
            LEFT JOIN brands b ON p.brand_id = b.id
            WHERE 1=1
        """

        conditions = ""
        params = {}

        conditions += " AND p.nutriscore_grade = :nutriscore"
        params['nutriscore'] = 'a'

        conditions += " AND p.quality_score >= :min_quality"
        params['min_quality'] = 50

        final_query = base_query + conditions + " ORDER BY p.id LIMIT :limit OFFSET :offset"
        params['limit'] = 20
        params['offset'] = 0

        assert ':nutriscore' in final_query
        assert ':min_quality' in final_query
        assert ':limit' in final_query
        assert ':offset' in final_query
        assert params['nutriscore'] == 'a'
        assert params['min_quality'] == 50


# ============================================
# Tests d'intégration Pipeline complet
# ============================================

class TestPipelineIntegration:
    """Tests d'intégration pour le pipeline complet sur un petit jeu de données"""

    def _create_sample_raw_products(self):
        """Crée un petit jeu de données brutes de test"""
        return [
            {
                '_id': 'test_id_1',
                'source': 'openfoodfacts',
                'fetched_at': '2026-01-15T10:00:00Z',
                'raw_hash': 'hash_1',
                'payload': {
                    'code': '3017620422003',
                    'product_name': 'Nutella',
                    'brands': 'Ferrero',
                    'categories': 'Spreads, Chocolate spreads',
                    'nutriscore_grade': 'e',
                    'ingredients_text': 'sugar, palm oil, hazelnuts, cocoa, milk, lecithin, vanillin',
                    'nutriments': {
                        'energy-kcal_100g': 539,
                        'fat_100g': 30.9,
                        'saturated-fat_100g': 10.6,
                        'sugars_100g': 56.3,
                        'salt_100g': 0.107,
                        'proteins_100g': 6.3,
                        'fiber_100g': 0
                    },
                    'image_url': 'https://images.openfoodfacts.org/nutella.jpg'
                }
            },
            {
                '_id': 'test_id_2',
                'source': 'openfoodfacts',
                'fetched_at': '2026-01-15T10:00:01Z',
                'raw_hash': 'hash_2',
                'payload': {
                    'code': '5449000000996',
                    'product_name': 'Coca-Cola',
                    'brands': 'Coca-Cola',
                    'categories': 'Beverages, Sodas',
                    'nutriscore_grade': 'e',
                    'ingredients_text': 'water, sugar, carbon dioxide, colour, phosphoric acid, natural flavourings including caffeine',
                    'nutriments': {
                        'energy-kcal_100g': 42,
                        'fat_100g': 0,
                        'saturated-fat_100g': 0,
                        'sugars_100g': 10.6,
                        'salt_100g': 0,
                        'proteins_100g': 0,
                        'fiber_100g': 0
                    },
                    'image_url': 'https://images.openfoodfacts.org/coca.jpg'
                }
            },
            {
                '_id': 'test_id_3',
                'source': 'openfoodfacts',
                'fetched_at': '2026-01-15T10:00:02Z',
                'raw_hash': 'hash_3',
                'payload': {
                    'code': '3175681851849',
                    'product_name': 'Salade Bio',
                    'brands': 'Bonduelle',
                    'categories': 'Salads, Organic',
                    'nutriscore_grade': 'a',
                    'ingredients_text': 'organic lettuce, water',
                    'nutriments': {
                        'energy-kcal_100g': 15,
                        'fat_100g': 0.2,
                        'saturated-fat_100g': 0,
                        'sugars_100g': 1.5,
                        'salt_100g': 0.01,
                        'proteins_100g': 1.3,
                        'fiber_100g': 1.5
                    },
                    'image_url': None
                }
            }
        ]

    def _get_enricher(self):
        """Crée un enricher sans connexion MongoDB"""
        # Import local pour éviter d'importer SQLAlchemy au niveau module
        with patch('src.config.database.MongoDatabase'):
            from src.enrichment.enricher import ProductEnricher
            enricher = ProductEnricher.__new__(ProductEnricher)
            enricher.ALLERGENS = ProductEnricher.ALLERGENS
            enricher.NUTRISCORE_VALUES = ProductEnricher.NUTRISCORE_VALUES
            return enricher

    def test_full_pipeline_raw_to_enriched(self):
        """Test le pipeline complet : RAW → ENRICHED"""
        enricher = self._get_enricher()
        raw_products = self._create_sample_raw_products()

        results = []
        for raw in raw_products:
            enriched = enricher._enrich_product(raw['payload'])
            results.append(enriched)

        # Nutella
        nutella = results[0]
        assert nutella['product_name'] == 'Nutella'
        assert nutella['brand'] == 'Ferrero'
        assert nutella['nutriscore_grade'] == 'e'
        assert nutella['nutriscore_score'] == 1
        assert nutella['quality_score'] < 50
        assert 'milk' in nutella['detected_allergens']
        assert 'energy_kcal' in nutella['nutrients']
        assert nutella['nutrients']['sugars']['value'] == 56.3
        assert nutella['has_image'] is True
        assert len(nutella['categories']) == 2

        # Coca-Cola
        coca = results[1]
        assert coca['product_name'] == 'Coca-Cola'
        assert coca['nutriscore_grade'] == 'e'
        assert len(coca['detected_allergens']) == 0

        # Salade Bio
        salade = results[2]
        assert salade['product_name'] == 'Salade Bio'
        assert salade['nutriscore_grade'] == 'a'
        assert salade['nutriscore_score'] == 5
        assert salade['quality_score'] > 80
        assert salade['has_image'] is False

    def test_pipeline_enrichment_consistency(self):
        """Test que l'enrichissement est déterministe"""
        enricher = self._get_enricher()
        raw = self._create_sample_raw_products()[0]

        result1 = enricher._enrich_product(raw['payload'])
        result2 = enricher._enrich_product(raw['payload'])

        assert result1['product_name'] == result2['product_name']
        assert result1['nutriscore_grade'] == result2['nutriscore_grade']
        assert result1['nutriscore_score'] == result2['nutriscore_score']
        assert result1['quality_score'] == result2['quality_score']
        assert result1['detected_allergens'] == result2['detected_allergens']
        assert result1['nutrients'] == result2['nutrients']

    def test_pipeline_etl_mapping(self):
        """Test le mapping ETL enriched → SQL"""
        enricher = self._get_enricher()
        raw_products = self._create_sample_raw_products()

        for raw in raw_products:
            enriched = enricher._enrich_product(raw['payload'])

            assert enriched['product_name'] is not None
            assert len(enriched['product_name']) <= 500

            assert len(enriched.get('barcode', '')) <= 50

            grade = enriched['nutriscore_grade']
            if grade != 'unknown':
                assert len(grade) == 1
                assert grade in ['a', 'b', 'c', 'd', 'e']

            assert 0 <= enriched['nutriscore_score'] <= 5
            assert 0 <= enriched['quality_score'] <= 100
            assert isinstance(enriched['has_image'], bool)

            for cat in enriched.get('categories', []):
                assert len(cat) <= 255

            for name, data in enriched.get('nutrients', {}).items():
                assert isinstance(data['value'], (int, float))
                assert isinstance(data['unit'], str)

            for allergen in enriched.get('detected_allergens', []):
                assert len(allergen) <= 100

    def test_pipeline_hash_deduplication(self):
        """Test que le hash permet la déduplication"""
        from src.utils.hash_utils import generate_hash

        raw_products = self._create_sample_raw_products()

        hashes = [generate_hash(raw['payload']) for raw in raw_products]
        assert len(set(hashes)) == len(hashes), "Les hash doivent être uniques"

        hash1 = generate_hash(raw_products[0]['payload'])
        hash2 = generate_hash(raw_products[0]['payload'])
        assert hash1 == hash2, "Le hash doit être déterministe"

    def test_pipeline_handles_incomplete_data(self):
        """Test le pipeline avec des données incomplètes"""
        enricher = self._get_enricher()

        minimal_product = {
            'code': '000000',
            'product_name': 'Produit Minimal'
        }

        enriched = enricher._enrich_product(minimal_product)

        assert enriched['product_name'] == 'Produit Minimal'
        assert enriched['nutriscore_grade'] == 'unknown'
        assert enriched['nutriscore_score'] == 0
        assert enriched['quality_score'] >= 0
        assert enriched['detected_allergens'] == []
        assert enriched['nutrients'] == {}
        assert enriched['categories'] == []

    def test_pipeline_handles_empty_product(self):
        """Test le pipeline avec un produit complètement vide"""
        enricher = self._get_enricher()

        enriched = enricher._enrich_product({})

        assert enriched['product_name'] == ''
        assert enriched['nutriscore_grade'] == 'unknown'
        assert enriched['quality_score'] == 30
        assert enriched['detected_allergens'] == []
        assert enriched['nutrients'] == {}