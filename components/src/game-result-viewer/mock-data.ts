import type { BasketballGameData } from './sports/basketball/types';

export const mockBasketballData: BasketballGameData = {
  sportType: 'basketball',
  league: 'NBA',
  date: '2024-12-18',
  status: '진행중',
  homeTeam: {
    name: 'Los Angeles Lakers',
    shortName: 'LAL',
    logo: '',
    record: '15승 8패',
    score: 87,
    quarterScores: { q1: 28, q2: 22, q3: 25, q4: 12 },
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
    score: 82,
    quarterScores: { q1: 25, q2: 20, q3: 22, q4: 15 },
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
  headToHead: {
    totalGames: 10,
    homeWins: 6,
    awayWins: 4,
    recentMatches: [
      { date: '2024-11-15', homeScore: 118, awayScore: 112, winner: 'home' },
      { date: '2024-10-22', homeScore: 105, awayScore: 110, winner: 'away' },
    ],
  },
};

// 다른 스포츠 mock 데이터도 여기에 추가 가능
