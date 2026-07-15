import React from 'react';
import { describe, test, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ApprovalModal } from '../../src/components/ApprovalModal';

describe('ApprovalModal Component', () => {
  test('returns null when show is false', () => {
    const { container } = render(<ApprovalModal show={false} onApprove={() => {}} onOverride={() => {}} />);
    expect(container.firstChild).toBeNull();
  });

  test('renders modal warning and executes approve/override callbacks', () => {
    const onApprove = vi.fn();
    const onOverride = vi.fn();
    
    render(<ApprovalModal show={true} onApprove={onApprove} onOverride={onOverride} />);
    
    expect(screen.getByText(/Operator Approval Required/i)).toBeInTheDocument();
    
    const approveBtn = screen.getByRole('button', { name: /Approve Plan/i });
    const overrideBtn = screen.getByRole('button', { name: /Override/i });
    
    fireEvent.click(approveBtn);
    expect(onApprove).toHaveBeenCalledOnce();
    
    fireEvent.click(overrideBtn);
    expect(onOverride).toHaveBeenCalledOnce();
  });
});
