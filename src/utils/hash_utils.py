import hashlib
import json


def generate_hash(data: dict) -> str:
    """
    Génère un hash SHA256 unique pour un dictionnaire.
    Utilisé pour éviter les doublons dans la collection RAW.
    
    Args:
        data: Dictionnaire à hasher
        
    Returns:
        Hash SHA256 sous forme de chaîne hexadécimale
    """
    json_string = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(json_string.encode('utf-8')).hexdigest()