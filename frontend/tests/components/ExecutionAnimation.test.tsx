import React from 'react';
import { describe, test, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ExecutionAnimation } from '../../src/components/ExecutionAnimation';

describe('ExecutionAnimation Component', () => {
  test('returns null when status is not executing', () => {
    const { container } = render(<ExecutionAnimation status="idle" winner={null} />);
    expect(container.firstChild).toBeNull();
  });

  test('renders green wave HUD signals and countdown when executing', () => {
    render(<ExecutionAnimation status="executing" winner="route_a_speed_first" />);
    
    expect(screen.getByText(/Emergency Corridor Active/i)).toBeInTheDocument();
    expect(screen.getByText(/INT_01 \[GREEN WAVE\]/i)).toBeInTheDocument();
    expect(screen.getByText(/Surface Streets/i)).toBeInTheDocument();
  });
});
