
# <Project Name> Real-Time AIS Vessel Tracking & Maritime Analytics

A full-stack GIS platform for live AIS ingestion, vessel tracking, spatial analytics, and interactive dashboards.

## 1) Purpose

- What it does: track vessels in real time, aggregate traffic, and visualize UK/Liverpool port activity.
- What it provides: A modular, low-level platform for:
    - Live vessel positions and trajectories
    - Accurate port and sub-area visit tracking
    - UK and Liverpool analytics
    - Scalable APIs for dashboarding and reporting


## 2) Architecture Overview

- **Frontend**: React (Create React App) + Mapbox (interactive map, dashboards, neon and liquid glass UI)
- **Backend**: FastAPI (REST), Python
- **Database**: MongoDB (Atlas/local) with geospatial indexes
- **Data Pipeline**: AIS WebSocket ingestion → normalization → upserts (latest) + historical writes + processed writes


## 3) Quick Start

### Prerequisites
- Node.js 
- Python + venv
- MongoDB URI (Atlas or local)
- Mapbox access token
- (Optional) Docker & Docker Compose

### Environment Variables

Create `.env` files:

**Backend (`/src/.env`):**
```
MONGODB_URI=<...>
MONGODB_DB=<...>
AIS_API_KEY=<...>
OPENAI_API_KEY=<...> #optional
```

**Frontend (`/frontend/.env`):**
```
REACT_APP_MAPBOX_TOKEN=<...>
AWS_ACCESS_KEY_ID=<...> #optional
AWS_SECRET_ACCESS_KEY_ID=<...> #optional
````

### Run locally

**App startup bash script**
```bash
cd vehicle-gis-platform
./start.sh
````

Alternatively, you can run the backend or frontend separately:

**Backend**
```bash
cd vehicle-gis-platform
python -m venv venv
source venv/bin/activate    # (Windows) venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --reload --host ${API_HOST:-0.0.0.0} --port ${API_PORT:-8000}
````

**Frontend**

```bash
cd frontend
npm install
npm start
```

Open: [http://localhost:3000](http://localhost:3000)

### With Docker (optional)

```bash
docker compose up --build
```
## 4) Data Collection
### Scheduled Tasks (Run Once a Day)
The following aggregators should be run daily to process and aggregate vessel traffic data:

1. **Port Traffic Aggregator**:
   - **File**: `src/database/aggregate_port_traffic.py`
   - **Purpose**: Aggregates vessel traffic statistics per port into 6-hour or daily buckets.
   - **Command**:
     ```bash
     python src/database/aggregate_port_traffic.py
     ```

2. **Area Traffic Aggregator**:
   - **File**: `src/database/aggregate_area_traffic.py`
   - **Purpose**: Aggregates vessel traffic statistics per dock/terminal into 6-hour or daily buckets.
   - **Command**:
     ```bash
     python src/database/aggregate_area_traffic.py
     ```

---

### Live Tasks (Run Continuously)
The following scripts should be run continuously to process live AIS data and detect vessel visits:

1. **AIS Stream Runner**:
   - **File**: `ais_stream_runner.py`
   - **Purpose**: Collects live AIS data via WebSocket and periodically cleans up stale vessel positions.
   - **Command**:
     ```bash
     python ais_stream_runner.py
     ```

2. **Visit Processor Runner**:
   - **File**: `visit_processor_runner.py`
   - **Purpose**: Processes vessel visits and port calls in real-time.
   - **Command**:
     ```bash
     python visit_processor_runner.py
     ```

---

### **Summary**
- **Daily Tasks**: Aggregate port and area traffic data for reporting and analytics.
- **Live Tasks**: Continuously collect AIS data and process vessel visits in real-time.



## 5) Project Structure

```
/frontend
  ├─ src/
  │  ├─ components/
  │  │  ├─ map/ (VesselMap, markers, popups)
  │  │  ├─ charts/ (bar charts, chart themes, neon styles)
  │  │  ├─ dashboarding_components/ (UK Dashboard, Liverpool Dashboard, Dashboard Container etd)
  │  │  └─ shared/ (TimeRangePicker, loaders, popups, map, panels etc.)
  │  ├─ api/axiosClient.js
  │  └─ assets/
  │  └─ index.js, App.js, index.css
  ├─ public/ (vessel_images/, flags/, favicon)
  └─ package.json

