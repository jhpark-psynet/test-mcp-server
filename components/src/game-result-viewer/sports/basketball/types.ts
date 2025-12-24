import { z } from 'zod';

// 농구 리그 타입
export type BasketballLeague = 'NBA' | 'KBL' | 'WKBL';

// 경기 상태 (서버 반환 값에 맞춤)
export type GameStatus = '예정' | '진행중' | '종료';

// 컨퍼런스 (NBA)
export type Conference = '동부' | '서부';

// 최근 경기 결과
export type RecentGameResult = 'W' | 'L';

// 라인업 포지션 (선발: 21-25, 벤치: 5)
export type LineupPosition = 'C' | 'PF' | 'SF' | 'PG' | 'SG' | 'BENCH';

// 라인업 선수 정보
export interface LineupPlayer {
  playerId: string;        // 선수 ID
  name: string;            // 선수명
  number: number;          // 등번호
  position: LineupPosition; // 포지션
  isStarter: boolean;      // 선발 여부
}

// 선수 스탯
export interface BasketballPlayerStats {
  number: number;        // 등번호
  name: string;          // 선수명
  position: string;      // 포지션 (G, F, C 등)
  minutes: number;       // 출전 시간
  rebounds: number;      // 리바운드
  assists: number;       // 어시스트
  points: number;        // 득점
  fgm?: number;          // 필드골 성공
  fga?: number;          // 필드골 시도
  tpm?: number;          // 3점슛 성공
  tpa?: number;          // 3점슛 시도
  steals?: number;       // 스틸
  blocks?: number;       // 블록
}

// 쿼터별 점수
export interface QuarterScores {
  q1: number;
  q2: number;
  q3: number;
  q4: number;
  ot?: number[];  // 연장전 (여러 번 가능)
}

// 팀 정보
export interface BasketballTeamInfo {
  name: string;           // 팀 전체 이름
  shortName: string;      // 짧은 이름 (탭에 표시)
  logo: string;           // 로고 URL (빈 문자열이면 플레이스홀더)
  record: string;         // 시즌 기록 (예: "15승 3패")
  score: number;          // 경기 점수
  quarterScores?: QuarterScores;  // 쿼터별 점수
  players: BasketballPlayerStats[];
  recentGames?: RecentGameResult[];  // 최근 5경기 결과
  lineup?: LineupPlayer[];  // 라인업 (선발 + 벤치)
}

// 경기 기록 (팀 비교 스탯)
export interface BasketballGameRecord {
  label: string;           // 항목명 (필드골, 리바운드 등)
  home: number | string;   // 홈팀 값
  away: number | string;   // 원정팀 값
}

// 맞대결 기록
export interface HeadToHeadRecord {
  totalGames: number;      // 총 경기 수
  homeWins: number;        // 홈팀 승리
  awayWins: number;        // 원정팀 승리
  recentMatches?: {        // 최근 맞대결
    date: string;
    homeScore: number;
    awayScore: number;
    winner: 'home' | 'away';
  }[];
}

// 팀별 시즌 통계 (vs API에서 제공)
export interface TeamSeasonStats {
  winRate: string;           // 승률 (0.741)
  avgPoints: number;         // 평균 득점
  avgPointsAgainst: number;  // 평균 실점
  fgPct: string;             // FG%
  threePct: string;          // 3P%
  avgRebounds: number;       // 평균 리바운드
  avgAssists: number;        // 평균 어시스트
  avgSteals?: number;        // 평균 스틸
  avgBlocks?: number;        // 평균 블록
  avgTurnovers?: number;     // 평균 턴오버
}

// 양팀 비교 데이터
export interface TeamComparisonData {
  home: TeamSeasonStats;
  away: TeamSeasonStats;
}

// 리그 순위 팀 정보
export interface StandingsTeam {
  rank: number;            // 순위
  name: string;            // 팀명
  shortName: string;       // 짧은 팀명
  wins: number;            // 승
  losses: number;          // 패
  winRate: string;         // 승률
  recentGames: RecentGameResult[];  // 최근 5경기
}

// 리그 순위
export interface LeagueStandings {
  conference?: Conference;  // 컨퍼런스 (NBA용)
  teams: StandingsTeam[];
}

