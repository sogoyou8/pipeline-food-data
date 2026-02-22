from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import text

from src.config.database import PostgresDatabase

app = FastAPI(
    title="Food Data API",
    description="API pour l'analyse des produits alimentaires",
    version="1.0.0"
)

# CORS pour le dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connexion base de données (lazy)
_db = None

def get_db():
    global _db
    if _db is None:
        _db = PostgresDatabase().connect()
    return _db


# ============================================
# Modèles Pydantic
# ============================================

class NutrientResponse(BaseModel):
    name: str
    value: float
    unit: str


class ProductResponse(BaseModel):
    id: int
    barcode: Optional[str]
    product_name: str
    brand_name: Optional[str]
    nutriscore_grade: Optional[str]
    nutriscore_score: Optional[int]
    quality_score: Optional[int]
    has_image: bool
    image_url: Optional[str]
    categories: List[str]
    allergens: List[str]
    nutrient_count: int = 0
    allergen_count: int = 0
    category_count: int = 0


class ProductDetailResponse(ProductResponse):
    nutrients: List[NutrientResponse]
    created_at: datetime
    completeness: Optional[int] = None
    countries: Optional[str] = None


class PaginatedResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class StatsResponse(BaseModel):
    total_products: int
    total_brands: int
    total_categories: int
    nutriscore_distribution: dict
    avg_quality_score: float
    top_brands: List[dict]
    top_categories: List[dict]


# ============================================
# Endpoints
# ============================================

@app.get("/")
def root():
    """Endpoint racine"""
    return {"message": "Food Data API", "version": "1.0.0"}


@app.get("/products", response_model=PaginatedResponse)
def get_products(
    page: int = Query(1, ge=1, description="Numéro de page"),
    page_size: int = Query(20, ge=1, le=100, description="Taille de page"),
    nutriscore: Optional[str] = Query(None, description="Filtrer par Nutriscore (a,b,c,d,e)"),
    brand: Optional[str] = Query(None, description="Filtrer par marque"),
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    min_quality: Optional[int] = Query(None, ge=0, le=100, description="Score qualité minimum"),
    search: Optional[str] = Query(None, description="Recherche par nom")
):
    """Liste paginée des produits avec filtres."""
    db = get_db()
    session = db.get_session()
    
    try:
        base_query = """
            SELECT DISTINCT p.id, p.barcode, p.product_name, b.name as brand_name,
                   p.nutriscore_grade, p.nutriscore_score, p.quality_score,
                   p.has_image, p.image_url
            FROM products p
            LEFT JOIN brands b ON p.brand_id = b.id
            LEFT JOIN product_categories pc ON p.id = pc.product_id
            LEFT JOIN categories c ON pc.category_id = c.id
            WHERE 1=1
        """
        
        count_query = """
            SELECT COUNT(DISTINCT p.id)
            FROM products p
            LEFT JOIN brands b ON p.brand_id = b.id
            LEFT JOIN product_categories pc ON p.id = pc.product_id
            LEFT JOIN categories c ON pc.category_id = c.id
            WHERE 1=1
        """
        
        params = {}
        conditions = ""
        
        if nutriscore:
            conditions += " AND p.nutriscore_grade = :nutriscore"
            params['nutriscore'] = nutriscore.lower()
        
        if brand:
            conditions += " AND LOWER(b.name) LIKE LOWER(:brand)"
            params['brand'] = f"%{brand}%"
        
        if category:
            conditions += " AND LOWER(c.name) LIKE LOWER(:category)"
            params['category'] = f"%{category}%"
        
        if min_quality is not None:
            conditions += " AND p.quality_score >= :min_quality"
            params['min_quality'] = min_quality
        
        if search:
            conditions += " AND LOWER(p.product_name) LIKE LOWER(:search)"
            params['search'] = f"%{search}%"
        
        # Compte total
        total_result = session.execute(text(count_query + conditions), params)
        total = total_result.fetchone()[0]
        
        # Pagination
        offset = (page - 1) * page_size
        params['limit'] = page_size
        params['offset'] = offset
        
        final_query = base_query + conditions + " ORDER BY p.quality_score DESC, p.id LIMIT :limit OFFSET :offset"
        result = session.execute(text(final_query), params)
        
        items = []
        for row in result:
            product_id = row[0]
            
            # Catégories
            cat_result = session.execute(
                text("SELECT c.name FROM categories c JOIN product_categories pc ON c.id = pc.category_id WHERE pc.product_id = :pid"),
                {'pid': product_id}
            )
            categories = [r[0] for r in cat_result]
            
            # Allergènes
            allerg_result = session.execute(
                text("SELECT allergen_name FROM product_allergens WHERE product_id = :pid"),
                {'pid': product_id}
            )
            allergens = [r[0] for r in allerg_result]
            
            # Comptes nutriments
            nut_count_result = session.execute(
                text("SELECT COUNT(*) FROM product_nutrients WHERE product_id = :pid"),
                {'pid': product_id}
            )
            nutrient_count = nut_count_result.fetchone()[0]
            
            items.append(ProductResponse(
                id=product_id,
                barcode=row[1],
                product_name=row[2],
                brand_name=row[3],
                nutriscore_grade=row[4],
                nutriscore_score=row[5],
                quality_score=row[6],
                has_image=row[7],
                image_url=row[8],
                categories=categories,
                allergens=allergens,
                nutrient_count=nutrient_count,
                allergen_count=len(allergens),
                category_count=len(categories)
            ))
        
        total_pages = (total + page_size - 1) // page_size
        
        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    finally:
        session.close()


