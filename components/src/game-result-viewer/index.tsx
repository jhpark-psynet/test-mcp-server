import { createRoot } from 'react-dom/client';
import { z } from 'zod';
import { GameResultViewer } from './GameResultViewer';
import { GameDataSchema, type GameData } from './types';
import '../index.css';

// Mock data for development (will be replaced by structuredContent from MCP server)
const MOCK_GAME_DATA: GameData = {
  league: 'NBA',
  date: '11.18',
  status: '종료',
  homeTeam: {
    name: '클리블랜드',
    shortName: '클리블랜드',
    logo: '',
    record: '-',
    score: 118,
    players: [
      { number: 45, name: '도노반 미첼', position: 'G', minutes: 35, rebounds: 6, assists: 8, points: 28 },
      { number: 4, name: '에반 모블리', position: 'F', minutes: 32, rebounds: 10, assists: 3, points: 18 },
    ],
  },
  awayTeam: {
    name: '밀워키',
    shortName: '밀워키',
    logo: '',
    record: '-',
    score: 106,
    players: [
      { number: 34, name: '야니스 아데토쿤보', position: 'F', minutes: 36, rebounds: 12, assists: 6, points: 32 },
      { number: 0, name: '데이미언 릴라드', position: 'G', minutes: 34, rebounds: 4, assists: 7, points: 24 },
    ],
  },
  gameRecords: [
    { label: '필드골', home: '45/88', away: '40/92' },
    { label: '3점슛', home: '12/30', away: '10/35' },
    { label: '자유투', home: '16/20', away: '16/22' },
    { label: '리바운드', home: 45, away: 40 },
    { label: '어시스트', home: 28, away: 22 },
    { label: '턴오버', home: 12, away: 15 },
    { label: '스틸', home: 8, away: 6 },
    { label: '블록', home: 5, away: 3 },
    { label: '파울', home: 18, away: 20 },
  ],
};

