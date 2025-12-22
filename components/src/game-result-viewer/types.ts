import { z } from 'zod';

// ===== 공통 타입 =====

// 지원하는 스포츠 종목
export type SportType = 'basketball' | 'soccer' | 'baseball' | 'volleyball';

// 경기 상태
export type GameStatus = '예정' | '진행중' | '종료';

// 공통 게임 데이터 인터페이스
export interface BaseGameData {
  sportType: SportType;
  league: string;
  date: string;
  status: GameStatus;
}

// 공통 Zod 스키마
export const SportTypeSchema = z.enum(['basketball', 'soccer', 'baseball', 'volleyball']);
export const GameStatusSchema = z.enum(['예정', '진행중', '종료']);

export const BaseGameDataSchema = z.object({
  sportType: SportTypeSchema,
  league: z.string(),
  date: z.string(),
  status: GameStatusSchema,
});

// 전체 게임 데이터 유니온 타입 (각 스포츠별 타입 import 후 확장)
// 각 스포츠별 세부 타입은 sports/[sport]/types.ts에서 정의
