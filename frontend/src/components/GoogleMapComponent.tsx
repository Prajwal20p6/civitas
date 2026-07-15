import React, { useEffect, useState } from 'react';

interface GoogleMapComponentProps {
  status: string;
  winner: string | null;
}

export const GoogleMapComponent: React.FC<GoogleMapComponentProps> = ({ status, winner }) => {
  const [ambulancePos, setAmbulancePos] = useState({ x: 50, y: 250 });
  const [lights, setLights] = useState(['red', 'red', 'red']);
  
  useEffect(() => {
    if (status !== 'executing') {
      setAmbulancePos({ x: 50, y: 250 });
      setLights(['red', 'red', 'red']);
      return;
    }
    
    // Animate ambulance moving along Surface Streets
    let step = 0;
    const interval = setInterval(() => {
      step += 1;
      if (step <= 10) {
        setAmbulancePos({ x: 50 + step * 40, y: 250 });
        if (step > 2) setLights(['green', 'red', 'red']);
        if (step > 5) setLights(['green', 'green', 'red']);
        if (step > 8) setLights(['green', 'green', 'green']);
      } else {
        clearInterval(interval);
      }
    }, 400);
    
    return () => clearInterval(interval);
  }, [status]);

  return (
    <div className="relative w-full h-[500px] bg-slate-950 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
      {/* Background Grid Pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] opacity-30" />
      
      {/* City Map Roads layout */}
      <svg className="absolute inset-0 w-full h-full" xmlns="http://www.w3.org/2000/svg">
        {/* Surface Streets Corridor (Main Diagonal Path) */}
        <path 
          d="M 50 250 L 150 250 L 250 250 L 350 250 L 450 250" 
          stroke={status === 'executing' && winner === 'route_a_speed_first' ? '#22c55e' : '#334155'} 
          strokeWidth={status === 'executing' ? "8" : "6"}
          strokeDasharray={status === 'executing' ? "none" : "4 4"}
          className="transition-all duration-500"
          fill="none" 
        />
        
        {/* Highway 1 alternative Corridor (Arc Path) */}
        <path 
          d="M 50 250 C 150 100, 350 100, 450 250" 
          stroke={status === 'executing' && winner === 'route_b_fairness_first' ? '#22c55e' : '#334155'} 
          strokeWidth={status === 'executing' ? "8" : "6"}
          fill="none" 
        />
        
        {/* Critical Intersections (Nodes) */}
        <g>
          {/* Intersection 1 */}
          <circle cx="150" cy="250" r="14" fill="#1e293b" stroke="#475569" strokeWidth="2" />
          <circle cx="150" cy="250" r="6" fill={lights[0] === 'green' ? '#22c55e' : '#ef4444'} />
          <text x="150" y="280" fill="#94a3b8" fontSize="10" textAnchor="middle" fontFamily="monospace">INT_01</text>
          
          {/* Intersection 2 */}
          <circle cx="300" cy="250" r="14" fill="#1e293b" stroke="#475569" strokeWidth="2" />
          <circle cx="300" cy="250" r="6" fill={lights[1] === 'green' ? '#22c55e' : '#ef4444'} />
          <text x="300" y="280" fill="#94a3b8" fontSize="10" textAnchor="middle" fontFamily="monospace">INT_02</text>
          
          {/* Intersection 3 */}
          <circle cx="450" cy="250" r="14" fill="#1e293b" stroke="#475569" strokeWidth="2" />
          <circle cx="450" cy="250" r="6" fill={lights[2] === 'green' ? '#22c55e' : '#ef4444'} />
          <text x="450" y="280" fill="#94a3b8" fontSize="10" textAnchor="middle" fontFamily="monospace">INT_03</text>
        </g>
        
        {/* Hospital (Destination Node) */}
        <g transform="translate(440, 210)">
          <rect width="20" height="20" rx="4" fill="#ef4444" />
          <path d="M 10 4 L 10 16 M 4 10 L 16 10" stroke="white" strokeWidth="3" />
          <text x="10" y="-8" fill="#f87171" fontSize="9" fontWeight="bold" textAnchor="middle" fontFamily="monospace">HOSPITAL</text>
        </g>

        {/* Dispatch (Start Node) */}
        <g transform="translate(25, 240)">
          <circle cx="10" cy="10" r="6" fill="#3b82f6" className="animate-ping" />
          <circle cx="10" cy="10" r="4" fill="#3b82f6" />
          <text x="10" y="-8" fill="#60a5fa" fontSize="9" fontWeight="bold" textAnchor="middle" fontFamily="monospace">DISPATCH</text>
        </g>

        {/* Animated Ambulance Icon */}
        {status === 'executing' && (
          <g transform={`translate(${ambulancePos.x - 10}, ${ambulancePos.y - 10})`}>
            <rect width="20" height="12" rx="3" fill="#ffffff" stroke="#ef4444" strokeWidth="2" />
            <circle cx="5" cy="12" r="3" fill="#1e293b" />
            <circle cx="15" cy="12" r="3" fill="#1e293b" />
            {/* Siren Ping */}
            <circle cx="10" cy="-2" r="3" fill="#3b82f6" className="animate-bounce" />
          </g>
        )}
      </svg>
      
      {/* Map Labels and HUD Overlay */}
      <div className="absolute top-4 left-4 bg-slate-900/90 border border-slate-800 rounded-xl p-3 backdrop-blur-md font-mono text-xs text-slate-300 space-y-1">
        <div className="text-white font-bold">CIVITAS GIS SIMULATION</div>
        <div className="flex items-center gap-1.5">
          <span className={`w-2 h-2 rounded-full ${status === 'executing' ? 'bg-green-500 animate-pulse' : 'bg-amber-500'}`} />
          <span>Status: {status.toUpperCase()}</span>
        </div>
        {winner && <div>Corridor: {winner === 'route_a_speed_first' ? 'Surface Streets (Plan A)' : 'Highway 1 (Plan B)'}</div>}
      </div>

      <div className="absolute bottom-4 right-4 bg-slate-900/90 border border-slate-800 rounded-xl p-2 backdrop-blur-md text-[10px] text-slate-500 font-mono">
        GOOGLE MAPS PLATFORM • Palo Alto Grid
      </div>
    </div>
  );
};
