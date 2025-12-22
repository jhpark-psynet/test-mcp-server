import { z } from 'zod';

// 지원하는 축구 리그
export type SoccerLeague =
  | 'K리그1' | 'K리그2'                    // 한국
  | 'EPL' | '라리가' | '분데스리가' | '세리에A' | '리그앙'  // 유럽 5대 리그
  | 'UEFA챔피언스리그' | 'UEFA유로파리그'  // UEFA
  | 'AFC챔피언스리그'                      // 아시아
  | '월드컵' | '아시안컵';                 // 국가대항전

// 경기 상태
export type GameStatus = '경기전' | '경기중' | '하프타임' | '경기종료';

// 경기 진행 상황 (경기중일 때)
export type SoccerPeriod = '전반' | '후반' | '연장전반' | '연장후반' | '승부차기';

// 최근 경기 결과 (무승부 포함)
export type RecentGameResult = 'W' | 'D' | 'L';

// 전/후반 점수
export interface HalfScores {
  firstHalf: number;
  secondHalf: number;
  extraFirstHalf?: number;   // 연장 전반
  extraSecondHalf?: number;  // 연장 후반
  penalties?: number;        // 승부차기
}

// 골 이벤트
export interface GoalEvent {
  minute: number;            // 득점 시간 (예: 45)
  addedTime?: number;        // 추가시간 (예: 3 -> "45+3'")
  scorer: string;            // 득점자 이름
  assist?: string;           // 어시스트 (선택)
  team: 'home' | 'away';     // 득점 팀
  isPenalty?: boolean;       // PK 여부
  isOwnGoal?: boolean;       // 자책골 여부
}

// 축구 선수 스탯
export interface SoccerPlayerStats {
  number: number;            // 등번호
  name: string;              // 이름
  position: string;          // GK, DF, MF, FW
  minutes: number;           // 출전 시간
  goals: number;             // 골
  assists: number;           // 어시스트
  shots: number;             // 슈팅
  shotsOnTarget: number;     // 유효 슈팅
  passes: number;            // 패스
  passAccuracy?: string;     // 패스 성공률
  tackles: number;           // 태클
  interceptions: number;     // 인터셉트
  fouls: number;             // 파울
  yellowCards: number;       // 옐로카드
  redCards: number;          // 레드카드
  saves?: number;            // 세이브 (GK용)
}

// 팀 정보
export interface SoccerTeamInfo {
  name: string;
  shortName: string;
  logo: string;
  record: string;            // "15승 5무 3패"
  score: number;             // 총 골 수
  halfScores?: HalfScores;
  players: SoccerPlayerStats[];
  recentGames?: RecentGameResult[];
  primaryColor: string;
  secondaryColor: string;
}

// 팀 기록 비교
export interface SoccerGameRecord {
  label: string;
  home: number | string;
  away: number | string;
}

// 맞대결 기록
export interface HeadToHeadRecord {
  totalGames: number;
  homeWins: number;
  awayWins: number;
  draws: number;             // 무승부 추가
  recentMatches?: Array<{
    date: string;
    homeScore: number;
    awayScore: number;
    winner: 'home' | 'away' | 'draw';
  }>;
}

// 순위표 팀
export interface StandingsTeam {
  rank: number;
  name: string;
  shortName: string;
  played: number;            // 경기 수
  wins: number;
  draws: number;             // 무승부
  losses: number;
  goalsFor: number;          // 득점
  goalsAgainst: number;      // 실점
  goalDifference: number;    // 골득실
  points: number;            // 승점
  recentGames: RecentGameResult[];
}

// 리그 순위
export interface LeagueStandings {
  teams: StandingsTeam[];
}

// 메인 게임 데이터
export interface SoccerGameData {
  sportType: 'soccer';
  league: SoccerLeague;
  date: string;
  time?: string;
  status: GameStatus;
  currentPeriod?: SoccerPeriod;    // 경기중일 때 현재 기간
  currentMinute?: number;          // 현재 경기 시간 (예: 67)
  addedTime?: number;              // 추가시간 (예: 3)
  homeTeam: SoccerTeamInfo;
  awayTeam: SoccerTeamInfo;
  goals?: GoalEvent[];             // 골 이벤트 타임라인
  gameRecords?: SoccerGameRecord[];
  headToHead?: HeadToHeadRecord;
  standings?: LeagueStandings[];
}

