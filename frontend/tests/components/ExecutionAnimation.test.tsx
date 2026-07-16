import React from 'react';
import { describe, test, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ExecutionAnimation } from '../../src/components/ExecutionAnimation';

import { MemoryRouter } from 'react-router-dom';

describe('ExecutionAnimation Component', () => {
  test('returns null when status is not executing', () => {
    const { container } = render(
      <MemoryRouter>
        <ExecutionAnimation status="idle" winner={null} />
      </MemoryRouter>
    );
    expect(container.firstChild).toBeNull();
  });

  test('renders green wave HUD signals and countdown when executing', () => {
    render(
      <MemoryRouter>
        <ExecutionAnimation status="executing" winner="route_a_speed_first" />
      </MemoryRouter>
    );
    
    expect(screen.getByText(/Emergency Corridor Active/i)).toBeInTheDocument();
    expect(screen.getByText(/INT_01 \[GREEN WAVE\]/i)).toBeInTheDocument();
    expect(screen.getByText(/Surface Streets/i)).toBeInTheDocument();
  });
});
