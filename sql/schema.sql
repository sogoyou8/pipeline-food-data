-- Schéma SQL pour les produits alimentaires
-- Base de données : PostgreSQL

-- Suppression des tables si elles existent (pour reset)
DROP TABLE IF EXISTS product_allergens CASCADE;
DROP TABLE IF EXISTS product_nutrients CASCADE;
DROP TABLE IF EXISTS product_categories CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS brands CASCADE;

-- ============================================
-- TABLE : brands (Marques)
-- ============================================
CREATE TABLE brands (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_brands_name ON brands(name);

-- ============================================
-- TABLE : categories (Catégories)
-- ============================================
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_categories_name ON categories(name);

-- ============================================
-- TABLE : products (Produits)
-- ============================================
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    mongo_raw_id VARCHAR(50) UNIQUE NOT NULL,
    barcode VARCHAR(50),
    product_name VARCHAR(500) NOT NULL,
    brand_id INTEGER REFERENCES brands(id),
    
    -- Nutriscore
    nutriscore_grade CHAR(1) CHECK (nutriscore_grade IN ('a', 'b', 'c', 'd', 'e') OR nutriscore_grade IS NULL),
    nutriscore_score INTEGER CHECK (nutriscore_score >= 0 AND nutriscore_score <= 5),
    
    -- Score qualité
    quality_score INTEGER CHECK (quality_score >= 0 AND quality_score <= 100),
    
    -- Image
    has_image BOOLEAN DEFAULT FALSE,
    image_url TEXT,
    
    -- Métadonnées
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_barcode ON products(barcode);
CREATE INDEX idx_products_nutriscore ON products(nutriscore_grade);
CREATE INDEX idx_products_quality ON products(quality_score);
CREATE INDEX idx_products_brand ON products(brand_id);
CREATE INDEX idx_products_name ON products(product_name);

-- ============================================
-- TABLE : product_categories (Relation N-N)
-- ============================================
CREATE TABLE product_categories (
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (product_id, category_id)
);

CREATE INDEX idx_pc_product ON product_categories(product_id);
CREATE INDEX idx_pc_category ON product_categories(category_id);

-- ============================================
-- TABLE : product_nutrients (Nutriments)
-- ============================================
CREATE TABLE product_nutrients (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    nutrient_name VARCHAR(50) NOT NULL,
    value DECIMAL(10, 2),
    unit VARCHAR(10),
    UNIQUE(product_id, nutrient_name)
);

CREATE INDEX idx_nutrients_product ON product_nutrients(product_id);
CREATE INDEX idx_nutrients_name ON product_nutrients(nutrient_name);

-- ============================================
-- TABLE : product_allergens (Allergènes)
-- ============================================
CREATE TABLE product_allergens (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    allergen_name VARCHAR(100) NOT NULL,
    UNIQUE(product_id, allergen_name)
);

CREATE INDEX idx_allergens_product ON product_allergens(product_id);
CREATE INDEX idx_allergens_name ON product_allergens(allergen_name);

-- ============================================
-- VUE : product_summary (Vue pour l'API)
-- ============================================
CREATE OR REPLACE VIEW product_summary AS
SELECT 
    p.id,
    p.barcode,
    p.product_name,
    b.name AS brand_name,
    p.nutriscore_grade,
    p.nutriscore_score,
    p.quality_score,
    p.has_image,
    p.image_url,
    p.created_at,
    ARRAY_AGG(DISTINCT c.name) FILTER (WHERE c.name IS NOT NULL) AS categories,
    ARRAY_AGG(DISTINCT pa.allergen_name) FILTER (WHERE pa.allergen_name IS NOT NULL) AS allergens
FROM products p
LEFT JOIN brands b ON p.brand_id = b.id
LEFT JOIN product_categories pc ON p.id = pc.product_id
LEFT JOIN categories c ON pc.category_id = c.id
LEFT JOIN product_allergens pa ON p.id = pa.product_id
GROUP BY p.id, b.name;