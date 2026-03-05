import type { BasketballGameData } from './sports/basketball/types';
import type { BaseballGameData } from './sports/baseball/types';
import type { SoccerGameData } from './sports/soccer/types';
import type { VolleyballGameData } from './sports/volleyball/types';
import { mockBaseballFinishedData } from './sports/baseball/mockData';

// ============================================================
// BASKETBALL
// ============================================================

// 경기 예정 목 데이터 (teamComparison 포함)
export const mockBasketballData: BasketballGameData = {
  sportType: 'basketball',
  league: 'NBA',
  date: '12.24',
  time: '11:00',
  status: '예정',
  venue: 'Chase Center',
  homeTeam: {
    name: '골든스테이트 워리어스',
    shortName: '골든스테이트',
    logo: 'https://lscdn.psynet.co.kr/livescore/photo/spt/livescore/emb_new/emblem_mid_OT31260.png',
    record: '20승 7패',
    score: 0,
    players: [],
    recentGames: ['W', 'W', 'L', 'W', 'W'],
  },
  awayTeam: {
    name: '로스앤젤레스 레이커스',
    shortName: 'LA레이커스',
    logo: 'https://lscdn.psynet.co.kr/livescore/photo/spt/livescore/emb_new/emblem_mid_OT31254.png',
    record: '18승 9패',
    score: 0,
    players: [],
    recentGames: ['L', 'W', 'W', 'L', 'W'],
  },
  teamComparison: {
    home: {
      winRate: '0.741',
      avgPoints: 118.5,
      avgPointsAgainst: 108.2,
      fgPct: '0.482',
      threePct: '0.378',
      avgRebounds: 45.3,
      avgAssists: 28.1,
      avgSteals: 8.2,
      avgBlocks: 5.4,
      avgTurnovers: 13.1,
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
  },
  standings: [
    {
      conference: '서부',
      teams: [
        { rank: 1, name: '오클라호마시티', shortName: 'OKC', wins: 22, losses: 5, winRate: '0.815', recentGames: ['W', 'W', 'W', 'W', 'L'] },
        { rank: 2, name: '골든스테이트', shortName: 'GSW', wins: 20, losses: 7, winRate: '0.741', recentGames: ['W', 'W', 'L', 'W', 'W'] },
        { rank: 3, name: 'LA레이커스', shortName: 'LAL', wins: 18, losses: 9, winRate: '0.667', recentGames: ['L', 'W', 'W', 'L', 'W'] },
        { rank: 4, name: '휴스턴', shortName: 'HOU', wins: 17, losses: 10, winRate: '0.630', recentGames: ['W', 'L', 'W', 'W', 'L'] },
        { rank: 5, name: '덴버', shortName: 'DEN', wins: 16, losses: 10, winRate: '0.615', recentGames: ['W', 'W', 'L', 'L', 'W'] },
      ],
    },
  ],
};

// 경기 진행중 목 데이터 (3쿼터 진행중)
export const mockBasketballLiveData: BasketballGameData = {
  sportType: 'basketball',
  league: 'NBA',
  date: '12.24',
  status: '진행중',
  venue: 'Chase Center',
  homeTeam: {
    name: '골든스테이트 워리어스',
    shortName: '골든스테이트',
    logo: 'https://lscdn.psynet.co.kr/livescore/photo/spt/livescore/emb_new/emblem_mid_OT31260.png',
    record: '20승 7패',
    score: 78,
    quarterScores: { q1: 28, q2: 25, q3: 25, q4: 0 },
    players: [
      { number: 30, name: 'Stephen Curry', position: 'G', minutes: 27, rebounds: 3, assists: 5, points: 26, fgm: 8, fga: 17, tpm: 4, tpa: 9 },
      { number: 11, name: 'Klay Thompson', position: 'G', minutes: 22, rebounds: 2, assists: 1, points: 16, fgm: 5, fga: 11, tpm: 3, tpa: 6 },
      { number: 23, name: 'Draymond Green', position: 'F', minutes: 24, rebounds: 6, assists: 7, points: 5, fgm: 2, fga: 5, tpm: 0, tpa: 1 },
      { number: 5, name: 'Jonathan Kuminga', position: 'F', minutes: 19, rebounds: 4, assists: 2, points: 18, fgm: 7, fga: 12, tpm: 1, tpa: 3 },
      { number: 15, name: 'Kevon Looney', position: 'C', minutes: 16, rebounds: 7, assists: 1, points: 4, fgm: 2, fga: 3, tpm: 0, tpa: 0 },
    ],
    recentGames: ['W', 'W', 'L', 'W', 'W'],
  },
  awayTeam: {
    name: '로스앤젤레스 레이커스',
    shortName: 'LA레이커스',
    logo: 'https://lscdn.psynet.co.kr/livescore/photo/spt/livescore/emb_new/emblem_mid_OT31254.png',
    record: '18승 9패',
    score: 72,
    quarterScores: { q1: 22, q2: 28, q3: 22, q4: 0 },
    players: [
      { number: 23, name: 'LeBron James', position: 'F', minutes: 28, rebounds: 7, assists: 8, points: 22, fgm: 8, fga: 16, tpm: 1, tpa: 4 },
      { number: 3, name: 'Anthony Davis', position: 'C', minutes: 26, rebounds: 10, assists: 2, points: 20, fgm: 7, fga: 14, tpm: 0, tpa: 1 },
      { number: 15, name: 'Austin Reaves', position: 'G', minutes: 22, rebounds: 2, assists: 4, points: 13, fgm: 4, fga: 9, tpm: 2, tpa: 5 },
      { number: 1, name: "D'Angelo Russell", position: 'G', minutes: 20, rebounds: 1, assists: 5, points: 9, fgm: 3, fga: 8, tpm: 1, tpa: 3 },
      { number: 12, name: 'Rui Hachimura', position: 'F', minutes: 18, rebounds: 3, assists: 1, points: 5, fgm: 2, fga: 5, tpm: 0, tpa: 1 },
    ],
    recentGames: ['L', 'W', 'W', 'L', 'W'],
  },
  gameRecords: [
    { label: '필드골', home: '24/52', away: '23/56' },
    { label: '3점슛', home: '8/20', away: '4/14' },
    { label: '자유투', home: '6/8', away: '10/12' },
    { label: '리바운드', home: 29, away: 33 },
    { label: '어시스트', home: 18, away: 20 },
    { label: '턴오버', home: 7, away: 9 },
  ],
};

// 경기 종료 목 데이터 (기존)
export const mockFinishedBasketballData: BasketballGameData = {
  sportType: 'basketball',
  league: 'NBA',
  date: '2024-12-18',
  status: '종료',
  homeTeam: {
    name: 'Los Angeles Lakers',
    shortName: 'LAL',
    logo: '',
    record: '15승 8패',
    score: 112,
    quarterScores: { q1: 28, q2: 22, q3: 25, q4: 37 },
    recentGames: ['W', 'W', 'L', 'W', 'L'],
    players: [
      { number: 23, name: 'LeBron James', position: 'F', minutes: 32, rebounds: 8, assists: 9, points: 28 },
      { number: 3, name: 'Anthony Davis', position: 'C', minutes: 30, rebounds: 12, assists: 3, points: 24 },
      { number: 15, name: 'Austin Reaves', position: 'G', minutes: 28, rebounds: 3, assists: 5, points: 15 },
      { number: 1, name: "D'Angelo Russell", position: 'G', minutes: 26, rebounds: 2, assists: 7, points: 12 },
      { number: 12, name: 'Rui Hachimura', position: 'F', minutes: 22, rebounds: 4, assists: 1, points: 8 },
    ],
  },
  awayTeam: {
    name: 'Golden State Warriors',
    shortName: 'GSW',
    logo: '',
    record: '12승 11패',
    score: 105,
    quarterScores: { q1: 25, q2: 20, q3: 22, q4: 38 },
    recentGames: ['L', 'W', 'W', 'L', 'L'],
    players: [
      { number: 30, name: 'Stephen Curry', position: 'G', minutes: 34, rebounds: 5, assists: 6, points: 32 },
      { number: 22, name: 'Andrew Wiggins', position: 'F', minutes: 30, rebounds: 6, assists: 2, points: 18 },
      { number: 23, name: 'Draymond Green', position: 'F', minutes: 28, rebounds: 7, assists: 8, points: 8 },
      { number: 11, name: 'Klay Thompson', position: 'G', minutes: 26, rebounds: 2, assists: 2, points: 14 },
      { number: 5, name: 'Kevon Looney', position: 'C', minutes: 20, rebounds: 9, assists: 2, points: 6 },
    ],
  },
  gameRecords: [
    { label: '필드골', home: '38/82', away: '35/78' },
    { label: '3점슛', home: '12/30', away: '14/35' },
    { label: '자유투', home: '15/18', away: '12/15' },
    { label: '리바운드', home: 42, away: 38 },
    { label: '어시스트', home: 25, away: 22 },
    { label: '턴오버', home: 10, away: 12 },
  ],
};

// ============================================================
// BASEBALL
// ============================================================

// 야구 경기전 목 데이터
export const mockBaseballBeforeData: BaseballGameData = {
  sportType: 'baseball',
  league: 'KBO리그',
  date: '05.10',
  time: '18:30',
  status: '예정',
  venue: '잠실야구장',
  homeStarterName: '고영표',
  awayStarterName: '안우진',
  homeTeam: {
    name: 'LG',
    shortName: 'LG',
    logo: '',
    score: 0,
    record: '22승 10패',
    recentGames: ['W', 'W', 'W', 'L', 'W'],
    inningScores: [],
    batters: [],
    pitchers: [],
  },
  awayTeam: {
    name: 'KIA',
    shortName: 'KIA',
    logo: '',
    score: 0,
    record: '20승 12패',
    recentGames: ['W', 'L', 'W', 'W', 'L'],
    inningScores: [],
    batters: [],
    pitchers: [],
  },
  headToHead: {
    totalGames: 10,
    homeWins: 6,
    awayWins: 4,
    draws: 0,
  },
};

// 야구 진행중 목 데이터 (5이닝까지 진행)
export const mockBaseballLiveData: BaseballGameData = {
  sportType: 'baseball',
  league: 'KBO리그',
  date: '05.10',
  time: '18:30',
  status: '진행중',
  venue: '잠실야구장',
  homeStarterName: '고영표',
  awayStarterName: '안우진',
  homeTeam: {
    name: 'LG',
    shortName: 'LG',
    logo: '',
    score: 3,
    record: '22승 10패',
    recentGames: ['W', 'W', 'W', 'L', 'W'],
    teamHits: 7,
    teamErrors: 0,
    inningScores: [
      { inning: 1, homeScore: '1', awayScore: '0' },
      { inning: 2, homeScore: '0', awayScore: '2' },
      { inning: 3, homeScore: '0', awayScore: '0' },
      { inning: 4, homeScore: '2', awayScore: '0' },
      { inning: 5, homeScore: '-', awayScore: '-' },
    ],
    batters: [
      { batOrder: 1, name: '홍창기', position: 'LF', atBats: 2, hits: 1, homeRuns: 0, rbi: 0, walks: 0, strikeouts: 0, avg: '.310', obp: '.380', ops: '.830' },
      { batOrder: 2, name: '오지환', position: 'SS', atBats: 2, hits: 2, homeRuns: 0, rbi: 1, walks: 0, strikeouts: 0, avg: '.295', obp: '.365', ops: '.820' },
      { batOrder: 3, name: '김현수', position: 'DH', atBats: 2, hits: 1, homeRuns: 1, rbi: 2, walks: 0, strikeouts: 1, avg: '.302', obp: '.375', ops: '.920' },
      { batOrder: 4, name: '박해민', position: 'CF', atBats: 2, hits: 1, homeRuns: 0, rbi: 0, walks: 0, strikeouts: 0, avg: '.278', obp: '.340', ops: '.760' },
      { batOrder: 5, name: '문보경', position: '3B', atBats: 2, hits: 1, homeRuns: 0, rbi: 0, walks: 0, strikeouts: 1, avg: '.255', obp: '.320', ops: '.720' },
      { batOrder: 6, name: '박동원', position: 'C', atBats: 2, hits: 0, homeRuns: 0, rbi: 0, walks: 1, strikeouts: 0, avg: '.245', obp: '.325', ops: '.695' },
      { batOrder: 7, name: '문성주', position: 'RF', atBats: 2, hits: 1, homeRuns: 0, rbi: 0, walks: 0, strikeouts: 0, avg: '.260', obp: '.318', ops: '.715' },
      { batOrder: 8, name: '신민재', position: '2B', atBats: 2, hits: 0, homeRuns: 0, rbi: 0, walks: 0, strikeouts: 1, avg: '.235', obp: '.290', ops: '.660' },
      { batOrder: 9, name: '김범석', position: '1B', atBats: 2, hits: 0, homeRuns: 0, rbi: 0, walks: 0, strikeouts: 1, avg: '.218', obp: '.275', ops: '.610' },
    ],
    pitchers: [
      { turnNo: 1, name: '고영표', result: '', innings: '4.0', pitchCount: 68, hits: 4, strikeouts: 5, runs: 2, earnedRuns: 2, era: '3.24', whip: '1.18' },
    ],
  },
  awayTeam: {
    name: 'KIA',
    shortName: 'KIA',
    logo: '',
    score: 2,
    record: '20승 12패',
    recentGames: ['W', 'L', 'W', 'W', 'L'],
    teamHits: 4,
    teamErrors: 0,
    inningScores: [
      { inning: 1, homeScore: '1', awayScore: '0' },
      { inning: 2, homeScore: '0', awayScore: '2' },
      { inning: 3, homeScore: '0', awayScore: '0' },
      { inning: 4, homeScore: '2', awayScore: '0' },
      { inning: 5, homeScore: '-', awayScore: '-' },
    ],
    batters: [
      { batOrder: 1, name: '박찬호', position: 'SS', atBats: 2, hits: 1, homeRuns: 0, rbi: 1, walks: 0, strikeouts: 0, avg: '.288', obp: '.350', ops: '.790' },
      { batOrder: 2, name: '소크라테스', position: 'LF', atBats: 2, hits: 1, homeRuns: 0, rbi: 0, walks: 0, strikeouts: 1, avg: '.305', obp: '.372', ops: '.875' },
      { batOrder: 3, name: '최형우', position: 'DH', atBats: 2, hits: 1, homeRuns: 0, rbi: 1, walks: 0, strikeouts: 0, avg: '.315', obp: '.390', ops: '.910' },
      { batOrder: 4, name: '나성범', position: 'RF', atBats: 2, hits: 0, homeRuns: 0, rbi: 0, walks: 1, strikeouts: 1, avg: '.275', obp: '.345', ops: '.790' },
      { batOrder: 5, name: '김도영', position: '3B', atBats: 2, hits: 1, homeRuns: 0, rbi: 0, walks: 0, strikeouts: 0, avg: '.298', obp: '.362', ops: '.840' },
      { batOrder: 6, name: '한준수', position: 'C', atBats: 2, hits: 0, homeRuns: 0, rbi: 0, walks: 0, strikeouts: 2, avg: '.230', obp: '.288', ops: '.640' },
      { batOrder: 7, name: '이우성', position: 'CF', atBats: 1, hits: 0, homeRuns: 0, rbi: 0, walks: 0, strikeouts: 1, avg: '.248', obp: '.308', ops: '.695' },
      { batOrder: 8, name: '박민', position: '2B', atBats: 2, hits: 0, homeRuns: 0, rbi: 0, walks: 0, strikeouts: 1, avg: '.220', obp: '.278', ops: '.620' },
      { batOrder: 9, name: '김태군', position: '1B', atBats: 2, hits: 0, homeRuns: 0, rbi: 0, walks: 0, strikeouts: 0, avg: '.210', obp: '.265', ops: '.590' },
    ],
    pitchers: [
      { turnNo: 1, name: '안우진', result: '', innings: '4.0', pitchCount: 72, hits: 5, strikeouts: 4, runs: 3, earnedRuns: 3, era: '3.80', whip: '1.35' },
    ],
  },
};

// 야구 종료 목 데이터 (baseball/mockData.ts에서 re-export)
export { mockBaseballFinishedData };

// ============================================================
// SOCCER
// ============================================================

// 축구 경기 예정 목 데이터
export const mockSoccerBeforeData: SoccerGameData = {
  sportType: 'soccer',
  league: '프리미어리그',
  date: '03.15',
  time: '21:00',
  status: '예정',
  venue: '에미레이츠 스타디움',
  homeTeam: {
    name: '아스널',
    shortName: '아스널',
    logo: '',
    record: '18승 3무 5패',
    score: 0,
    players: [],
    recentGames: ['W', 'W', 'D', 'W', 'L'],
  },
  awayTeam: {
    name: '맨체스터 시티',
    shortName: '맨시티',
    logo: '',
    record: '20승 2무 4패',
    score: 0,
    players: [],
    recentGames: ['W', 'W', 'W', 'L', 'W'],
  },
  headToHead: {
    totalGames: 8,
    homeWins: 3,
    awayWins: 4,
    draws: 1,
    recentMatches: [
      { date: '2024-01-01', homeScore: 0, awayScore: 1, winner: 'away' },
      { date: '2023-10-08', homeScore: 1, awayScore: 0, winner: 'home' },
      { date: '2023-04-26', homeScore: 3, awayScore: 3, winner: 'draw' },
    ],
  },
  standings: [
    {
      teams: [
        { rank: 1, name: '맨체스터 시티', shortName: '맨시티', played: 26, wins: 20, draws: 2, losses: 4, goalsFor: 58, goalsAgainst: 28, goalDifference: 30, points: 62, recentGames: ['W', 'W', 'W', 'L', 'W'] },
        { rank: 2, name: '아스널', shortName: '아스널', played: 26, wins: 18, draws: 3, losses: 5, goalsFor: 52, goalsAgainst: 25, goalDifference: 27, points: 57, recentGames: ['W', 'W', 'D', 'W', 'L'] },
        { rank: 3, name: '리버풀', shortName: '리버풀', played: 26, wins: 17, draws: 4, losses: 5, goalsFor: 55, goalsAgainst: 30, goalDifference: 25, points: 55, recentGames: ['W', 'D', 'W', 'W', 'W'] },
      ],
    },
  ],
};

// 축구 경기 진행중 목 데이터 (후반 67분)
export const mockSoccerLiveData: SoccerGameData = {
  sportType: 'soccer',
  league: '프리미어리그',
  date: '03.15',
  status: '진행중',
  venue: '에미레이츠 스타디움',
  currentPeriod: '후반',
  currentMinute: 67,
  homeTeam: {
    name: '아스널',
    shortName: '아스널',
    logo: '',
    record: '18승 3무 5패',
    score: 2,
    halfScores: { firstHalf: 1, secondHalf: 1 },
    players: [
      { number: 1, name: '라야', position: 'GK', minutes: 67, goals: 0, assists: 0, shots: 0, shotsOnTarget: 0, passes: 32, passAccuracy: '89%', tackles: 0, interceptions: 0, fouls: 0, yellowCards: 0, redCards: 0, saves: 3 },
      { number: 35, name: '지나브리', position: 'DF', minutes: 67, goals: 0, assists: 1, shots: 1, shotsOnTarget: 0, passes: 45, passAccuracy: '91%', tackles: 2, interceptions: 1, fouls: 0, yellowCards: 0, redCards: 0 },
      { number: 29, name: '트로사르', position: 'MF', minutes: 67, goals: 1, assists: 0, shots: 3, shotsOnTarget: 2, passes: 38, passAccuracy: '84%', tackles: 1, interceptions: 0, fouls: 1, yellowCards: 0, redCards: 0 },
      { number: 9, name: '제수스', position: 'FW', minutes: 67, goals: 1, assists: 0, shots: 4, shotsOnTarget: 2, passes: 22, passAccuracy: '78%', tackles: 0, interceptions: 0, fouls: 2, yellowCards: 0, redCards: 0 },
      { number: 7, name: '사카', position: 'FW', minutes: 67, goals: 0, assists: 1, shots: 2, shotsOnTarget: 1, passes: 34, passAccuracy: '82%', tackles: 0, interceptions: 0, fouls: 1, yellowCards: 0, redCards: 0 },
    ],
    recentGames: ['W', 'W', 'D', 'W', 'L'],
  },
  awayTeam: {
    name: '맨체스터 시티',
    shortName: '맨시티',
    logo: '',
    record: '20승 2무 4패',
    score: 1,
    halfScores: { firstHalf: 0, secondHalf: 1 },
    players: [
      { number: 31, name: '에데르송', position: 'GK', minutes: 67, goals: 0, assists: 0, shots: 0, shotsOnTarget: 0, passes: 28, passAccuracy: '86%', tackles: 0, interceptions: 0, fouls: 0, yellowCards: 0, redCards: 0, saves: 4 },
      { number: 17, name: '데브라위너', position: 'MF', minutes: 67, goals: 0, assists: 0, shots: 2, shotsOnTarget: 1, passes: 52, passAccuracy: '93%', tackles: 1, interceptions: 2, fouls: 0, yellowCards: 0, redCards: 0 },
      { number: 10, name: '그릴리쉬', position: 'MF', minutes: 67, goals: 0, assists: 1, shots: 1, shotsOnTarget: 1, passes: 41, passAccuracy: '88%', tackles: 0, interceptions: 0, fouls: 1, yellowCards: 1, redCards: 0 },
      { number: 9, name: '홀란드', position: 'FW', minutes: 67, goals: 1, assists: 0, shots: 5, shotsOnTarget: 3, passes: 18, passAccuracy: '72%', tackles: 0, interceptions: 0, fouls: 1, yellowCards: 0, redCards: 0 },
      { number: 20, name: '베르나르두', position: 'MF', minutes: 67, goals: 0, assists: 0, shots: 1, shotsOnTarget: 0, passes: 46, passAccuracy: '90%', tackles: 2, interceptions: 1, fouls: 0, yellowCards: 0, redCards: 0 },
    ],
    recentGames: ['W', 'W', 'W', 'L', 'W'],
  },
  goals: [
    { minute: 22, scorer: '트로사르', assist: '사카', team: 'home' },
    { minute: 58, scorer: '홀란드', team: 'away' },
    { minute: 61, scorer: '제수스', assist: '지나브리', team: 'home' },
  ],
  gameRecords: [
    { label: '유효 슈팅', home: 6, away: 5 },
    { label: '슈팅', home: 10, away: 12 },
    { label: '점유율', home: '52%', away: '48%' },
    { label: '패스', home: 380, away: 420 },
    { label: '코너킥', home: 5, away: 4 },
    { label: '파울', home: 8, away: 10 },
  ],
};

// 축구 경기 종료 목 데이터
export const mockSoccerFinishedData: SoccerGameData = {
  sportType: 'soccer',
  league: '프리미어리그',
  date: '03.10',
  status: '종료',
  venue: '에티하드 스타디움',
  homeTeam: {
    name: '맨체스터 시티',
    shortName: '맨시티',
    logo: '',
    record: '20승 2무 4패',
    score: 3,
    halfScores: { firstHalf: 2, secondHalf: 1 },
    players: [
      { number: 31, name: '에데르송', position: 'GK', minutes: 90, goals: 0, assists: 0, shots: 0, shotsOnTarget: 0, passes: 38, passAccuracy: '87%', tackles: 0, interceptions: 0, fouls: 0, yellowCards: 0, redCards: 0, saves: 4 },
      { number: 17, name: '데브라위너', position: 'MF', minutes: 90, goals: 1, assists: 2, shots: 3, shotsOnTarget: 2, passes: 72, passAccuracy: '94%', tackles: 2, interceptions: 3, fouls: 0, yellowCards: 0, redCards: 0 },
      { number: 9, name: '홀란드', position: 'FW', minutes: 90, goals: 2, assists: 0, shots: 7, shotsOnTarget: 5, passes: 25, passAccuracy: '76%', tackles: 0, interceptions: 0, fouls: 2, yellowCards: 0, redCards: 0 },
      { number: 20, name: '베르나르두', position: 'MF', minutes: 90, goals: 0, assists: 1, shots: 2, shotsOnTarget: 1, passes: 62, passAccuracy: '91%', tackles: 3, interceptions: 2, fouls: 1, yellowCards: 0, redCards: 0 },
      { number: 3, name: '루벤 디아스', position: 'DF', minutes: 90, goals: 0, assists: 0, shots: 0, shotsOnTarget: 0, passes: 58, passAccuracy: '92%', tackles: 4, interceptions: 3, fouls: 0, yellowCards: 0, redCards: 0 },
    ],
    recentGames: ['W', 'W', 'W', 'L', 'W'],
  },
  awayTeam: {
    name: '토트넘',
    shortName: '토트넘',
    logo: '',
    record: '14승 5무 7패',
    score: 1,
    halfScores: { firstHalf: 0, secondHalf: 1 },
    players: [
      { number: 1, name: '포로미시', position: 'GK', minutes: 90, goals: 0, assists: 0, shots: 0, shotsOnTarget: 0, passes: 25, passAccuracy: '78%', tackles: 0, interceptions: 0, fouls: 0, yellowCards: 0, redCards: 0, saves: 3 },
      { number: 10, name: '손흥민', position: 'FW', minutes: 90, goals: 1, assists: 0, shots: 4, shotsOnTarget: 2, passes: 28, passAccuracy: '80%', tackles: 0, interceptions: 0, fouls: 1, yellowCards: 0, redCards: 0 },
      { number: 7, name: '존슨', position: 'MF', minutes: 90, goals: 0, assists: 0, shots: 1, shotsOnTarget: 0, passes: 38, passAccuracy: '83%', tackles: 2, interceptions: 1, fouls: 2, yellowCards: 1, redCards: 0 },
      { number: 5, name: '호이브레크', position: 'DF', minutes: 90, goals: 0, assists: 0, shots: 0, shotsOnTarget: 0, passes: 45, passAccuracy: '86%', tackles: 3, interceptions: 1, fouls: 1, yellowCards: 0, redCards: 0 },
      { number: 17, name: '베르트용', position: 'MF', minutes: 90, goals: 0, assists: 1, shots: 1, shotsOnTarget: 0, passes: 42, passAccuracy: '85%', tackles: 2, interceptions: 2, fouls: 1, yellowCards: 0, redCards: 0 },
    ],
    recentGames: ['L', 'D', 'W', 'L', 'W'],
  },
  goals: [
    { minute: 12, scorer: '홀란드', assist: '데브라위너', team: 'home' },
    { minute: 38, scorer: '데브라위너', assist: '베르나르두', team: 'home' },
    { minute: 71, scorer: '손흥민', assist: '베르트용', team: 'away' },
    { minute: 85, scorer: '홀란드', team: 'home' },
  ],
  gameRecords: [
    { label: '유효 슈팅', home: 9, away: 3 },
    { label: '슈팅', home: 15, away: 8 },
    { label: '점유율', home: '62%', away: '38%' },
    { label: '패스', home: 520, away: 320 },
    { label: '코너킥', home: 8, away: 3 },
    { label: '파울', home: 7, away: 12 },
  ],
};

// ============================================================
// VOLLEYBALL
// ============================================================

// 배구 경기전 목 데이터
export const mockVolleyballBeforeData: VolleyballGameData = {
  sportType: 'volleyball',
  league: 'V리그 남자부',
  date: '03.12',
  time: '19:00',
  status: '예정',
  homeTeam: {
    name: '대한항공 점보스',
    shortName: '대한항공',
    logo: '',
    record: '25승 8패',
    setsWon: 0,
    players: [],
    recentGames: ['W', 'W', 'W', 'L', 'W'],
    primaryColor: '#003DA5',
    secondaryColor: '#FFD700',
  },
  awayTeam: {
    name: 'KB손해보험 스타즈',
    shortName: 'KB손보',
    logo: '',
    record: '20승 13패',
    setsWon: 0,
    players: [],
    recentGames: ['L', 'W', 'W', 'L', 'W'],
    primaryColor: '#1f2937',
    secondaryColor: '#FFFFFF',
  },
  headToHead: {
    totalGames: 6,
    homeWins: 4,
    awayWins: 2,
    recentMatches: [
      { date: '2025-01-15', homeSets: 3, awaySets: 1, winner: 'home' },
      { date: '2024-12-08', homeSets: 1, awaySets: 3, winner: 'away' },
      { date: '2024-11-20', homeSets: 3, awaySets: 0, winner: 'home' },
    ],
  },
  standings: [
    {
      teams: [
        { rank: 1, name: '대한항공', shortName: '대한항공', wins: 25, losses: 8, winRate: '0.758', recentGames: ['W', 'W', 'W', 'L', 'W'] },
        { rank: 2, name: '현대캐피탈', shortName: '현대캐피탈', wins: 23, losses: 10, winRate: '0.697', recentGames: ['W', 'L', 'W', 'W', 'W'] },
        { rank: 3, name: 'KB손보', shortName: 'KB손보', wins: 20, losses: 13, winRate: '0.606', recentGames: ['L', 'W', 'W', 'L', 'W'] },
      ],
    },
  ],
};

// 배구 경기중 목 데이터 (3세트 진행중)
export const mockVolleyballLiveData: VolleyballGameData = {
  sportType: 'volleyball',
  league: 'V리그 남자부',
  date: '03.12',
  status: '진행중',
  currentSet: 3,
  homeTeam: {
    name: '대한항공 점보스',
    shortName: '대한항공',
    logo: '',
    record: '25승 8패',
    setsWon: 1,
    setScores: { set1: 25, set2: 22, set3: 18 },
    players: [
      { number: 7, name: '정지석', position: 'OH', sets: 3, points: 18, attacks: 42, kills: 20, attackPct: '47.6%', blocks: 1, aces: 2, digs: 8 },
      { number: 10, name: '임동혁', position: 'MB', sets: 3, points: 10, attacks: 18, kills: 11, attackPct: '61.1%', blocks: 4, aces: 0, digs: 1 },
      { number: 3, name: '한선수', position: 'S', sets: 3, points: 2, attacks: 5, kills: 2, attackPct: '40.0%', blocks: 1, aces: 1, digs: 6, assists: 65 },
      { number: 14, name: '전광인', position: 'OP', sets: 3, points: 12, attacks: 32, kills: 14, attackPct: '43.8%', blocks: 2, aces: 1, digs: 3 },
      { number: 5, name: '황경민', position: 'OH', sets: 3, points: 8, attacks: 20, kills: 9, attackPct: '45.0%', blocks: 0, aces: 0, digs: 12 },
    ],
    recentGames: ['W', 'W', 'W', 'L', 'W'],
    primaryColor: '#003DA5',
    secondaryColor: '#FFD700',
  },
  awayTeam: {
    name: 'KB손해보험 스타즈',
    shortName: 'KB손보',
    logo: '',
    record: '20승 13패',
    setsWon: 1,
    setScores: { set1: 23, set2: 25, set3: 21 },
    players: [
      { number: 11, name: '김학민', position: 'OH', sets: 3, points: 15, attacks: 38, kills: 17, attackPct: '44.7%', blocks: 1, aces: 1, digs: 10 },
      { number: 6, name: '박철우', position: 'MB', sets: 3, points: 9, attacks: 16, kills: 10, attackPct: '62.5%', blocks: 5, aces: 0, digs: 0 },
      { number: 1, name: '노재욱', position: 'S', sets: 3, points: 1, attacks: 3, kills: 1, attackPct: '33.3%', blocks: 0, aces: 1, digs: 5, assists: 58 },
      { number: 20, name: '이선규', position: 'OP', sets: 3, points: 14, attacks: 30, kills: 15, attackPct: '50.0%', blocks: 1, aces: 2, digs: 2 },
      { number: 9, name: '이시몬', position: 'L', sets: 3, points: 0, attacks: 0, kills: 0, attackPct: '0%', blocks: 0, aces: 0, digs: 22 },
    ],
    recentGames: ['L', 'W', 'W', 'L', 'W'],
    primaryColor: '#1f2937',
    secondaryColor: '#FFFFFF',
  },
  gameRecords: [
    { label: '공격 성공률', home: '46.8%', away: '45.2%' },
    { label: '블로킹', home: 8, away: 12 },
    { label: '서브 에이스', home: 3, away: 4 },
    { label: '디그', home: 30, away: 38 },
  ],
};

// 배구 경기종료 목 데이터
export const mockVolleyballFinishedData: VolleyballGameData = {
  sportType: 'volleyball',
  league: 'V리그 남자부',
  date: '03.08',
  status: '종료',
  homeTeam: {
    name: '대한항공 점보스',
    shortName: '대한항공',
    logo: '',
    record: '24승 8패',
    setsWon: 3,
    setScores: { set1: 25, set2: 22, set3: 25, set4: 0, set5: 0 },
    players: [
      { number: 7, name: '정지석', position: 'OH', sets: 3, points: 22, attacks: 48, kills: 24, attackPct: '50.0%', blocks: 2, aces: 1, digs: 12 },
      { number: 10, name: '임동혁', position: 'MB', sets: 3, points: 14, attacks: 22, kills: 14, attackPct: '63.6%', blocks: 6, aces: 1, digs: 2 },
      { number: 3, name: '한선수', position: 'S', sets: 3, points: 3, attacks: 7, kills: 3, attackPct: '42.9%', blocks: 0, aces: 2, digs: 8, assists: 82 },
      { number: 14, name: '전광인', position: 'OP', sets: 3, points: 18, attacks: 38, kills: 20, attackPct: '52.6%', blocks: 3, aces: 0, digs: 4 },
      { number: 5, name: '황경민', position: 'OH', sets: 3, points: 10, attacks: 24, kills: 11, attackPct: '45.8%', blocks: 1, aces: 1, digs: 15 },
    ],
    recentGames: ['W', 'W', 'W', 'L', 'W'],
    primaryColor: '#003DA5',
    secondaryColor: '#FFD700',
  },
  awayTeam: {
    name: 'KB손해보험 스타즈',
    shortName: 'KB손보',
    logo: '',
    record: '19승 14패',
    setsWon: 0,
    setScores: { set1: 21, set2: 18, set3: 20, set4: 0, set5: 0 },
    players: [
      { number: 11, name: '김학민', position: 'OH', sets: 3, points: 16, attacks: 42, kills: 18, attackPct: '42.9%', blocks: 0, aces: 1, digs: 14 },
      { number: 6, name: '박철우', position: 'MB', sets: 3, points: 8, attacks: 14, kills: 8, attackPct: '57.1%', blocks: 4, aces: 0, digs: 1 },
      { number: 1, name: '노재욱', position: 'S', sets: 3, points: 2, attacks: 4, kills: 2, attackPct: '50.0%', blocks: 0, aces: 0, digs: 7, assists: 60 },
      { number: 20, name: '이선규', position: 'OP', sets: 3, points: 12, attacks: 28, kills: 12, attackPct: '42.9%', blocks: 2, aces: 2, digs: 3 },
      { number: 9, name: '이시몬', position: 'L', sets: 3, points: 0, attacks: 0, kills: 0, attackPct: '0%', blocks: 0, aces: 0, digs: 28 },
    ],
    recentGames: ['L', 'L', 'W', 'L', 'W'],
    primaryColor: '#1f2937',
    secondaryColor: '#FFFFFF',
  },
  gameRecords: [
    { label: '공격 성공률', home: '50.8%', away: '43.2%' },
    { label: '블로킹', home: 12, away: 10 },
    { label: '서브 에이스', home: 5, away: 3 },
    { label: '디그', home: 41, away: 55 },
  ],
};

// ============================================================
// MOCK_DATA_MAP (DevPanel에서 sport/state로 키 조합하여 사용)
// ============================================================

type GameData =
  | BasketballGameData
  | BaseballGameData
  | SoccerGameData
  | VolleyballGameData;

export const MOCK_DATA_MAP: Record<string, GameData> = {
  // 농구
  'basketball_예정': mockBasketballData,
  'basketball_진행중': mockBasketballLiveData,
  'basketball_종료': mockFinishedBasketballData,
  // 야구
  'baseball_예정': mockBaseballBeforeData,
  'baseball_진행중': mockBaseballLiveData,
  'baseball_종료': mockBaseballFinishedData,
  // 축구
  'soccer_예정': mockSoccerBeforeData,
  'soccer_진행중': mockSoccerLiveData,
  'soccer_종료': mockSoccerFinishedData,
  // 배구
  'volleyball_예정': mockVolleyballBeforeData,
  'volleyball_진행중': mockVolleyballLiveData,
  'volleyball_종료': mockVolleyballFinishedData,
};

// DevPanel에서 스포츠별 선택 가능한 상태 목록
export const SPORT_STATES: Record<string, string[]> = {
  basketball: ['예정', '진행중', '종료'],
  baseball: ['예정', '진행중', '종료'],
  soccer: ['예정', '진행중', '종료'],
  volleyball: ['예정', '진행중', '종료'],
};
