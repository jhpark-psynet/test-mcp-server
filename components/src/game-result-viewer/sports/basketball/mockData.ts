/**
 * TeamComparison 컴포넌트 테스트용 목 데이터
 */

import type { TeamComparisonData } from './types';

// 팀 비교 통계 목 데이터
export const mockTeamComparison: TeamComparisonData = {
  home: {
    winRate: '0.741',      // 승률
    avgPoints: 118.5,      // 평균 득점
    avgPointsAgainst: 108.2, // 평균 실점
    fgPct: '0.482',        // FG%
    threePct: '0.378',     // 3P%
    avgRebounds: 45.3,     // 평균 리바운드
    avgAssists: 28.1,      // 평균 어시스트
    avgSteals: 8.2,        // 평균 스틸
    avgBlocks: 5.4,        // 평균 블록
    avgTurnovers: 13.1,    // 평균 턴오버
  },
  away: {
    winRate: '0.667',
    avgPoints: 114.2,
    avgPointsAgainst: 110.5,
    fgPct: '0.468',
    threePct: '0.365',
    avgRebounds: 43.8,
    avgAssists: 26.4,
    avgSteals: 7.5,
    avgBlocks: 4.8,
    avgTurnovers: 14.2,
  },
};

// 전체 BeforeGame 테스트용 목 데이터
export const mockBeforeGameData = {
  sportType: 'basketball' as const,
  league: 'NBA' as const,
  date: '12.24',
  time: '11:00',
  status: '예정' as const,
  venue: 'Chase Center',
  homeTeam: {
    name: '골든스테이트 워리어스',
    shortName: '골든스테이트',
    logo: 'https://lscdn.psynet.co.kr/livescore/photo/spt/livescore/emb_new/emblem_mid_OT31260.png',
    record: '20승 7패',
    score: 0,
    players: [],
    recentGames: ['W', 'W', 'L', 'W', 'W'] as const,
  },
  awayTeam: {
    name: '로스앤젤레스 레이커스',
    shortName: 'LA레이커스',
    logo: 'https://lscdn.psynet.co.kr/livescore/photo/spt/livescore/emb_new/emblem_mid_OT31254.png',
    record: '18승 9패',
    score: 0,
    players: [],
    recentGames: ['L', 'W', 'W', 'L', 'W'] as const,
  },
  teamComparison: mockTeamComparison,
};
