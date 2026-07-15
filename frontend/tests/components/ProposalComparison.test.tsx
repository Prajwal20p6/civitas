import React from 'react';
import { describe, test, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ProposalComparison } from '../../src/components/ProposalComparison';

describe('ProposalComparison Component', () => {
  test('returns null when proposals are missing', () => {
    const { container } = render(<ProposalComparison proposalA={null} proposalB={null} winner={null} />);
    expect(container.firstChild).toBeNull();
  });

  test('renders comparison metrics cards and marks the winner properly', () => {
    const propA = { recommended_route: 'Surface Streets', ambulance_eta: 8, vehicles_impacted: 12 };
    const propB = { recommended_route: 'Highway 1', ambulance_eta: 11, vehicles_impacted: 3 };
    
    render(<ProposalComparison proposalA={propA} proposalB={propB} winner="route_a_speed_first" />);
    
    expect(screen.getByText(/Plan A \(Speed-First\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Plan B \(Fairness-First\)/i)).toBeInTheDocument();
    expect(screen.getByText(/WINNER/i)).toBeInTheDocument();
    expect(screen.getByText(/8 mins/i)).toBeInTheDocument();
    expect(screen.getByText(/3 vehicles/i)).toBeInTheDocument();
  });
});
