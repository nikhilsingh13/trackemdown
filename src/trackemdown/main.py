"""FastAPI application for the Geotagging Service."""

from fastapi import FastAPI, HTTPException, Query
from .models import GeoTagResponse
from .core import fetch_geotags, NoResultsFoundError, GeocodingServiceError, InvalidCoordinatesError

app = FastAPI(
    title="Geotagging Service",
    description="An API to convert addresses and coordinates to Uber H3 geotags using OSM Nominatim.",
    version="1.0.0",
)

@app.get(
    "/geotag",
    response_model=GeoTagResponse,
    summary="Get H3 geotag for an address or coordinates",
    tags=["Geotagging"],
)
async def get_geotag(
    q: str = Query(..., description="The address string or 'latitude,longitude' pair to look up."),
    resolution: int = Query(12, ge=0, le=15, description="The H3 resolution (0-15). Default is 12.")
):
    """
    This endpoint takes a query string `q` and an H3 `resolution` and returns a list of matching geotags.

    - If `q` is a valid "latitude,longitude" string, it's converted directly.
    - If `q` is an address, it's sent to the OpenStreetMap Nominatim API for geocoding.
    - The resulting coordinates are then converted into H3 cell identifiers (geotags).
    """
    try:
        results = await fetch_geotags(q, resolution)
        return GeoTagResponse(
            query=q,
            resolution=resolution,
            result=results,
        )
    except InvalidCoordinatesError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NoResultsFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except GeocodingServiceError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint for health check."""
    return {"status": "ok", "message": "Geotagging Service is running."}
