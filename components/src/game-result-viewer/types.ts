import { z } from 'zod';

// League type
export type LeagueType = 'NBA' | 'KBL' | 'WKBL';

// Game status
export type GameStatus = '예정' | '진행중' | '종료';

// Player stats
export interface PlayerStats {
  number: number;      // Jersey number
  name: string;        // Player name
  position: string;    // Position (G, F, C, etc.)
  minutes: number;     // Minutes played
  rebounds: number;    // Rebounds
  assists: number;     // Assists
  points: number;      // Points
}

// Team info
export interface TeamInfo {
  name: string;        // Full team name
  shortName: string;   // Short team name (displayed in tab)
  logo: string;        // Logo URL (empty string shows placeholder)
  record: string;      // Season record (e.g., "9승 6패")
  score: number;       // Game score
  players: PlayerStats[]; // Player stats array
}

// Game record (team comparison stats)
export interface GameRecord {
  label: string;           // Item name (Field Goals, Rebounds, etc.)
  home: number | string;   // Home team value
  away: number | string;   // Away team value
}

// Full game data
export interface GameData {
  league: LeagueType;      // League
  date: string;            // Game date (e.g., "11.17 (월)")
  status: GameStatus;      // Game status
  homeTeam: TeamInfo;      // Home team info
  awayTeam: TeamInfo;      // Away team info
  gameRecords?: GameRecord[]; // Game records (optional)
}

// Zod schemas for validation
export const PlayerStatsSchema = z.object({
  number: z.number(),
  name: z.string(),
  position: z.string(),
  minutes: z.number(),
  rebounds: z.number(),
  assists: z.number(),
  points: z.number(),
});

export const TeamInfoSchema = z.object({
  name: z.string(),
  shortName: z.string(),
  logo: z.string(),
  record: z.string(),
  score: z.number(),
  players: z.array(PlayerStatsSchema),
});

export const GameRecordSchema = z.object({
  label: z.string(),
  home: z.union([z.number(), z.string()]),
  away: z.union([z.number(), z.string()]),
});

export const GameDataSchema = z.object({
  league: z.enum(['NBA', 'KBL', 'WKBL']),
  date: z.string(),
  status: z.enum(['예정', '진행중', '종료']),
  homeTeam: TeamInfoSchema,
  awayTeam: TeamInfoSchema,
  gameRecords: z.array(GameRecordSchema).optional(),
});

// Raw API response types from get_game_details
export const ApiGameDetailsSchema = z.object({
  game_id: z.string(),
  game_info: z.object({
    league: z.string(),
    home_team: z.string(),
    away_team: z.string(),
    home_score: z.number(),
    away_score: z.number(),
    arena: z.string(),
    date: z.string(),
    time: z.string(),
  }),
  team_stats: z.array(z.record(z.any())),
  player_stats: z.array(z.record(z.any())),
});

export type ApiGameDetails = z.infer<typeof ApiGameDetailsSchema>;