/src
  ├─ api/
  │  ├─ main.py (FastAPI app)
  │  └─ endpoints/
  │     ├─ vessels.py            # /api/vessels (latest positions GeoJSON)
  │     ├─ vessel_history.py     # /api/vessel_history/{mmsi}
  │     ├─ dashboard.py          # /api/dashboard (UK + Liverpool stats)
  │     ├─ ports.py              # /api/ports (FeatureCollection)
  │     ├─ ai_insights.py        # /ai-insights/summary, /ai-insights/top-ports
  │     └─ <liverpool_endpoints>.py  # /api/liverpool/*
  ├─ database/
  │    ├─ mongo_connection.py
  │    ├─ indices.py               # 2dsphere indexes setup
  │    ├─ aggregate_*.py
  │    └─ data_insertion_scripts/  # Scripts for inserting data into collections
  ├─ modules/
  │    ├─ ais_main_data_collector.py
  ├─ ais_collector.py         # AIS data collection logic
  │    ├─ ais_collector.py         # AIS data collection logic
  │    ├─ ais_collector.py         # AIS data collection logic
  │    └─ visit_processor.py       # Visit detection and processing
  ├─ processors/
  │  ├─ visit_state_updater.py
  │  └─ visit_state_updater_liverpool_areas.py
  ├─ models/                     # Pydantic schemas (if used)
  ├─ utils/                      # helpers (MMSI→flag, geo utils, etc.)
  └─ scripts/
     ├─ run_aggregations.sh
     └─ start.sh
