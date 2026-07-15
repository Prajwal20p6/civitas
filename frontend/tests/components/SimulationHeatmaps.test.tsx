import React from 'react';
import { describe, test, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SimulationHeatmaps } from '../../src/components/SimulationHeatmaps';

describe('SimulationHeatmaps Component', () => {
  test('returns null when scores are null', () => {
    const { container } = render(<SimulationHeatmaps scoreA={null} scoreB={null} />);
    expect(container.firstChild).toBeNull();
  });

  test('renders scenario heat maps and congestion scores', () => {
    render(<SimulationHeatmaps scoreA={92} scoreB={74} />);
    
    expect(screen.getByText(/Simulation Congestion Heatmaps/i)).toBeInTheDocument();
    expect(screen.getByText(/Congestion Score: 92/i)).toBeInTheDocument();
    expect(screen.getByText(/Congestion Score: 74/i)).toBeInTheDocument();
  });
});
