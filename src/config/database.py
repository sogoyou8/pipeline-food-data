import os
from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()


class MongoDatabase:
    """Gestionnaire de connexion MongoDB"""
    
    def __init__(self):
        self.uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.db_name = os.getenv('MONGODB_DB_NAME', 'food_data')
        self.client = None
        self.db = None
    
    def connect(self):
        """Établit la connexion à MongoDB"""
        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]
        return self
    
    def get_raw_collection(self):
        """Retourne la collection RAW"""
        return self.db['raw_products']
    
    def get_enriched_collection(self):
        """Retourne la collection ENRICHED"""
        return self.db['enriched_products']
    
    def close(self):
        """Ferme la connexion"""
        if self.client:
            self.client.close()


class PostgresDatabase:
    """Gestionnaire de connexion PostgreSQL"""
    
    def __init__(self):
        self.host = os.getenv('POSTGRES_HOST', 'localhost')
        self.port = os.getenv('POSTGRES_PORT', '5432')
        self.db = os.getenv('POSTGRES_DB', 'food_data')
        self.user = os.getenv('POSTGRES_USER', 'postgres')
        self.password = os.getenv('POSTGRES_PASSWORD', 'postgres')
        self.engine = None
        self.Session = None
    
    def connect(self):
        """Établit la connexion à PostgreSQL"""
        url = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"
        self.engine = create_engine(url)
        self.Session = sessionmaker(bind=self.engine)
        return self
    
    def get_session(self):
        """Retourne une nouvelle session"""
        return self.Session()
    
    def get_engine(self):
        """Retourne l'engine SQLAlchemy"""
        return self.engine
    
    def close(self):
        """Ferme la connexion"""
        if self.engine:
            self.engine.dispose()