```

## 6) Database & Collections

* `latest_positions`: Holds the most recent AIS position report for each vessel, identified by MMSI.  
    - **Data Source**: Real-time AIS via WebSocket from [aisstream.io](https://aisstream.io/)  
    - **Update Frequency**: Real-time - every 30 seconds (updated per new PositionReport message per vessel)  

* `vessel_position`: Stores historical AIS position reports for all vessels, with full message content and timestamps.  
    - **Data Source**: Real-time AIS via WebSocket from [aisstream.io](https://aisstream.io/)  
    - **Update Frequency**: Every 30 minutes - snapshot of `latest_positions`  

* `vessel_details`: Static metadata for vessels that is unlikely to change after a journey starts (e.g., name, type, dimensions, IMO, callsign, destination).  
    - **Data Source**: Static AIS messages via WebSocket from [aisstream.io](https://aisstream.io/)  
    - **Update Frequency**: Updated on new ShipStaticData messages or when new MMSI appears  

* `ports`: Geospatial dataset of UK ports with location coordinates and LOCODEs.  
    - **Data Source**: [VesselFinder](https://www.vesselfinder.com/ports?country=gb) and UN/LOCODE database  
    - **Update Frequency**: One-time import, manually updated when new port data is available  

* `port_areas`: GeoJSON polygons defining dock, terminal, and facility boundaries within major UK ports (e.g., Liverpool Dock Estate, Garston, Birkenhead).  
    - **Data Source**: Custom-created using [geojson.io](https://geojson.io/) and clustering AIS data (DBSCAN + convex hull)  
    - **Update Frequency**: Manually updated as new boundaries are digitized  

* `port_calls`: Records vessel arrivals and departures at ports (entry→exit events). Derived from AIS visit detection pipeline.  
    - **Data Source**: Derived from `vessel_position` and `ports` collections  
    - **Update Frequency**: Real-time via `visit_state_updater` pipeline  

* `visit_state`: Ephemeral state store tracking whether a vessel is currently in a port, used to debounce entry/exit detection.  
    - **Data Source**: Derived from `vessel_position` with point-in-polygon checks against `ports`  
    - **Update Frequency**: Updated continuously in real-time  

* `visit_state_areas`: Ephemeral state store tracking whether a vessel is currently inside a dock/terminal polygon (sub-port level).  
    - **Data Source**: Derived from `vessel_position` with point-in-polygon checks against `port_areas`  
    - **Update Frequency**: Updated continuously in real-time  

* `area_calls`: Records vessel arrivals and departures for dock/terminal areas (entry→exit events).  
    - **Data Source**: Derived from `vessel_position` and `port_areas` collections  
    - **Update Frequency**: Real-time via `visit_state_areas` pipeline  

* `area_traffic`: Aggregated vessel traffic statistics per dock/terminal, binned into 6-hour or daily buckets.  
    - **Data Source**: Aggregated from `area_calls` collection  
    - **Update Frequency**: Every 6 hours  

* `port_traffic`: Aggregated vessel traffic statistics per port, binned into 6-hour or daily buckets.  
    - **Data Source**: Aggregated from `port_calls` collection  
    - **Update Frequency**: Every 6 hours  


> Indexes: 2dsphere on `coordinates`/`location` fields; time indexes on `timestamp_utc`
> See `src/database/indices.py`

## 7) Key API Endpoints

### Core

* `GET /api/vessels` — Latest vessel positions as GeoJSON
* `GET /api/ports` — All ports as GeoJSON FeatureCollection
* `GET /api/vessel_history/{mmsi}` — Historical AIS points
* `GET /api/dashboard` — UK + Liverpool summary stats
* `GET /api/liverpool/*` — Liverpool-specific freight/traffic metrics
* `GET /api/port_areas` — Dock/terminal polygons
* `GET /api/area-traffic` — Sub-area traffic stats
* `GET /api/vessel-popup` — Vessel popup details (port calls)
* `GET /api/traffic-insights` — Traffic insights

### AI Insights

* `GET /ai-insights/summary` — AI-generated summary of traffic (UK or port scope)
* `GET /ai-insights/top-ports` — AI-generated analysis of top ports (with Liverpool context)

> Interactive docs: `http://localhost:8000/docs` (FastAPI Swagger UI)

## 8) Frontend Features

* Interactive Mapbox map (style toggle, 3D sky/terrain, vessel/port layers)
* Popups: ports, port areas, vessel details (name/type/flag/image), trajectory simulator, date filters
* Dashboards: UK overview and Liverpool deep-dive (bar/line/stacked charts, neon glass theme)
* City filters, map controls, refresh, map layers
* Side panel lists for vessels/ports with “Show on map”
* LLM insight cards (peak traffic, busiest ports explanations)

## 9) Web Interface Screenshots

>Screenshot 1 : Zoomed in view of Liverpool port with an example vessel popup open
![alt text](image-3.png)


>Screenshots 2 & 3: UK Dashboard
![alt text](image-4.png)
![alt text](image-5.png)

>Screenshot 4 & 5: Liverpool Dashboard:
![alt text](image-6.png)
![alt text](image-7.png)

>Screenshot 6: List of ports with interactive location links
![alt text](image-8.png)

>Screenshot 7: List of vessels with live location links
![alt text](image-9.png)


## 10) Data Pipeline

* WebSocket AIS ingestion (aisstream or provider) → normalize → upsert to `latest_positions` + write to `vessel_position`
* Visit detection:
  * Ports: point-in-polygon + debounce
  * Liverpool sub-areas: polygon visits → `area_calls`, aggregated to `area_traffic`
* Port traffic aggregation (scheduled)

## 11) Windows terminal troubleshooting
* Windows bash path issues → ensure `npm` on PATH (`setx PATH "%PATH%;C:\Program Files\nodejs"`), `venv\Scripts\activate`.

