import React, { useState } from 'react';
import './SessionSetup.css';

interface SessionSetupProps {
  onSessionStart: (variant: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
  onClearError: () => void;
}

const SessionSetup: React.FC<SessionSetupProps> = ({
  onSessionStart,
  isLoading,
  error,
  onClearError,
}) => {
  const [selectedVariant, setSelectedVariant] = useState<string>('US');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isLoading) return;
    
    try {
      await onSessionStart(selectedVariant);
    } catch (err) {
      // Error is handled by the hook
    }
  };

  const handleRetry = () => {
    onClearError();
  };

  return (
    <div className="session-setup-container">
      <div className="session-setup-card">
        <h1 className="session-setup-title">Welcome to AI Lingo</h1>
        <p className="session-setup-subtitle">
          Learn English idioms and expressions through natural conversation
        </p>

        <form onSubmit={handleSubmit} className="session-setup-form">
          <div className="form-group">
            <label className="form-label">Select Language Variant</label>
            <div className="variant-options">
              <label className="variant-option">
                <input
                  type="radio"
                  name="variant"
                  value="US"
                  checked={selectedVariant === 'US'}
                  onChange={(e) => setSelectedVariant(e.target.value)}
                  disabled={isLoading}
                />
                <span className="variant-label">
                  <span className="variant-flag">🇺🇸</span>
                  <span className="variant-text">US English</span>
                </span>
              </label>

              <label className="variant-option">
                <input
                  type="radio"
                  name="variant"
                  value="UK"
                  checked={selectedVariant === 'UK'}
                  onChange={(e) => setSelectedVariant(e.target.value)}
                  disabled={isLoading}
                />
                <span className="variant-label">
                  <span className="variant-flag">🇬🇧</span>
                  <span className="variant-text">UK English</span>
                </span>
              </label>

              <label className="variant-option">
                <input
                  type="radio"
                  name="variant"
                  value="Custom"
                  checked={selectedVariant === 'Custom'}
                  onChange={(e) => setSelectedVariant(e.target.value)}
                  disabled={isLoading}
                />
                <span className="variant-label">
                  <span className="variant-flag">🌍</span>
                  <span className="variant-text">Custom</span>
                </span>
              </label>
            </div>
          </div>

          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              <span className="error-text">{error}</span>
              <button
                type="button"
                onClick={handleRetry}
                className="error-retry-button"
              >
                Retry
              </button>
            </div>
          )}

          <button
            type="submit"
            className="start-button"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className="loading-spinner"></span>
                <span>Starting Session...</span>
              </>
            ) : (
              'Start Learning'
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default SessionSetup;
