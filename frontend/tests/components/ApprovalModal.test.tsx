import React from 'react';
import { describe, test, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { ApprovalModal } from '../../src/components/ApprovalModal';

describe('ApprovalModal Component', () => {
  test('returns null when show is false', () => {
    const { container } = render(
      <MemoryRouter>
        <ApprovalModal show={false} onApprove={() => {}} onOverride={() => {}} />
      </MemoryRouter>
    );
    expect(container.firstChild).toBeNull();
  });

  test('renders modal warning and executes approve/override callbacks', () => {
    const onApprove = vi.fn();
    const onOverride = vi.fn();
    
    render(
      <MemoryRouter>
        <ApprovalModal show={true} onApprove={onApprove} onOverride={onOverride} />
      </MemoryRouter>
    );
    
    expect(screen.getByText(/Operator Approval Required/i)).toBeInTheDocument();
    
    const approveBtn = screen.getByRole('button', { name: /Approve Plan/i });
    const overrideBtn = screen.getByRole('button', { name: /Override/i });
    
    fireEvent.click(approveBtn);
    expect(onApprove).toHaveBeenCalledOnce();
    
    fireEvent.click(overrideBtn);
    expect(onOverride).toHaveBeenCalledOnce();
  });
});
