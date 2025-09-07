

import VesselListPanel from './VesselListPanel';
import PortListPanel from './PortListPanel';
import React, { useState } from 'react';
import VesselMap from './VesselMap';
import DashboardPanel from './DashboardPanel';
import ViewTogglePopup from './ViewTogglePopup';
import FilterControlsPopup from './FilterControlsPopup';
import LayersChecklistPopup from './LayersChecklistPopup';
import DashboardControlsPopup from './DashboardControlsPopup';
import './AppLayout.css';
import './VesselSidePanel.css'
import logo from '../assets/logo.png';
import {
  EyeIcon,
  RefreshCwIcon,
  LayersIcon,
  FilterIcon,
  BarChart2Icon,
  ShipIcon,
  AnchorIcon
} from 'lucide-react';
import MaritimeDashboardOverlay from './dashboarding_components/MaritimeDashboardOverlay';


// Map layer options
const LAYER_OPTIONS = [
  { key: 'port-areas', label: 'Port-area polygons' },
];




// Dashboard control sections (not yet individually wired)
const DASH_SECTIONS = [
  {
    key: 'national',
    label: 'National Overview: UK-Wide Maritime Stats',
    items: [
      { key:'vessel_dist',    label:'Vessel type distribution' },
      { key:'top10_dests',    label:'Top 10 destinations' },
      { key:'speed_analysis', label:'Vessel Speed Analysis' },
    ]
  },
  {
    key: 'liverpool',
    label: 'Liverpool Port Activity (Last 3 days)',
    items: [
      { key:'daily_arrivals', label:'Daily Vessel arrivals' },
      { key:'liv_dist',       label:'Vessel type distribution' },
      { key:'liv_top10',      label:'Top 10 destinations' },
      { key:'liv_speed',      label:'Vessel Speed Analysis' },
      { key:'liv_insights',   label:'Insights' },
    ]
  },
  {
    key: 'dock',
    label: 'Dock Level Analytics',
    items: [
      { key:'traffic_per_dock', label:'Vessel traffic per dock/terminal' },
      { key:'types_by_dock',    label:'Ship types by dock' },
      { key:'area_vs_traffic',  label:'Dock area vs traffic' },
      { key:'avg_dwell',        label:'Average dwell time' },
      { key:'dock_insights',    label:'Insights' },
    ]
  },
  {
    key: 'alerts',
    label: 'Anomalies and Alerts',
    items: [
      { key:'timeline',     label:'Timeline' },
      { key:'status_chart', label:'Status chart' },
      { key:'alerts',       label:'Alerts' },
    ]
  }
];

const NAVIGATION_DAY = 'mapbox://styles/mapbox/navigation-day-v1';
const SATELLITE     = 'mapbox://styles/mapbox/satellite-streets-v12';

/**
 * SidebarMenu renders the vertical icon bar.
 */
const SidebarMenu = ({ onView, onReload, onLayers, onFilter, onDashboard, onVessels, onPorts }) => {
  const items = [
    { Icon: EyeIcon,       label: 'Views',     onClick: onView },
    { Icon: RefreshCwIcon, label: 'Reload',    onClick: onReload },
    { Icon: LayersIcon,    label: 'Layers',    onClick: onLayers },
    { Icon: FilterIcon,    label: 'Filter',    onClick: onFilter },
    { Icon: BarChart2Icon, label: 'Dashboard', onClick: onDashboard },
    { Icon: ShipIcon,      label: 'Vessels',   onClick: onVessels },
    { Icon: AnchorIcon,    label: 'Ports',      onClick: onPorts }
  ];
  return (
    <div className="sidebar-menu">
      {items.map(({ Icon, label, onClick }) => (
        <button
          key={label}
          className="sidebar-btn"
          title={label}
          onClick={onClick}
        >
          <Icon size={22} />
        </button>
      ))}
    </div>
  );
};

/**
 * AppLayout is the top-level layout: header, sidebar icons, map,
 * and right‐side panels for vessel, filter, layers, and dashboard.
 */
