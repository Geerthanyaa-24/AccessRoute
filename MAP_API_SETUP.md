# AccessRoute Map API setup

AccessRoute supports Mapbox routing when configured and uses OpenStreetMap geocoding with Valhalla pedestrian routing by default.

## 1. Create a Mapbox token
Create a Mapbox public access token in your Mapbox account. Use URL/domain restrictions for the browser token.

## 2. Backend
Copy `.env.example` to `.env` and set:

`MAPBOX_ACCESS_TOKEN=your_token`

The FastAPI endpoint `POST /api/routes/compare` then geocodes the start/destination and requests live walking geometry from Mapbox Directions. Without a Mapbox token, the backend uses OpenStreetMap Nominatim and the public Valhalla pedestrian router; no token is needed for local testing.

## 3. Frontend
Copy `frontend/.env.example` to `frontend/.env` and set:

`VITE_MAPBOX_TOKEN=your_token`

This enables the Mapbox Streets map tiles in Leaflet. If it is blank, the UI automatically falls back to OpenStreetMap tiles.

## 4. Run
Backend:

```bash
cd Navigation
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

Frontend in a second terminal:

```bash
cd Navigation/frontend
npm install
npm run dev
```

## 5. Verify
Open `/docs` on the FastAPI server and call `GET /api/map/config`. It reports `mapbox` when the backend token is loaded and `openstreetmap_valhalla` otherwise.

### Important
Routing providers provide pedestrian geometry, distance and duration. They do **not** guarantee wheelchair accessibility, slope, ramps, tactile paving, or other accessibility attributes. AccessRoute keeps those attributes separate and combines route geometry with the project's accessibility dataset and community reports. Public OSM services may rate-limit requests; set `ACCESSROUTE_CONTACT` to a contact string for deployments.
