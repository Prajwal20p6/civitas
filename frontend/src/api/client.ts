import axios from 'axios';

// Fallback host if proxy is bypassed
const API_BASE = import.meta.env.VITE_BACKEND_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface LocationData {
  lat: number;
  lng: number;
}

export interface DestinationData {
  name: string;
  lat: number;
  lng: number;
}

export interface IncidentPayload {
  incident_type: string;
  description: string;
  location: LocationData;
  destination: DestinationData;
}

export const api = {
  createIncident: async (payload: IncidentPayload) => {
    const res = await axios.post(`${API_BASE}/api/v1/incidents`, payload);
    return res.data;
  },
  
  getIncident: async (incidentId: string) => {
    const res = await axios.get(`${API_BASE}/api/v1/incidents/${incidentId}`);
    return res.data;
  },
  
  approveIncident: async (incidentId: string, status: 'approved' | 'denied', reason: string) => {
    const res = await axios.post(`${API_BASE}/api/v1/approval/${incidentId}`, {
      incident_id: incidentId,
      status,
      reason
    });
    return res.data;
  }
};