export default function AppLayout() {
  // Map style toggle
  const [mapStyle, setMapStyle] = useState(SATELLITE);
  const toggleStyle = () =>
    setMapStyle(s => (s === NAVIGATION_DAY ? SATELLITE : NAVIGATION_DAY));

  // Popups open state
  const [viewOpen, setViewOpen]           = useState(false);
  const [layersOpen, setLayersOpen]       = useState(false);
  const [filterOpen, setFilterOpen]       = useState(false);
  const [dashboardOpen, setDashboardOpen] = useState(false);
  const [showDashboard, setShowDashboard] = useState(false);//////////new dashboard
  // Data control states
  const [selectedLayers, setSelectedLayers] = useState(
    LAYER_OPTIONS.map(o => o.key)
  );
  const [filterCities, setFilterCities] = useState([]);

  // Dashboard “view all” only
  const [viewAllDash, setViewAllDash] = useState(false);

  const [showVesselList, setShowVesselList] = useState(false);
  const [showPortList, setShowPortList] = useState(false);
  return (
    <div className="layout-container">
      {/* Top Navigation */}
      <header className="top-nav">
        <div className="nav-left">
          <img src={logo} alt="Logo" className="logo" />
          <span className="title">AIS Vessel Tracking and Maritime Analytics</span>
        </div>
        <div className="nav-center" />
        <div className="nav-right">
          <input
            type="text"
            placeholder="🔍 Ship / Port"
            className="search-bar"
          />
        </div>
      </header>

      {/* Body: Sidebar icons + Map */}
      <div className="main-body">
        {/* Left sidebar: only icons */}
        <aside className="left-panel glass-rail">
          <SidebarMenu
            onView={()       => setViewOpen(v => !v)}
            onReload={()     => window.location.reload()}
            onLayers={()     => setLayersOpen(l => !l)}
            onFilter={()     => setFilterOpen(f => !f)}
            // onDashboard={()  => setDashboardOpen(d => !d)}
            onDashboard={()  => setShowDashboard(true)}
            onVessels={()    => setShowVesselList(v => !v)}
            onPorts={()      => setShowPortList(p => !p)}

          />
        </aside>

        {/* Map Container + Popups */}
        <main className="map-container">
          <VesselMap
            mapStyle={mapStyle}
            filterCities={filterCities}
            selectedLayers={selectedLayers}
          />

          {/* View Toggle */}
          {viewOpen && (
            <ViewTogglePopup
              currentStyle={mapStyle}
              toggleStyle={toggleStyle}
              onClose={() => setViewOpen(false)}
            />
          )}

          {/* Layers Checklist */}
          {layersOpen && (
            <LayersChecklistPopup
              availableLayers={LAYER_OPTIONS}
              selected={selectedLayers}
              onClose={() => setLayersOpen(false)}
              onApply={keys => {
                setSelectedLayers(keys);
                setLayersOpen(false);
              }}
            />
          )}

          {/* Filter Controls */}
          {filterOpen && (
            <FilterControlsPopup
              onClose={() => setFilterOpen(false)}
              onApply={cities => {
                setFilterCities(cities);
                setFilterOpen(false);
              }}
            />
          )}

          // Right-side Panels for Vessels and Ports
          {showVesselList && (
            <div className="side-panel">
              <div className="popup-glass">
                <button className="popup-close" onClick={() => setShowVesselList(false)}>×</button>
                <VesselListPanel />
              </div>
            </div>
          )}

          {showPortList && (
            <div className="side-panel">
              <div className="popup-glass">
                <button className="popup-close" onClick={() => setShowPortList(false)}>×</button>
                <PortListPanel />
              </div>
            </div>
          )}

          {/* Dashboard Controls (only uses “View All”) */}
          {dashboardOpen && (
            <DashboardControlsPopup
              sections={DASH_SECTIONS}
              selected={[]}     // ignored for now
              viewAll={viewAllDash}
              onClose={() => setDashboardOpen(false)}
              onApply={({ viewAll }) => {
                setViewAllDash(viewAll);
                setDashboardOpen(false);
                // TODO: open right-hand side panel with these controls
              }}
            />
          )}
        </main>
        {/* NEW: Full Dashboard Overlay */}
          <MaritimeDashboardOverlay
            isVisible={showDashboard}
            onClose={() => setShowDashboard(false)}
          />

      </div>



      {/* Right‐side Dashboard Panel when “View All” is checked */}
      {viewAllDash && (
        <div className="side-panel side-panel--dashboard">
          <div className="popup-glass popup-glass--dashboard">
            <button
              className="popup-close"
              onClick={() => setViewAllDash(false)}
            >
              ×
            </button>
            {/* Reuse your existing DashboardPanel here */}
            <DashboardPanel />
          </div>
        </div>
      )}
    </div>
  );
}