@app.get("/products/{product_id}", response_model=ProductDetailResponse)
def get_product(product_id: int):
    """Détail d'un produit par son ID."""
    db = get_db()
    session = db.get_session()
    
    try:
        result = session.execute(
            text("""
            SELECT p.id, p.barcode, p.product_name, b.name, 
                   p.nutriscore_grade, p.nutriscore_score, p.quality_score,
                   p.has_image, p.image_url, p.created_at
            FROM products p
            LEFT JOIN brands b ON p.brand_id = b.id
            WHERE p.id = :pid
            """),
            {'pid': product_id}
        )
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
        
        # Catégories
        cat_result = session.execute(
            text("""SELECT c.name FROM categories c 
               JOIN product_categories pc ON c.id = pc.category_id 
               WHERE pc.product_id = :pid"""),
            {'pid': product_id}
        )
        categories = [r[0] for r in cat_result]
        
        # Allergènes
        allerg_result = session.execute(
            text("SELECT allergen_name FROM product_allergens WHERE product_id = :pid"),
            {'pid': product_id}
        )
        allergens = [r[0] for r in allerg_result]
        
        # Nutriments
        nutr_result = session.execute(
            text("SELECT nutrient_name, value, unit FROM product_nutrients WHERE product_id = :pid"),
            {'pid': product_id}
        )
        nutrients = [
            NutrientResponse(name=r[0], value=float(r[1]) if r[1] else 0, unit=r[2] or '')
            for r in nutr_result
        ]
        
        # Calcul complétude
        completeness = 0
        if row[2]: completeness += 20  # nom
        if row[3]: completeness += 20  # marque
        if categories: completeness += 20  # catégories
        if nutrients: completeness += 20  # nutriments
        if row[4]: completeness += 20  # nutriscore
        
        return ProductDetailResponse(
            id=row[0],
            barcode=row[1],
            product_name=row[2],
            brand_name=row[3],
            nutriscore_grade=row[4],
            nutriscore_score=row[5],
            quality_score=row[6],
            has_image=row[7],
            image_url=row[8],
            categories=categories,
            allergens=allergens,
            nutrients=nutrients,
            created_at=row[9],
            nutrient_count=len(nutrients),
            allergen_count=len(allergens),
            category_count=len(categories),
            completeness=completeness
        )
        
    finally:
        session.close()


@app.get("/stats", response_model=StatsResponse)
def get_stats():
    """Statistiques globales sur les produits."""
    db = get_db()
    session = db.get_session()
    
    try:
        total_products = session.execute(text("SELECT COUNT(*) FROM products")).fetchone()[0]
        total_brands = session.execute(text("SELECT COUNT(*) FROM brands")).fetchone()[0]
        total_categories = session.execute(text("SELECT COUNT(*) FROM categories")).fetchone()[0]
        
        nutri_result = session.execute(
            text("""
            SELECT nutriscore_grade, COUNT(*) 
            FROM products 
            WHERE nutriscore_grade IS NOT NULL
            GROUP BY nutriscore_grade
            ORDER BY nutriscore_grade
            """)
        )
        nutriscore_distribution = {row[0]: row[1] for row in nutri_result}
        
        avg_quality = session.execute(
            text("SELECT COALESCE(AVG(quality_score), 0) FROM products")
        ).fetchone()[0]
        
        top_brands_result = session.execute(
            text("""
            SELECT b.name, COUNT(p.id) as cnt
            FROM brands b
            JOIN products p ON p.brand_id = b.id
            GROUP BY b.name
            ORDER BY cnt DESC
            LIMIT 10
            """)
        )
        top_brands = [{"name": row[0], "count": row[1]} for row in top_brands_result]
        
        top_categories_result = session.execute(
            text("""
            SELECT c.name, COUNT(pc.product_id) as cnt
            FROM categories c
            JOIN product_categories pc ON c.id = pc.category_id
            GROUP BY c.name
            ORDER BY cnt DESC
            LIMIT 10
            """)
        )
        top_categories = [{"name": row[0], "count": row[1]} for row in top_categories_result]
        
        return StatsResponse(
            total_products=total_products,
            total_brands=total_brands,
            total_categories=total_categories,
            nutriscore_distribution=nutriscore_distribution,
            avg_quality_score=float(avg_quality),
            top_brands=top_brands,
            top_categories=top_categories
        )
        
    finally:
        session.close()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)