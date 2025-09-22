"""Core logic for fetching geotags from addresses or coordinates."""

import re
from typing import List
import httpx
import h3
from .models import GeoTagResult

# Regex for validating "latitude,longitude" input
COORD_REGEX = re.compile(r"^-?([1-8]?[0-9]|[1-9]0)\.{1}\d{1,15}\s*,\s*-?([1]?[0-7]?[0-9]|[1]?[1-8]?[0])\.{1}\d{1,15}$")

class GeotaggingError(Exception):
    """Base exception for geotagging errors."""
    pass

class InvalidCoordinatesError(GeotaggingError):
    """Raised when coordinate input is invalid."""
    pass

class GeocodingServiceError(GeotaggingError):
    """Raised when the external geocoding service fails."""
    pass

class NoResultsFoundError(GeotaggingError):
    """Raised when no results are found for a query."""
    pass


async def fetch_geotags(q: str, resolution: int) -> List[GeoTagResult]:
    """
    Fetches geotag information for a given query string (address or lat,lng).

    Args:
        q: The address string or 'latitude,longitude' pair.
        resolution: The H3 resolution (0-15).

    Returns:
        A list of GeoTagResult objects.

    Raises:
        InvalidCoordinatesError: If the input coordinates are malformed.
        GeocodingServiceError: If there's an issue connecting to the geocoding service.
        NoResultsFoundError: If the geocoding service returns no results.
    """
    locations = []

    if COORD_REGEX.match(q.replace(" ", "")):
        try:
            lat_str, lon_str = q.split(',')
            lat, lon = float(lat_str), float(lon_str)
            locations.append({
                "lat": lat,
                "lon": lon,
                "display_name": f"Coordinates: {lat:.6f}, {lon:.6f}"
            })
        except (ValueError, IndexError):
            raise InvalidCoordinatesError("Invalid coordinate format. Use 'latitude,longitude'.")
    else:
        headers = {'User-Agent': 'TrackEmDown/1.0 (nikhilsingh.io)'}
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={q}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, timeout=10.0)
                response.raise_for_status()
                locations = response.json()
            except httpx.RequestError as exc:
                raise GeocodingServiceError(f"Error connecting to geocoding service: {exc}")

    if not locations:
        raise NoResultsFoundError("No results found for the given query.")

    results = []
    for loc in locations:
        try:
            lat, lon = float(loc['lat']), float(loc['lon'])
            geotag = h3.latlng_to_cell(lat, lon, resolution)
            results.append(
                GeoTagResult(
                    address=loc.get('display_name', 'N/A'),
                    latitude=lat,
                    longitude=lon,
                    geotag=geotag
                )
            )
        except (ValueError, KeyError) as e:
            # Skip malformed results from the external API
            print(f"Skipping a location due to parsing error: {e}")
            continue
    
    if not results:
        raise NoResultsFoundError("Geocoding service returned malformed data.")

    return results
