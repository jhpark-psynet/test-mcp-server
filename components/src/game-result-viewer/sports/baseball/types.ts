import { z } from 'zod';

// 야구 리그 (유연한 string)
export type BaseballLeague = string;

// 경기 상태
export type GameStatus = '예정' | '진행중' | '종료';

// 최근 경기 결과
export type RecentGameResult = 'W' | 'L' | 'D';

// 이닝별 점수 (홈/원정 모두 포함)
export interface InningScore {
  inning: number;
  homeScore: string;  // "-" 또는 "X" 가능
  awayScore: string;
}

// 타자 스탯
export interface BaseballBatterStats {
  batOrder: number;
  name: string;
  position: string;
  atBats: number;
  hits: number;
  homeRuns: number;
  rbi: number;
  walks: number;
  strikeouts: number;
  avg: string;   // ".312" 형식
  obp: string;
  ops: string;
}

// 투수 스탯
export interface BaseballPitcherStats {
  turnNo: number;
  name: string;
  result: string;      // "승", "패", "세", "홀", "BS", ""
  innings: string;     // "6.0" 형식
  pitchCount: number;
  hits: number;
  strikeouts: number;
  runs: number;
  earnedRuns: number;
  era: string;
  whip: string;
}

// 팀 정보
export interface BaseballTeamInfo {
  name: string;
  shortName: string;
  logo: string;
  score: number;
  record: string;          // "83승 0무 79패"
  inningScores: InningScore[];
  batters: BaseballBatterStats[];
  pitchers: BaseballPitcherStats[];
  recentGames?: RecentGameResult[];
  teamHits?: number;
  teamErrors?: number;
}

// 경기 기록
export interface BaseballGameRecord {
  label: string;
  home: number | string;
  away: number | string;
}

// 맞대결 기록
export interface BaseballHeadToHead {
  totalGames: number;
  homeWins: number;
  awayWins: number;
  draws: number;
}

// 야구 경기 데이터 (메인)
export interface BaseballGameData {
  sportType: 'baseball';
  league: BaseballLeague;
  date: string;
  time?: string;
  status: GameStatus;
  venue?: string;
  homeTeam: BaseballTeamInfo;
  awayTeam: BaseballTeamInfo;
  homeStarterName?: string;
  awayStarterName?: string;
  gameRecords?: BaseballGameRecord[];
  headToHead?: BaseballHeadToHead;
}

// ===== Zod 스키마 =====

export const RecentGameResultSchema = z.enum(['W', 'L', 'D']);

export const InningScoreSchema = z.object({
  inning: z.number(),
  homeScore: z.string(),
  awayScore: z.string(),
});

export const BaseballBatterStatsSchema = z.object({
  batOrder: z.number(),
  name: z.string(),
  position: z.string(),
  atBats: z.number(),
  hits: z.number(),
  homeRuns: z.number(),
  rbi: z.number(),
  walks: z.number(),
  strikeouts: z.number(),
  avg: z.string(),
  obp: z.string(),
  ops: z.string(),
});

export const BaseballPitcherStatsSchema = z.object({
  turnNo: z.number(),
  name: z.string(),
  result: z.string(),
  innings: z.string(),
  pitchCount: z.number(),
  hits: z.number(),
  strikeouts: z.number(),
  runs: z.number(),
  earnedRuns: z.number(),
  era: z.string(),
  whip: z.string(),
});

export const BaseballTeamInfoSchema = z.object({
  name: z.string(),
  shortName: z.string(),
  logo: z.string(),
  score: z.number(),
  record: z.string(),
  inningScores: z.array(InningScoreSchema),
  batters: z.array(BaseballBatterStatsSchema),
  pitchers: z.array(BaseballPitcherStatsSchema),
  recentGames: z.array(RecentGameResultSchema).optional(),
  teamHits: z.number().optional(),
  teamErrors: z.number().optional(),
});

export const BaseballGameRecordSchema = z.object({
  label: z.string(),
  home: z.union([z.number(), z.string()]),
  away: z.union([z.number(), z.string()]),
});

export const BaseballHeadToHeadSchema = z.object({
  totalGames: z.number(),
  homeWins: z.number(),
  awayWins: z.number(),
  draws: z.number(),
});

export const GameStatusSchema = z.enum(['예정', '진행중', '종료']);

export const BaseballGameDataSchema = z.object({
  sportType: z.literal('baseball'),
  league: z.string(),
  date: z.string(),
  time: z.string().optional(),
  status: GameStatusSchema,
  venue: z.string().optional(),
  homeTeam: BaseballTeamInfoSchema,
  awayTeam: BaseballTeamInfoSchema,
  homeStarterName: z.string().optional(),
  awayStarterName: z.string().optional(),
  gameRecords: z.array(BaseballGameRecordSchema).optional(),
  headToHead: BaseballHeadToHeadSchema.optional(),
});
