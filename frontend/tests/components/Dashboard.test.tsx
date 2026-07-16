import React from 'react';
import { describe, test, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Dashboard } from '../../src/components/Dashboard';

// Mock hook to control WebSocket streaming state in tests
vi.mock('../../src/hooks/useIncidentStream', () => ({
  useIncidentStream: (incidentId: string | null) => {
    if (incidentId === 'test-incident-uuid') {
      return {
        logs: [
          { timestamp: 12345, message: "Perception Agent: Processing..." },
          { timestamp: 12346, message: "Route Agent: Proposing routes..." }
        ],
        status: 'pending_approval',
        decision: {
          winner: 'route_a_speed_first',
          reasoning_one_liner: 'Surface Streets chosen: saves ambulance 14 minutes.',
          requires_approval: true
        },
        setStatus: vi.fn()
      };
    }
    return {
      logs: [],
      status: 'idle',
      decision: null,
      setStatus: vi.fn()
    };
  }
}));

// Mock API client wrapper
vi.mock('../../src/api/client', () => ({
  api: {
    createIncident: vi.fn().mockResolvedValue({
      incident_id: 'test-incident-uuid',
      status: 'processing',
      message: 'ADK Orchestrator invoked.'
    }),
    approveIncident: vi.fn().mockResolvedValue({
      status: 'approved'
    })
  }
}));

import { MemoryRouter } from 'react-router-dom';

describe('Dashboard Component Tests', () => {
  test('renders initial landing state with Trigger Emergency button', () => {
    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );
    
    // Verify title and button presence
    expect(screen.getByText(/CIVITAS Traffic Coordinator/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Trigger Emergency/i })).toBeInTheDocument();
  });

  test('clicking Trigger Emergency launches flow and displays stream logs', async () => {
    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );
    
    const triggerBtn = screen.getByRole('button', { name: /Trigger Emergency/i });
    fireEvent.click(triggerBtn);
    
    // Verify that the reasoning pipeline terminal receives and displays mock logs
    await waitFor(() => {
      expect(screen.getByText(/Perception Agent: Processing.../i)).toBeInTheDocument();
      expect(screen.getByText(/Route Agent: Proposing routes.../i)).toBeInTheDocument();
    });
  });

  test('displays operator approval modal when status is pending_approval', async () => {
    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );
    
    const triggerBtn = screen.getByRole('button', { name: /Trigger Emergency/i });
    fireEvent.click(triggerBtn);
    
    // Verify approval modal pop-up and decision explainability details appear
    await waitFor(() => {
      expect(screen.getByText(/Operator Approval Required/i)).toBeInTheDocument();
      expect(screen.getByText(/Surface Streets chosen: saves ambulance 14 minutes./i)).toBeInTheDocument();
    });
  });
});
