import React, { useEffect, useState } from 'react';
import { GoogleMap, useJsApiLoader, MarkerF, PolylineF } from '@react-google-maps/api';
import { useParams } from 'react-router-dom';
import { useFirestore } from '../hooks/useFirestore';

// --- Error Boundary for Google Maps API/rendering Errors ---
class MapErrorBoundary extends React.Component<{ children: React.ReactNode }, { hasError: boolean; error: Error | null }> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("Google Maps Error Boundary caught an error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="relative w-full h-[500px] bg-red-50 border border-red-200 rounded-2xl overflow-hidden shadow-sm flex flex-col items-center justify-center p-6 text-center">
          <div className="text-red-600 font-bold mb-2">⚠️ Google Maps Load Error</div>
          <div className="text-xs text-red-500 font-mono mb-4">{this.state.error?.message || "Unknown rendering or API error"}</div>
          <button 
            onClick={() => this.setState({ hasError: false, error: null })}
            className="px-4 py-2 bg-red-600 text-white rounded-lg text-xs hover:bg-red-700 transition-colors shadow-sm font-sans"
          >
            Retry Loading Map
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

const mapContainerStyle = {
  width: '100%',
  height: '100%'
};

const centerLA = {
  lat: 34.0522,
  lng: -118.2437
};

const routeAPath = [
  { lat: 34.0522, lng: -118.2437 },
  { lat: 34.0562, lng: -118.2487 },
  { lat: 34.0612, lng: -118.2537 },
  { lat: 34.0662, lng: -118.2587 },
  { lat: 34.0722, lng: -118.2637 }
];

const routeBPath = [
  { lat: 34.0522, lng: -118.2437 },
  { lat: 34.0482, lng: -118.2537 },
  { lat: 34.0532, lng: -118.2687 },
  { lat: 34.0632, lng: -118.2737 },
  { lat: 34.0722, lng: -118.2637 }
];

interface GoogleMapComponentProps {
  status?: string;
  winner?: string | null;
  incidents?: any[];
}

export const GoogleMapComponent: React.FC<GoogleMapComponentProps> = ({ 
  status: propStatus, 
  winner: propWinner,
  incidents = []
}) => {
  const { id } = useParams<{ id: string }>();
  const { incidentData } = useFirestore(propStatus !== undefined ? null : (id || null));

  const status = propStatus !== undefined ? propStatus : incidentData?.status || 'idle';
  const winner = propWinner !== undefined ? propWinner : incidentData?.decision?.winner || null;

  const activePath = winner === 'route_b_fairness_first' ? routeBPath : routeAPath;
  const [ambulancePos, setAmbulancePos] = useState(activePath[0]);

  // Load Google Maps API script
  const { isLoaded, loadError } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ''
  });

  useEffect(() => {
    if (status !== 'executing') {
      if (status === 'success' || status === 'completed') {
        setAmbulancePos(activePath[activePath.length - 1]);
      } else {
        setAmbulancePos(activePath[0]);
      }
      return;
    }

    const durationMs = 15000; // 15 seconds matching progress countdown
    const intervalMs = 100;   // 100ms interval for smooth 10fps updates
    const steps = durationMs / intervalMs;
    let step = 0;

    const interval = setInterval(() => {
      step += 1;
      const progress = Math.min(step / steps, 1);
      
      // Interpolate along activePath
      const pathLength = activePath.length;
      const exactIndex = progress * (pathLength - 1);
      const segmentIndex = Math.min(Math.floor(exactIndex), pathLength - 2);
      const factor = exactIndex - segmentIndex;

      const startNode = activePath[segmentIndex];
      const endNode = activePath[segmentIndex + 1];

      const currentLat = startNode.lat + factor * (endNode.lat - startNode.lat);
      const currentLng = startNode.lng + factor * (endNode.lng - startNode.lng);

      setAmbulancePos({ lat: currentLat, lng: currentLng });

      if (progress >= 1) {
        clearInterval(interval);
      }
    }, intervalMs);

    return () => clearInterval(interval);
  }, [status, winner]);

  // Fallback view if Maps API fails, is loading, or inside test environment
  if (!isLoaded || loadError) {
    return (
      <div className="relative w-full h-[500px] bg-slate-50 border border-slate-200 rounded-2xl overflow-hidden shadow-sm flex items-center justify-center text-slate-600 font-mono text-xs">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#f1f5f9_1px,transparent_1px),linear-gradient(to_bottom,#f1f5f9_1px,transparent_1px)] bg-[size:4rem_4rem] opacity-40" />
        <div className="z-10 text-center space-y-2">
          <div className="text-slate-805 text-slate-800 font-bold font-sans text-sm">🗺️ Google Maps Loading (LA Grid fallback active)</div>
          <div className="text-[10px] text-slate-500">Status: {status.toUpperCase()}</div>
          {status === 'executing' && (
            <div className="text-blue-600 font-bold animate-pulse">Ambulance Moving: {ambulancePos.lat.toFixed(4)}, {ambulancePos.lng.toFixed(4)}</div>
          )}
        </div>
      </div>
    );
  }

  return (
    <MapErrorBoundary>
      <div className="relative w-full h-[500px] border border-slate-200 rounded-2xl overflow-hidden shadow-md">
        <GoogleMap
          mapContainerStyle={mapContainerStyle}
          center={centerLA}
          zoom={11}
          options={{
          styles: [
            { elementType: "geometry", stylers: [{ color: "#f5f5f5" }] },
            { elementType: "labels.text.stroke", stylers: [{ color: "#ffffff" }] },
            { elementType: "labels.text.fill", stylers: [{ color: "#333333" }] },
            { featureType: "administrative", stylers: [{ visibility: "on" }] },
            { featureType: "road", elementType: "geometry", stylers: [{ color: "#ffffff" }] },
            { featureType: "road", elementType: "geometry.stroke", stylers: [{ color: "#e0e0e0" }] },
            { featureType: "road", elementType: "labels.text.fill", stylers: [{ color: "#757575" }] },
            { featureType: "water", elementType: "geometry", stylers: [{ color: "#c9e2f5" }] }
          ],
          disableDefaultUI: true,
          zoomControl: false,
        }}
      >
        {/* Render all active incidents */}
        {incidents.map((inc, i) => (
          <MarkerF
            key={inc.id || i}
            position={inc.location || centerLA}
            title={`Incident: ${inc.id}`}
            options={{
              icon: {
                path: window.google?.maps?.SymbolPath?.CIRCLE ?? 0,
                fillColor: '#ef4444',
                fillOpacity: 1,
                strokeWeight: 2,
                strokeColor: '#ffffff',
                scale: 8,
              }
            }}
          />
        ))}

        {/* If standalone route mode, show active incident marker */}
        {incidents.length === 0 && (
          <MarkerF
            position={centerLA}
            title="Active Incident"
            options={{
              icon: {
                path: window.google?.maps?.SymbolPath?.CIRCLE ?? 0,
                fillColor: '#ef4444',
                fillOpacity: 1,
                strokeWeight: 2,
                strokeColor: '#ffffff',
                scale: 8,
              }
            }}
          />
        )}

        {/* Hospital Destination Marker */}
        <MarkerF
          position={{ lat: 34.0722, lng: -118.2637 }}
          title="County Hospital"
          options={{
            icon: {
              path: window.google?.maps?.SymbolPath?.FORWARD_CLOSED_ARROW ?? 1,
              fillColor: '#3b82f6',
              fillOpacity: 1,
              strokeWeight: 1,
              strokeColor: '#ffffff',
              scale: 6,
            }
          }}
        />

        {/* Route Path (solid blue line) and Preemption Animation */}
        {(status === 'executing' || status === 'success' || status === 'completed') && (
          <>
            <PolylineF
              path={activePath}
              options={{
                strokeColor: '#2563eb', // solid blue line
                strokeOpacity: 0.9,
                strokeWeight: 5,
                geodesic: true,
              }}
            />
            {/* Blinking green waves along polyline corridor */}
            <PolylineF
              path={activePath}
              options={{
                strokeColor: '#10b981', // green wave highlight
                strokeOpacity: 0.4,
                strokeWeight: 10,
                geodesic: true,
              }}
            />
            {/* Real-time updating Ambulance Marker */}
            <MarkerF
              position={ambulancePos}
              title="Ambulance"
              options={{
                icon: {
                  path: window.google?.maps?.SymbolPath?.CIRCLE ?? 0,
                  fillColor: '#ef4444', // Red center
                  fillOpacity: 1,
                  strokeWeight: 3,
                  strokeColor: '#3b82f6', // Blue flashing border
                  scale: 8,
                }
              }}
            />
          </>
        )}

        {/* Success checkmark marker at destination */}
        {(status === 'success' || status === 'completed') && (
          <MarkerF
            position={{ lat: 34.0722, lng: -118.2637 }}
            title="Success Checkmark"
            options={{
              icon: {
                path: 'M -3,0 L -1,2 L 3,-2',
                strokeColor: '#10b981',
                strokeWeight: 4,
                scale: 3,
              }
            }}
          />
        )}
      </GoogleMap>

      {/* Info HUD */}
      <div className="absolute top-4 left-4 bg-white/95 border border-slate-200 rounded-xl p-3 backdrop-blur-md font-mono text-xs text-slate-600 shadow-md space-y-1">
        <div className="text-slate-800 font-bold font-sans">CIVITAS GIS SIMULATION (LA)</div>
        <div className="flex items-center gap-1.5 text-slate-500">
          <span className={`w-2 h-2 rounded-full ${status === 'executing' ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
          <span>Status: {status.toUpperCase()}</span>
        </div>
      </div>
      </div>
    </MapErrorBoundary>
  );
};
