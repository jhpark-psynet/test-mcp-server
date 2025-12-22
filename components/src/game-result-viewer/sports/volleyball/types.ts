import { z } from 'zod';

// 지원하는 배구 리그
export type VolleyballLeague = 'V리그남자' | 'V리그여자' | 'VNL남자' | 'VNL여자';

// 경기 상태
export type GameStatus = '경기전' | '경기중' | '경기종료';

// 최근 경기 결과
export type RecentGameResult = 'W' | 'L';

// 세트별 점수
export interface SetScores {
  set1: number;
  set2: number;
  set3: number;
  set4?: number;
  set5?: number;
}

// 배구 선수 스탯
export interface VolleyballPlayerStats {
  number: number;           // 등번호
  name: string;             // 이름
  position: string;         // S, OH, MB, OP, L
  sets: number;             // 출전 세트 수
  points: number;           // 총 득점
  attacks: number;          // 공격 시도
  kills: number;            // 공격 성공
  attackPct?: string;       // 공격 성공률
  blocks: number;           // 블로킹
  aces: number;             // 서브 에이스
  digs: number;             // 디그
  assists?: number;         // 어시스트 (세터용)
}

// 팀 정보
export interface VolleyballTeamInfo {
  name: string;
  shortName: string;
  logo: string;
  record: string;           // "25승 11패"
  setsWon: number;          // 획득 세트 수 (0-3)
  setScores?: SetScores;
  players: VolleyballPlayerStats[];
  recentGames?: RecentGameResult[];
  // 동적 팀 컬러
  primaryColor: string;     // 예: "#003DA5"
  secondaryColor: string;   // 예: "#FFD700"
}

// 팀 기록 비교
export interface VolleyballGameRecord {
  label: string;
  home: number | string;
  away: number | string;
}

// 맞대결 기록
export interface HeadToHeadRecord {
  totalGames: number;
  homeWins: number;
  awayWins: number;
  recentMatches?: Array<{
    date: string;
    homeSets: number;
    awaySets: number;
    winner: 'home' | 'away';
  }>;
}

// 순위표 팀
export interface StandingsTeam {
  rank: number;
  name: string;
  shortName: string;
  wins: number;
  losses: number;
  winRate: string;
  recentGames: RecentGameResult[];
}

// 리그 순위
export interface LeagueStandings {
  teams: StandingsTeam[];
}

// 메인 게임 데이터
export interface VolleyballGameData {
  sportType: 'volleyball';
  league: VolleyballLeague;
  date: string;
  time?: string;
  status: GameStatus;
  currentSet?: number;      // 경기중일 때 현재 세트
  homeTeam: VolleyballTeamInfo;
  awayTeam: VolleyballTeamInfo;
  gameRecords?: VolleyballGameRecord[];
  headToHead?: HeadToHeadRecord;
  standings?: LeagueStandings[];
}

// ============ Zod Schemas ============

export const RecentGameResultSchema = z.enum(['W', 'L']);

export const SetScoresSchema = z.object({
  set1: z.number(),
  set2: z.number(),
  set3: z.number(),
  set4: z.number().optional(),
  set5: z.number().optional(),
});

export const VolleyballPlayerStatsSchema = z.object({
  number: z.number(),
  name: z.string(),
  position: z.string(),
  sets: z.number(),
  points: z.number(),
  attacks: z.number(),
  kills: z.number(),
  attackPct: z.string().optional(),
  blocks: z.number(),
  aces: z.number(),
  digs: z.number(),
  assists: z.number().optional(),
});

export const VolleyballTeamInfoSchema = z.object({
  name: z.string(),
  shortName: z.string(),
  logo: z.string(),
  record: z.string(),
  setsWon: z.number(),
  setScores: SetScoresSchema.optional(),
  players: z.array(VolleyballPlayerStatsSchema),
  recentGames: z.array(RecentGameResultSchema).optional(),
  primaryColor: z.string(),
  secondaryColor: z.string(),
});

export const VolleyballGameRecordSchema = z.object({
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
    homeSets: z.number(),
    awaySets: z.number(),
    winner: z.enum(['home', 'away']),
  })).optional(),
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
  teams: z.array(StandingsTeamSchema),
});

export const GameStatusSchema = z.enum(['경기전', '경기중', '경기종료']);

export const VolleyballLeagueSchema = z.enum(['V리그남자', 'V리그여자', 'VNL남자', 'VNL여자']);

export const VolleyballGameDataSchema = z.object({
  sportType: z.literal('volleyball'),
  league: VolleyballLeagueSchema,
  date: z.string(),
  time: z.string().optional(),
  status: GameStatusSchema,
  currentSet: z.number().optional(),
  homeTeam: VolleyballTeamInfoSchema,
  awayTeam: VolleyballTeamInfoSchema,
  gameRecords: z.array(VolleyballGameRecordSchema).optional(),
  headToHead: HeadToHeadRecordSchema.optional(),
  standings: z.array(LeagueStandingsSchema).optional(),
});
