---
title: Trackemdown
emoji: 🐢
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 5.46.1
app_file: app.py
pinned: false
license: apache-2.0
short_description: A simple learning project to explore H3 geospatial indexing.
---

Type any address and get:
- Exact coordinates (latitude, longitude)
- H3 geotag (hierarchical hexagonal identifier)
- Interactive map with hexagon boundaries

#### How it works

1. Address → Coordinates: Uses `OpenStreetMap Nominatim` to find locations
2. Coordinates → H3 Geotag: Converts to Uber's H3 hexagonal grid system
3. Visualisation: Shows results on an interactive map

#### Examples

Try typing:
- San Francisco - City names
- 37.7749,-122.4194 - Direct coordinates
- Eiffel Tower - Landmarks
- Main Street - Generic addresses (shows multiple matches)

#### What's H3?

H3 divides Earth into hexagonal cells at different resolutions:
- Low resolution (0-5): Continental/country level
- Medium resolution (6-10): City/neighborhood level
- High resolution (11-15): Building/room level

#### Tech Stack

- Backend: FastAPI + H3 library
- Geocoding: OpenStreetMap Nominatim (free service)
- Frontend: Gradio interface
- Maps: Plotly with hexagon boundary visualization
