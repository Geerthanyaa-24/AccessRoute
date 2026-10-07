# AccessRoute implementation notes

## What was added

- Refreshed React dashboard with responsive map-first layout.
- Accessibility preference controls.
- Route candidate comparison cards.
- Personalized demonstration scoring fields.
- Pareto status display.
- Data-confidence summary.
- Interactive route selection on the Leaflet map.
- Obstacle report form with pending-verification status.
- Grounded chatbot endpoint with deterministic fallback and optional OpenAI API integration.
- Chatbot UI connected to the selected route context.
- Accessibility-focused focus styles and non-color labels.

## Important limitations

- The current route candidates are explicitly demonstration candidates because the extracted project does not include populated routing GeoJSON files and the prior compare endpoint used hardcoded coordinates.
- Configure a real routing provider or populate the graph before using this for real-world navigation.
- The OpenAI integration is optional. Set `OPENAI_API_KEY` in a local `.env` file; never commit secrets.
- The current obstacle report is stored in process memory. Connect it to the existing SQLAlchemy/PostGIS models for persistence.

## Run

### Backend

From the project root:

```bash
uvicorn backend.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_URL` if the backend is hosted somewhere other than `http://localhost:8000`.

## Dynamic obstacle-aware rerouting (latest)
- `POST /api/routes/reroute` refreshes route alternatives and re-ranks them using active community obstacle reports.
- Live Mapbox geometry is fetched when `MAPBOX_ACCESS_TOKEN` is configured.
- Reports are matched to route corridors using a geographic distance threshold; they are treated as observations, not guaranteed closures.
- Maintainers can verify/reject reports through role-protected endpoints.
- Frontend Find Route now includes a "Reroute around reported obstacles" action and shows affected-report status.
- Maintainers get a dedicated console at `/maintainer` for report review.
