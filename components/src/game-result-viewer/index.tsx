import { createRoot } from 'react-dom/client';
import { useState, useEffect } from 'react';
import { z } from 'zod';
import { BasketballViewer, BasketballGameDataSchema } from './sports/basketball';
import { VolleyballViewer, VolleyballGameDataSchema } from './sports/volleyball';
import { SoccerViewer, SoccerGameDataSchema } from './sports/soccer';
import { BaseballViewer, BaseballGameDataSchema } from './sports/baseball';
import { DevPanel } from './DevPanel';
import '../index.css';

// 개발용 mock 데이터 주입 (VITE_INCLUDE_MOCK=true 일 때만)
if (import.meta.env.VITE_INCLUDE_MOCK === 'true') {
  import('./mock-data').then((module) => {
    const params = new URLSearchParams(window.location.search);
    const sport = params.get('sport') || 'basketball';
    const state = params.get('state') || module.SPORT_STATES[sport]?.[0] || '예정';
    const key = `${sport}_${state}`;
    const data = module.MOCK_DATA_MAP[key] ?? module.mockBasketballData;
    window.openai = { toolOutput: data };
    console.log(`[DEV] Mock injected: ${key}`, data);
  });
}

// Declare global window type for OpenAI Apps SDK
declare global {
  interface Window {
    openai?: {
      toolInput?: any;
      toolOutput?: any;
      toolResponseMetadata?: any;
      theme?: 'light' | 'dark';
    };
  }
}

// 테마 감지 및 적용 훅
function useTheme() {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    let currentTheme: 'light' | 'dark' = 'light';

    const updateTheme = () => {
      // OpenAI Apps SDK의 테마 감지
      const sdkTheme = window.openai?.theme;

      // 시스템 다크 모드 감지 (폴백)
      const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

      const newTheme = sdkTheme || (systemPrefersDark ? 'dark' : 'light');

      // 테마가 변경된 경우에만 업데이트
      if (newTheme !== currentTheme) {
        currentTheme = newTheme;
        setTheme(newTheme);
        document.documentElement.setAttribute('data-theme', newTheme);
      }
    };

    // 초기 테마 설정
    updateTheme();

    // 시스템 테마 변경 감지
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener('change', updateTheme);

    // OpenAI 테마 변경 감지를 위한 폴링 (SDK에서 테마 변경 시)
    const intervalId = setInterval(updateTheme, 1000);

    return () => {
      mediaQuery.removeEventListener('change', updateTheme);
      clearInterval(intervalId);
    };
  }, []);

  return theme;
}

// 전체 게임 데이터 스키마 (sportType으로 분기)
const GameDataSchema = z.discriminatedUnion('sportType', [
  BasketballGameDataSchema,
  VolleyballGameDataSchema,
  SoccerGameDataSchema,
  BaseballGameDataSchema,
]);

type GameData = z.infer<typeof GameDataSchema>;

// 에러 폴백 컴포넌트
function ErrorFallback({ error }: { error: string }) {
  return (
    <div className="max-w-2xl mx-auto my-8 p-8 bg-danger-soft rounded-lg shadow-lg border border-danger-outline">
      <h1 className="text-2xl font-bold text-danger mb-4">Validation Error</h1>
      <p className="text-danger-soft font-mono text-sm whitespace-pre-wrap">{error}</p>
    </div>
  );
}

// 로딩 컴포넌트
function Loading() {
  return (
    <div className="max-w-2xl mx-auto my-8 p-8 bg-surface-secondary rounded-lg shadow-lg">
      <p className="text-secondary">Loading game data...</p>
    </div>
  );
}

// 지원하지 않는 스포츠 타입
function UnsupportedSport({ sportType }: { sportType: string }) {
  return (
    <div className="max-w-2xl mx-auto my-8 p-8 bg-caution-soft rounded-lg shadow-lg border border-caution-outline">
      <h1 className="text-2xl font-bold text-caution mb-4">Unsupported Sport</h1>
      <p className="text-caution-soft">
        스포츠 타입 "{sportType}"은(는) 아직 지원되지 않습니다.
      </p>
      <p className="text-caution text-sm mt-2">
        지원 종목: basketball, soccer, baseball, volleyball
      </p>
    </div>
  );
}