// Legacy transformation function (not used anymore - handler returns GameData directly)
function transformApiDataToGameData_LEGACY(apiData: any): GameData {
  const { game_info, team_stats, player_stats } = apiData;

  // Parse date format (YYYYMMDD to readable format)
  const formatDate = (dateStr: string): string => {
    if (dateStr.length !== 8) return dateStr;
    const year = dateStr.substring(0, 4);
    const month = dateStr.substring(4, 6);
    const day = dateStr.substring(6, 8);
    const date = new Date(`${year}-${month}-${day}`);
    const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
    const weekday = weekdays[date.getDay()];
    return `${month}.${day} (${weekday})`;
  };

  // Map league name to LeagueType
  const mapLeague = (league: string): LeagueType => {
    if (league === 'NBA' || league === 'KBL' || league === 'WKBL') {
      return league;
    }
    return 'NBA'; // default
  };

  // Convert time string "MM:SS" to minutes
  const parseMinutes = (timeStr: string): number => {
    if (!timeStr || typeof timeStr !== 'string') return 0;
    const parts = timeStr.split(':');
    if (parts.length === 2) {
      return parseInt(parts[0], 10) || 0;
    }
    if (parts.length === 3) {
      // HH:MM:SS format
      return parseInt(parts[0], 10) * 60 + parseInt(parts[1], 10) || 0;
    }
    return 0;
  };

  // Extract home and away team stats
  const homeTeamStats = team_stats[0] || {};
  const awayTeamStats = team_stats[1] || {};

  // Group players by team
  const homePlayers = player_stats.filter(
    (p: any) => p.team_id === homeTeamStats.home_team_id
  );
  const awayPlayers = player_stats.filter(
    (p: any) => p.team_id === awayTeamStats.away_team_id
  );

  // Transform player stats
  const transformPlayer = (player: any) => ({
    number: parseInt(player.back_no || '0', 10),
    name: player.player_name || 'Unknown',
    position: player.pos_sc || '-',
    minutes: parseMinutes(player.player_time),
    rebounds: parseInt(player.treb_cn || '0', 10),
    assists: parseInt(player.assist_cn || '0', 10),
    points: parseInt(player.tot_score || '0', 10),
  });

  // Create game records from team stats
  const createGameRecords = () => {
    const records = [];

    // Field Goals
    const homeFgm = parseInt(homeTeamStats.home_team_fgm_cn || '0', 10);
    const homeFga = parseInt(homeTeamStats.home_team_fga_cn || '1', 10);
    const awayFgm = parseInt(awayTeamStats.away_team_fgm_cn || '0', 10);
    const awayFga = parseInt(awayTeamStats.away_team_fga_cn || '1', 10);
    records.push({
      label: '필드골',
      home: `${homeFgm}/${homeFga}`,
      away: `${awayFgm}/${awayFga}`,
    });

    // 3-Pointers
    const home3pm = parseInt(homeTeamStats.home_team_pgm3_cn || '0', 10);
    const home3pa = parseInt(homeTeamStats.home_team_pga3_cn || '1', 10);
    const away3pm = parseInt(awayTeamStats.away_team_pgm3_cn || '0', 10);
    const away3pa = parseInt(awayTeamStats.away_team_pga3_cn || '1', 10);
    records.push({
      label: '3점슛',
      home: `${home3pm}/${home3pa}`,
      away: `${away3pm}/${away3pa}`,
    });

    // Free Throws
    const homeFtm = parseInt(homeTeamStats.home_team_ftm_cn || '0', 10);
    const homeFta = parseInt(homeTeamStats.home_team_fta_cn || '1', 10);
    const awayFtm = parseInt(awayTeamStats.away_team_ftm_cn || '0', 10);
    const awayFta = parseInt(awayTeamStats.away_team_fta_cn || '1', 10);
    records.push({
      label: '자유투',
      home: `${homeFtm}/${homeFta}`,
      away: `${awayFtm}/${awayFta}`,
    });

    // Rebounds
    const homeOreb = parseInt(homeTeamStats.home_team_oreb_cn || '0', 10);
    const homeDreb = parseInt(homeTeamStats.home_team_dreb_cn || '0', 10);
    const awayOreb = parseInt(awayTeamStats.away_team_oreb_cn || '0', 10);
    const awayDreb = parseInt(awayTeamStats.away_team_dreb_cn || '0', 10);
    records.push({
      label: '리바운드',
      home: homeOreb + homeDreb,
      away: awayOreb + awayDreb,
    });

    // Assists
    records.push({
      label: '어시스트',
      home: parseInt(homeTeamStats.home_team_assist_cn || '0', 10),
      away: parseInt(awayTeamStats.away_team_assist_cn || '0', 10),
    });

    // Turnovers
    records.push({
      label: '턴오버',
      home: parseInt(homeTeamStats.home_team_turnover_cn || '0', 10),
      away: parseInt(awayTeamStats.away_team_turnover_cn || '0', 10),
    });

    // Steals
    records.push({
      label: '스틸',
      home: parseInt(homeTeamStats.home_team_steal_cn || '0', 10),
      away: parseInt(awayTeamStats.away_team_steal_cn || '0', 10),
    });

    // Blocks
    records.push({
      label: '블록',
      home: parseInt(homeTeamStats.home_team_block_cn || '0', 10),
      away: parseInt(awayTeamStats.away_team_block_cn || '0', 10),
    });

    // Fouls
    records.push({
      label: '파울',
      home: parseInt(homeTeamStats.home_team_pfoul_cn || '0', 10),
      away: parseInt(awayTeamStats.away_team_pfoul_cn || '0', 10),
    });

    return records;
  };

  // Get short team name (extract first 2-3 characters)
  const getShortName = (fullName: string): string => {
    // Remove common prefixes
    const cleaned = fullName.replace(/^(뉴|골든|샌)\s*/, '');
    return cleaned.split(' ')[0] || fullName.slice(0, 3);
  };

  return {
    league: mapLeague(game_info.league),
    date: formatDate(game_info.date),
    status: '종료' as GameStatus, // Assuming finished games only
    homeTeam: {
      name: game_info.home_team,
      shortName: getShortName(game_info.home_team),
      logo: '', // No logo data in API response
      record: '-', // No record data in API response
      score: game_info.home_score,
      players: homePlayers.map(transformPlayer),
    },
    awayTeam: {
      name: game_info.away_team,
      shortName: getShortName(game_info.away_team),
      logo: '', // No logo data in API response
      record: '-', // No record data in API response
      score: game_info.away_score,
      players: awayPlayers.map(transformPlayer),
    },
    gameRecords: createGameRecords(),
  };
}

function ErrorFallback({ error }: { error: string }) {
  return (
    <div className="max-w-2xl mx-auto my-8 p-8 bg-red-50 rounded-lg shadow-lg border-2 border-red-200">
      <h1 className="text-2xl font-bold text-red-800 mb-4">Validation Error</h1>
      <p className="text-red-600 font-mono text-sm whitespace-pre-wrap">{error}</p>
    </div>
  );
}

// Declare global window type for structuredContent
declare global {
  interface Window {
    __STRUCTURED_CONTENT__?: any;
  }
}

// Initialize the app
const rootElement = document.getElementById('game-result-viewer-root');
if (rootElement) {
  const root = createRoot(rootElement);

  // Get game data from MCP server via structuredContent (global variable)
  // Fall back to mock data for development
  const gameData = window.__STRUCTURED_CONTENT__ || MOCK_GAME_DATA;

  // Validate game data
  try {
    const validatedGameData = GameDataSchema.parse(gameData);
    root.render(<GameResultViewer data={validatedGameData} />);
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errorMessage = error.errors
        .map((err) => `${err.path.join('.')}: ${err.message}`)
        .join('\n');
      root.render(<ErrorFallback error={errorMessage} />);
    } else {
      root.render(<ErrorFallback error={String(error)} />);
    }
  }
}

export default GameResultViewer;
