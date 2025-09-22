""" Data models ffor the geotagging service"""

from typing import List
from pydantic import BaseModel

class GeoTagResult(BaseModel):
   """Defines the structure for a single geotag result."""
   address: str
   latitude: float
   longitude: float
   geotag: str

class GeoTagResponse(BaseModel):
   """Defines the structure for a successful API response."""
   status: str = "success"
   query: str
   resolution: int
   result: List[GeoTagResult]
