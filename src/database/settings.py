# src/database/settings.py
import os

# Debounce thresholds
HITS_IN  = int(os.getenv("PORT_VISIT_HITS_IN", 3))   # consecutive "inside" hits to confirm entry
HITS_OUT = int(os.getenv("PORT_VISIT_HITS_OUT", 3))  # consecutive "outside" hits to confirm exit

# Heuristics
SLOW_SOG_KNOTS = float(os.getenv("SLOW_SOG_KNOTS", 0.5))      # sog < this is "slow"
NAV_STATUS_IN_PORT = int(os.getenv("NAV_STATUS_IN_PORT", 5))  # 5: moored

# Collections
COLL_LATEST_POSITIONS = os.getenv("COLL_LATEST_POSITIONS", "latest_positions")
COLL_VESSEL_POSITION  = os.getenv("COLL_VESSEL_POSITION", "vessel_position")
COLL_PORT_AREAS       = os.getenv("COLL_PORT_AREAS", "port_areas")
COLL_VISIT_STATE      = os.getenv("COLL_VISIT_STATE", "port_visit_state")
COLL_PORT_CALLS       = os.getenv("COLL_PORT_CALLS", "port_calls")
COLL_PORT_TRAFFIC     = os.getenv("COLL_PORT_TRAFFIC", "port_traffic")

# Scan limits
SCAN_LIMIT = int(os.getenv("STATE_UPDATE_SCAN_LIMIT", 5000))

# Live updater: only scan this many recent minutes from latest_positions
LIVE_RECENT_MINUTES = int(os.getenv("LIVE_RECENT_MINUTES", 15))

# Historical backfill batch size (how many docs to stream per find() batch)
HISTORY_BATCH_SIZE = int(os.getenv("HISTORY_BATCH_SIZE", 20000))
