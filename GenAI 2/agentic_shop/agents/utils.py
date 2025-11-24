from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import re

@dataclass
class Review:
    rating: Optional[float] = None
    text: Optional[str] = None
    source: str = "unknown"

@dataclass
class Product:
    id: str
    title: str
    price: float
    currency: str
    retailer: str
    url: str
    image_url: Optional[str] = None
    rating: Optional[float] = None
    reviews: List[Review] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)

def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()