// 스포츠 타입에 따라 적절한 뷰어 렌더링
function SportViewer({ data }: { data: GameData }) {
  switch (data.sportType) {
    case 'basketball':
      return <BasketballViewer data={data} />;
    case 'volleyball':
      return <VolleyballViewer data={data} />;
    case 'soccer':
      return <SoccerViewer data={data} />;
    case 'baseball':
      return <BaseballViewer data={data} />;
    default:
      return <UnsupportedSport sportType={(data as any).sportType} />;
  }
}

// 메인 앱 컴포넌트
function GameResultViewerApp() {
  const [gameData, setGameData] = useState<GameData | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 테마 훅 적용
  useTheme();

  useEffect(() => {
    let intervalId: ReturnType<typeof setInterval> | null = null;

    const updateGameData = () => {
      try {
        const rawData = window.openai?.toolOutput;

        // 데이터가 아직 없으면 대기
        if (!rawData || (typeof rawData === 'object' && Object.keys(rawData).length === 0)) {
          return;
        }

        // 데이터 검증
        const validatedData = GameDataSchema.parse(rawData);

        setGameData(validatedData);
        setError(null);

        // 데이터 로드 성공 시 폴링 중단
        if (intervalId) {
          clearInterval(intervalId);
          intervalId = null;
        }
      } catch (err) {
        if (err instanceof z.ZodError) {
          const errorMessage = err.errors
            .map((e) => `${e.path.join('.')}: ${e.message}`)
            .join('\n');
          console.error('[game-result-viewer] ZodError:', JSON.stringify(err.errors, null, 2));
          setError(errorMessage);
        } else {
          setError(String(err));
        }

        // 에러 발생 시에도 폴링 중단
        if (intervalId) {
          clearInterval(intervalId);
          intervalId = null;
        }
      }
    };

    // 초기 데이터 로드
    updateGameData();

    // 데이터가 아직 없으면 폴링 시작
    if (!gameData && !error) {
      intervalId = setInterval(updateGameData, 100);
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, []);

  // DevPanel에서 mock 데이터 변경 시 직접 state 업데이트
  const handleDevDataChange = (rawData: unknown) => {
    try {
      const validatedData = GameDataSchema.parse(rawData);
      setGameData(validatedData);
      setError(null);
    } catch (err) {
      if (err instanceof z.ZodError) {
        const errorMessage = err.errors
          .map((e) => `${e.path.join('.')}: ${e.message}`)
          .join('\n');
        setError(errorMessage);
      } else {
        setError(String(err));
      }
    }
  };

  if (error) {
    return (
      <>
        <DevPanel onDataChange={handleDevDataChange} />
        <ErrorFallback error={error} />
      </>
    );
  }

  if (!gameData) {
    return (
      <>
        <DevPanel onDataChange={handleDevDataChange} />
        <Loading />
      </>
    );
  }

  const buttonText = gameData.status === '종료'
    ? '세부 경기기록 보기'
    : gameData.status === '진행중'
    ? '실시간 경기기록 및 알림 받기'
    : '세부 전력비교 및 알림 받기';

  return (
    <>
      <DevPanel onDataChange={handleDevDataChange} />
      <div style={{ maxWidth: '420px', margin: '0 auto' }}>
        <SportViewer data={gameData} />
        <a
          href="https://home.psynet.co.kr/livescore"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: 'block',
            width: '100%',
            padding: '14px',
            marginTop: '12px',
            backgroundColor: 'rgb(10, 73, 104)',
            color: 'white',
            textAlign: 'center',
            textDecoration: 'none',
            borderRadius: '8px',
            fontWeight: '600',
            fontSize: '15px',
            boxSizing: 'border-box',
          }}
        >
          {buttonText}
        </a>
      </div>
    </>
  );
}

// 앱 초기화
const rootElement = document.getElementById('game-result-viewer-root');
if (rootElement) {
  const root = createRoot(rootElement);
  root.render(<GameResultViewerApp />);
}

export default GameResultViewerApp;