// 농구 경기 데이터
export interface BasketballGameData {
  sportType: 'basketball';
  league: BasketballLeague;
  date: string;             // 경기 날짜
  time?: string;            // 경기 시간 (경기전일 때)
  status: GameStatus;
  venue?: string;           // 경기장 이름
  homeTeam: BasketballTeamInfo;
  awayTeam: BasketballTeamInfo;
  gameRecords?: BasketballGameRecord[];   // 팀 스탯 비교
  headToHead?: HeadToHeadRecord;          // 맞대결 기록
  standings?: LeagueStandings[];          // 리그 순위 (동부/서부)
  teamComparison?: TeamComparisonData;    // 양팀 시즌 통계 비교
}

// ===== Zod 스키마 =====

export const RecentGameResultSchema = z.enum(['W', 'L']);

export const LineupPositionSchema = z.enum(['C', 'PF', 'SF', 'PG', 'SG', 'BENCH']);

export const LineupPlayerSchema = z.object({
  playerId: z.string(),
  name: z.string(),
  number: z.number(),
  position: LineupPositionSchema,
  isStarter: z.boolean(),
});

export const QuarterScoresSchema = z.object({
  q1: z.number(),
  q2: z.number(),
  q3: z.number(),
  q4: z.number(),
  ot: z.array(z.number()).optional(),
});

export const BasketballPlayerStatsSchema = z.object({
  number: z.number(),
  name: z.string(),
  position: z.string(),
  minutes: z.number(),
  rebounds: z.number(),
  assists: z.number(),
  points: z.number(),
  fgm: z.number().optional(),
  fga: z.number().optional(),
  tpm: z.number().optional(),
  tpa: z.number().optional(),
  steals: z.number().optional(),
  blocks: z.number().optional(),
});

export const BasketballTeamInfoSchema = z.object({
  name: z.string(),
  shortName: z.string(),
  logo: z.string(),
  record: z.string(),
  score: z.number(),
  quarterScores: QuarterScoresSchema.optional(),
  players: z.array(BasketballPlayerStatsSchema),
  recentGames: z.array(RecentGameResultSchema).optional(),
  lineup: z.array(LineupPlayerSchema).optional(),
});

export const BasketballGameRecordSchema = z.object({
  label: z.string(),
  home: z.union([z.number(), z.string()]),
  away: z.union([z.number(), z.string()]),
});

export const HeadToHeadRecordSchema = z.object({
  totalGames: z.number(),
  homeWins: z.number(),
  awayWins: z.number(),
  recentMatches: z.array(z.object({
    date: z.string(),
    homeScore: z.number(),
    awayScore: z.number(),
    winner: z.enum(['home', 'away']),
  })).optional(),
});

export const TeamSeasonStatsSchema = z.object({
  winRate: z.string(),
  avgPoints: z.number(),
  avgPointsAgainst: z.number(),
  fgPct: z.string(),
  threePct: z.string(),
  avgRebounds: z.number(),
  avgAssists: z.number(),
  avgSteals: z.number().optional(),
  avgBlocks: z.number().optional(),
  avgTurnovers: z.number().optional(),
});

export const TeamComparisonDataSchema = z.object({
  home: TeamSeasonStatsSchema,
  away: TeamSeasonStatsSchema,
});

export const StandingsTeamSchema = z.object({
  rank: z.number(),
  name: z.string(),
  shortName: z.string(),
  wins: z.number(),
  losses: z.number(),
  winRate: z.string(),
  recentGames: z.array(RecentGameResultSchema),
});

export const LeagueStandingsSchema = z.object({
  conference: z.enum(['동부', '서부']).optional(),
  teams: z.array(StandingsTeamSchema),
});

export const GameStatusSchema = z.enum(['예정', '진행중', '종료']);

export const BasketballGameDataSchema = z.object({
  sportType: z.literal('basketball'),
  league: z.enum(['NBA', 'KBL', 'WKBL']),
  date: z.string(),
  time: z.string().optional(),
  status: GameStatusSchema,
  venue: z.string().optional(),
  homeTeam: BasketballTeamInfoSchema,
  awayTeam: BasketballTeamInfoSchema,
  gameRecords: z.array(BasketballGameRecordSchema).optional(),
  headToHead: HeadToHeadRecordSchema.optional(),
  standings: z.array(LeagueStandingsSchema).optional(),
  teamComparison: TeamComparisonDataSchema.optional(),
});
