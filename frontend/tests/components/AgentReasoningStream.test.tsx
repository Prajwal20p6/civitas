import React from 'react';
import { describe, test, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AgentReasoningStream } from '../../src/components/AgentReasoningStream';

describe('AgentReasoningStream Component', () => {
  test('renders empty idle message when no logs are provided', () => {
    render(<AgentReasoningStream logs={[]} status="idle" />);
    expect(screen.getByText(/No incident active. Stream idle./i)).toBeInTheDocument();
  });

  test('renders log lines and live indicators during processing status', () => {
    const logs = [
      { timestamp: Date.now(), message: 'Perception classified incident' }
    ];
    render(<AgentReasoningStream logs={logs} status="processing" />);
    
    expect(screen.getByText(/● LIVE/i)).toBeInTheDocument();
    expect(screen.getByText(/Perception classified incident/i)).toBeInTheDocument();
  });
});