// ============ Zod Schemas ============

export const RecentGameResultSchema = z.enum(['W', 'D', 'L']);

export const HalfScoresSchema = z.object({
  firstHalf: z.number(),
  secondHalf: z.number(),
  extraFirstHalf: z.number().optional(),
  extraSecondHalf: z.number().optional(),
  penalties: z.number().optional(),
});

export const GoalEventSchema = z.object({
  minute: z.number(),
  addedTime: z.number().optional(),
  scorer: z.string(),
  assist: z.string().optional(),
  team: z.enum(['home', 'away']),
  isPenalty: z.boolean().optional(),
  isOwnGoal: z.boolean().optional(),
});

export const SoccerPlayerStatsSchema = z.object({
  number: z.number(),
  name: z.string(),
  position: z.string(),
  minutes: z.number(),
  goals: z.number(),
  assists: z.number(),
  shots: z.number(),
  shotsOnTarget: z.number(),
  passes: z.number(),
  passAccuracy: z.string().optional(),
  tackles: z.number(),
  interceptions: z.number(),
  fouls: z.number(),
  yellowCards: z.number(),
  redCards: z.number(),
  saves: z.number().optional(),
});

export const SoccerTeamInfoSchema = z.object({
  name: z.string(),
  shortName: z.string(),
  logo: z.string(),
  record: z.string(),
  score: z.number(),
  halfScores: HalfScoresSchema.optional(),
  players: z.array(SoccerPlayerStatsSchema),
  recentGames: z.array(RecentGameResultSchema).optional(),
  primaryColor: z.string(),
  secondaryColor: z.string(),
});

export const SoccerGameRecordSchema = z.object({
  label: z.string(),
  home: z.union([z.number(), z.string()]),
  away: z.union([z.number(), z.string()]),
});

export const HeadToHeadRecordSchema = z.object({
  totalGames: z.number(),
  homeWins: z.number(),
  awayWins: z.number(),
  draws: z.number(),
  recentMatches: z.array(z.object({
    date: z.string(),
    homeScore: z.number(),
    awayScore: z.number(),
    winner: z.enum(['home', 'away', 'draw']),
  })).optional(),
});

export const StandingsTeamSchema = z.object({
  rank: z.number(),
  name: z.string(),
  shortName: z.string(),
  played: z.number(),
  wins: z.number(),
  draws: z.number(),
  losses: z.number(),
  goalsFor: z.number(),
  goalsAgainst: z.number(),
  goalDifference: z.number(),
  points: z.number(),
  recentGames: z.array(RecentGameResultSchema),
});

export const LeagueStandingsSchema = z.object({
  teams: z.array(StandingsTeamSchema),
});

export const GameStatusSchema = z.enum(['경기전', '경기중', '하프타임', '경기종료']);

export const SoccerPeriodSchema = z.enum(['전반', '후반', '연장전반', '연장후반', '승부차기']);

export const SoccerLeagueSchema = z.enum([
  'K리그1', 'K리그2',
  'EPL', '라리가', '분데스리가', '세리에A', '리그앙',
  'UEFA챔피언스리그', 'UEFA유로파리그',
  'AFC챔피언스리그',
  '월드컵', '아시안컵',
]);

export const SoccerGameDataSchema = z.object({
  sportType: z.literal('soccer'),
  league: SoccerLeagueSchema,
  date: z.string(),
  time: z.string().optional(),
  status: GameStatusSchema,
  currentPeriod: SoccerPeriodSchema.optional(),
  currentMinute: z.number().optional(),
  addedTime: z.number().optional(),
  homeTeam: SoccerTeamInfoSchema,
  awayTeam: SoccerTeamInfoSchema,
  goals: z.array(GoalEventSchema).optional(),
  gameRecords: z.array(SoccerGameRecordSchema).optional(),
  headToHead: HeadToHeadRecordSchema.optional(),
  standings: z.array(LeagueStandingsSchema).optional(),
});
