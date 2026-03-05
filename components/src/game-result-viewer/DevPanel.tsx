import { useState } from 'react';
import { MOCK_DATA_MAP, SPORT_STATES } from './mock-data';

type GameData = (typeof MOCK_DATA_MAP)[string];

interface DevPanelProps {
  onDataChange: (data: GameData) => void;
}

const SPORTS = Object.keys(SPORT_STATES) as Array<keyof typeof SPORT_STATES>;

function getSportFromUrl(): string {
  return new URLSearchParams(window.location.search).get('sport') || 'basketball';
}

function getStateFromUrl(sport: string): string {
  const stateParam = new URLSearchParams(window.location.search).get('state');
  return stateParam || SPORT_STATES[sport][0];
}

export function DevPanel({ onDataChange }: DevPanelProps) {
  if (import.meta.env.VITE_INCLUDE_MOCK !== 'true') return null;

  const [sport, setSport] = useState(getSportFromUrl);
  const [state, setState] = useState(() => getStateFromUrl(getSportFromUrl()));
  const [isCollapsed, setIsCollapsed] = useState(false);

  const availableStates = SPORT_STATES[sport] || [];

  const handleSportChange = (newSport: string) => {
    const newStates = SPORT_STATES[newSport] || [];
    const newState = newStates[0] || '';
    setSport(newSport);
    setState(newState);
    applyMockData(newSport, newState);
    updateUrl(newSport, newState);
  };

  const handleStateChange = (newState: string) => {
    setState(newState);
    applyMockData(sport, newState);
    updateUrl(sport, newState);
  };

  const applyMockData = (s: string, st: string) => {
    const key = `${s}_${st}`;
    const data = MOCK_DATA_MAP[key];
    if (data) {
      onDataChange(data);
      console.log(`[DEV] Mock changed: ${key}`);
    } else {
      console.warn(`[DEV] No mock data for key: ${key}`);
    }
  };

  const updateUrl = (s: string, st: string) => {
    const url = new URL(window.location.href);
    url.searchParams.set('sport', s);
    url.searchParams.set('state', st);
    window.history.replaceState({}, '', url.toString());
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: '12px',
        right: '12px',
        zIndex: 9999,
        background: 'rgba(15, 15, 15, 0.88)',
        border: '1px solid rgba(255,255,255,0.15)',
        borderRadius: '8px',
        color: '#e0e0e0',
        fontSize: '11px',
        fontFamily: 'monospace',
        minWidth: '160px',
        boxShadow: '0 4px 16px rgba(0,0,0,0.5)',
        backdropFilter: 'blur(8px)',
        userSelect: 'none',
      }}
    >
      {/* Header */}
      <div
        onClick={() => setIsCollapsed((v) => !v)}
        style={{
          padding: '6px 10px',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: isCollapsed ? 'none' : '1px solid rgba(255,255,255,0.1)',
        }}
      >
        <span style={{ color: '#7dd3fc', fontWeight: 'bold' }}>⚙ DEV</span>
        <span style={{ opacity: 0.6, fontSize: '10px' }}>{isCollapsed ? '▼' : '▲'}</span>
      </div>

      {/* Body */}
      {!isCollapsed && (
        <div style={{ padding: '8px 10px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {/* Sport selector */}
          <label style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
            <span style={{ opacity: 0.6, fontSize: '10px' }}>SPORT</span>
            <select
              value={sport}
              onChange={(e) => handleSportChange(e.target.value)}
              style={{
                background: 'rgba(255,255,255,0.1)',
                border: '1px solid rgba(255,255,255,0.2)',
                borderRadius: '4px',
                color: '#e0e0e0',
                padding: '3px 6px',
                fontSize: '11px',
                cursor: 'pointer',
                outline: 'none',
              }}
            >
              {SPORTS.map((s) => (
                <option key={s} value={s} style={{ background: '#1a1a1a', color: '#e0e0e0' }}>
                  {s}
                </option>
              ))}
            </select>
          </label>

          {/* State selector */}
          <label style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
            <span style={{ opacity: 0.6, fontSize: '10px' }}>STATE</span>
            <select
              value={state}
              onChange={(e) => handleStateChange(e.target.value)}
              style={{
                background: 'rgba(255,255,255,0.1)',
                border: '1px solid rgba(255,255,255,0.2)',
                borderRadius: '4px',
                color: '#e0e0e0',
                padding: '3px 6px',
                fontSize: '11px',
                cursor: 'pointer',
                outline: 'none',
              }}
            >
              {availableStates.map((st) => (
                <option key={st} value={st} style={{ background: '#1a1a1a', color: '#e0e0e0' }}>
                  {st}
                </option>
              ))}
            </select>
          </label>

          {/* Active key indicator */}
          <div
            style={{
              marginTop: '2px',
              padding: '3px 6px',
              background: 'rgba(125, 211, 252, 0.1)',
              borderRadius: '4px',
              color: '#7dd3fc',
              fontSize: '10px',
              letterSpacing: '0.02em',
            }}
          >
            {sport}_{state}
          </div>
        </div>
      )}
    </div>
  );
}
