import { createRoot } from 'react-dom/client';
import { z } from 'zod';
import '../index.css';

// Zod schema for props validation
const GameInfoSchema = z.object({
  league: z.string(),
  home_team: z.string(),
  away_team: z.string(),
  home_score: z.number(),
  away_score: z.number(),
  arena: z.string(),
  date: z.string(),
  time: z.string(),
});

const TeamStatsSchema = z.object({
  home_team_id: z.string().optional(),
  home_team_name: z.string().optional(),
  home_team_fgm_cn: z.string().optional(),
  home_team_fga_cn: z.string().optional(),
  home_team_pgm3_cn: z.string().optional(),
  home_team_pga3_cn: z.string().optional(),
  home_team_ftm_cn: z.string().optional(),
  home_team_fta_cn: z.string().optional(),
  home_team_oreb_cn: z.string().optional(),
  home_team_dreb_cn: z.string().optional(),
  home_team_assist_cn: z.string().optional(),
  home_team_turnover_cn: z.string().optional(),
  home_team_steal_cn: z.string().optional(),
  home_team_block_cn: z.string().optional(),
  home_team_pfoul_cn: z.string().optional(),
  away_team_id: z.string().optional(),
  away_team_name: z.string().optional(),
  away_team_fgm_cn: z.string().optional(),
  away_team_fga_cn: z.string().optional(),
  away_team_pgm3_cn: z.string().optional(),
  away_team_pga3_cn: z.string().optional(),
  away_team_ftm_cn: z.string().optional(),
  away_team_fta_cn: z.string().optional(),
  away_team_oreb_cn: z.string().optional(),
  away_team_dreb_cn: z.string().optional(),
  away_team_assist_cn: z.string().optional(),
  away_team_turnover_cn: z.string().optional(),
  away_team_steal_cn: z.string().optional(),
  away_team_block_cn: z.string().optional(),
  away_team_pfoul_cn: z.string().optional(),
});

const PlayerStatsSchema = z.object({
  game_id: z.string(),
  team_id: z.string(),
  player_id: z.string(),
  player_name: z.string(),
  pos_sc: z.string(),
  player_time: z.string(),
  tot_score: z.union([z.string(), z.number()]),
  treb_cn: z.union([z.string(), z.number()]),
  assist_cn: z.union([z.string(), z.number()]),
  steal_cn: z.union([z.string(), z.number()]),
  blocks: z.union([z.string(), z.number()]),
  fgm_cn: z.union([z.string(), z.number()]),
  fga_cn: z.union([z.string(), z.number()]),
  pgm3_cn: z.union([z.string(), z.number()]),
  fgpct: z.string(),
});

const GameStatsPropsSchema = z.object({
  game_id: z.string(),
  game_info: GameInfoSchema,
  team_stats: z.array(TeamStatsSchema),
  player_stats: z.array(PlayerStatsSchema),
});

type GameStatsProps = z.infer<typeof GameStatsPropsSchema>;

function GameHeader({ game_info }: { game_info: GameStatsProps['game_info'] }) {
  const homeWon = game_info.home_score > game_info.away_score;

  return (
    <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white p-6 rounded-t-lg">
      <div className="text-center mb-2">
        <div className="text-sm opacity-90">{game_info.league}</div>
        <div className="text-xs opacity-75">{game_info.arena}</div>
        <div className="text-xs opacity-75">{game_info.date} {game_info.time}</div>
      </div>

      <div className="flex items-center justify-center gap-8 mt-4">
        <div className={`text-center flex-1 ${homeWon ? 'opacity-100' : 'opacity-70'}`}>
          <div className="text-2xl font-bold mb-2">{game_info.home_team}</div>
          <div className="text-5xl font-bold">{game_info.home_score}</div>
          {homeWon && <div className="text-sm mt-1">🏆 WIN</div>}
        </div>

        <div className="text-3xl font-light opacity-50">VS</div>

        <div className={`text-center flex-1 ${!homeWon ? 'opacity-100' : 'opacity-70'}`}>
          <div className="text-2xl font-bold mb-2">{game_info.away_team}</div>
          <div className="text-5xl font-bold">{game_info.away_score}</div>
          {!homeWon && <div className="text-sm mt-1">🏆 WIN</div>}
        </div>
      </div>
    </div>
  );
}

function TeamStatsTable({ team_stats, game_info }: { team_stats: GameStatsProps['team_stats'], game_info: GameStatsProps['game_info'] }) {
  if (team_stats.length < 2) return null;

  const homeTeam = team_stats[0];
  const awayTeam = team_stats[1];

  const toNum = (val: any) => typeof val === 'string' ? parseInt(val) || 0 : val || 0;

  const homeFgm = toNum(homeTeam.home_team_fgm_cn);
  const homeFga = toNum(homeTeam.home_team_fga_cn);
  const home3pm = toNum(homeTeam.home_team_pgm3_cn);
  const home3pa = toNum(homeTeam.home_team_pga3_cn);
  const homeFtm = toNum(homeTeam.home_team_ftm_cn);
  const homeFta = toNum(homeTeam.home_team_fta_cn);
  const homeOreb = toNum(homeTeam.home_team_oreb_cn);
  const homeDreb = toNum(homeTeam.home_team_dreb_cn);
  const homeAst = toNum(homeTeam.home_team_assist_cn);
  const homeTov = toNum(homeTeam.home_team_turnover_cn);
  const homeStl = toNum(homeTeam.home_team_steal_cn);
  const homeBlk = toNum(homeTeam.home_team_block_cn);
  const homePf = toNum(homeTeam.home_team_pfoul_cn);

  const awayFgm = toNum(awayTeam.away_team_fgm_cn);
  const awayFga = toNum(awayTeam.away_team_fga_cn);
  const away3pm = toNum(awayTeam.away_team_pgm3_cn);
  const away3pa = toNum(awayTeam.away_team_pga3_cn);
  const awayFtm = toNum(awayTeam.away_team_ftm_cn);
  const awayFta = toNum(awayTeam.away_team_fta_cn);
  const awayOreb = toNum(awayTeam.away_team_oreb_cn);
  const awayDreb = toNum(awayTeam.away_team_dreb_cn);
  const awayAst = toNum(awayTeam.away_team_assist_cn);
  const awayTov = toNum(awayTeam.away_team_turnover_cn);
  const awayStl = toNum(awayTeam.away_team_steal_cn);
  const awayBlk = toNum(awayTeam.away_team_block_cn);
  const awayPf = toNum(awayTeam.away_team_pfoul_cn);

  const homeFgPct = homeFga > 0 ? ((homeFgm / homeFga) * 100).toFixed(1) : '0.0';
  const home3pPct = home3pa > 0 ? ((home3pm / home3pa) * 100).toFixed(1) : '0.0';
  const homeFtPct = homeFta > 0 ? ((homeFtm / homeFta) * 100).toFixed(1) : '0.0';

  const awayFgPct = awayFga > 0 ? ((awayFgm / awayFga) * 100).toFixed(1) : '0.0';
  const away3pPct = away3pa > 0 ? ((away3pm / away3pa) * 100).toFixed(1) : '0.0';
  const awayFtPct = awayFta > 0 ? ((awayFtm / awayFta) * 100).toFixed(1) : '0.0';

  return (
    <div className="p-6 bg-gray-50">
      <h2 className="text-xl font-bold text-gray-800 mb-4">📊 Team Statistics</h2>
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-4 py-3 text-left font-semibold text-gray-700">Stat</th>
              <th className="px-4 py-3 text-center font-semibold text-blue-700">{game_info.home_team}</th>
              <th className="px-4 py-3 text-center font-semibold text-red-700">{game_info.away_team}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            <tr>
              <td className="px-4 py-3 font-medium text-gray-700">Field Goals</td>
              <td className="px-4 py-3 text-center">{homeFgm}/{homeFga} ({homeFgPct}%)</td>
              <td className="px-4 py-3 text-center">{awayFgm}/{awayFga} ({awayFgPct}%)</td>
            </tr>
            <tr className="bg-gray-50">
              <td className="px-4 py-3 font-medium text-gray-700">3-Pointers</td>
              <td className="px-4 py-3 text-center">{home3pm}/{home3pa} ({home3pPct}%)</td>
              <td className="px-4 py-3 text-center">{away3pm}/{away3pa} ({away3pPct}%)</td>
            </tr>
            <tr>
              <td className="px-4 py-3 font-medium text-gray-700">Free Throws</td>
              <td className="px-4 py-3 text-center">{homeFtm}/{homeFta} ({homeFtPct}%)</td>
              <td className="px-4 py-3 text-center">{awayFtm}/{awayFta} ({awayFtPct}%)</td>
            </tr>
            <tr className="bg-gray-50">
              <td className="px-4 py-3 font-medium text-gray-700">Rebounds</td>
              <td className="px-4 py-3 text-center">{homeOreb + homeDreb} ({homeOreb}+{homeDreb})</td>
              <td className="px-4 py-3 text-center">{awayOreb + awayDreb} ({awayOreb}+{awayDreb})</td>
            </tr>
            <tr>
              <td className="px-4 py-3 font-medium text-gray-700">Assists</td>
              <td className="px-4 py-3 text-center">{homeAst}</td>
              <td className="px-4 py-3 text-center">{awayAst}</td>
            </tr>
            <tr className="bg-gray-50">
              <td className="px-4 py-3 font-medium text-gray-700">Turnovers</td>
              <td className="px-4 py-3 text-center">{homeTov}</td>
              <td className="px-4 py-3 text-center">{awayTov}</td>
            </tr>
            <tr>
              <td className="px-4 py-3 font-medium text-gray-700">Steals</td>
              <td className="px-4 py-3 text-center">{homeStl}</td>
              <td className="px-4 py-3 text-center">{awayStl}</td>
            </tr>
            <tr className="bg-gray-50">
              <td className="px-4 py-3 font-medium text-gray-700">Blocks</td>
              <td className="px-4 py-3 text-center">{homeBlk}</td>
              <td className="px-4 py-3 text-center">{awayBlk}</td>
            </tr>
            <tr>
              <td className="px-4 py-3 font-medium text-gray-700">Fouls</td>
              <td className="px-4 py-3 text-center">{homePf}</td>
              <td className="px-4 py-3 text-center">{awayPf}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

function PlayerStatsTable({ player_stats, team_id, team_name }: { player_stats: GameStatsProps['player_stats'], team_id: string, team_name: string }) {
  const teamPlayers = player_stats.filter(p => p.team_id === team_id);

  if (teamPlayers.length === 0) return null;

  // Sort by points (tot_score) descending
  const sortedPlayers = [...teamPlayers].sort((a, b) => {
    const aScore = typeof a.tot_score === 'string' ? parseInt(a.tot_score) : a.tot_score;
    const bScore = typeof b.tot_score === 'string' ? parseInt(b.tot_score) : b.tot_score;
    return bScore - aScore;
  });

  return (
    <div className="mb-6">
      <h3 className="text-lg font-bold text-gray-800 mb-3">{team_name}</h3>
      <div className="bg-white rounded-lg shadow overflow-x-auto">
        <table className="w-full text-xs">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-3 py-2 text-left font-semibold text-gray-700 sticky left-0 bg-gray-100">Player</th>
              <th className="px-3 py-2 text-center font-semibold text-gray-700">Pos</th>
              <th className="px-3 py-2 text-center font-semibold text-gray-700">Min</th>
              <th className="px-3 py-2 text-center font-semibold text-gray-700">PTS</th>
              <th className="px-3 py-2 text-center font-semibold text-gray-700">REB</th>
              <th className="px-3 py-2 text-center font-semibold text-gray-700">AST</th>
              <th className="px-3 py-2 text-center font-semibold text-gray-700">STL</th>
              <th className="px-3 py-2 text-center font-semibold text-gray-700">BLK</th>
              <th className="px-3 py-2 text-center font-semibold text-gray-700">FG</th>
              <th className="px-3 py-2 text-center font-semibold text-gray-700">3PT</th>
              <th className="px-3 py-2 text-center font-semibold text-gray-700">FG%</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {sortedPlayers.map((player, idx) => (
              <tr key={player.player_id} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className="px-3 py-2 font-medium text-gray-900 sticky left-0 bg-inherit">{player.player_name}</td>
                <td className="px-3 py-2 text-center text-gray-600">{player.pos_sc}</td>
                <td className="px-3 py-2 text-center text-gray-600">{player.player_time.substring(0, 5)}</td>
                <td className="px-3 py-2 text-center font-semibold text-gray-900">{player.tot_score}</td>
                <td className="px-3 py-2 text-center text-gray-600">{player.treb_cn}</td>
                <td className="px-3 py-2 text-center text-gray-600">{player.assist_cn}</td>
                <td className="px-3 py-2 text-center text-gray-600">{player.steal_cn}</td>
                <td className="px-3 py-2 text-center text-gray-600">{player.blocks}</td>
                <td className="px-3 py-2 text-center text-gray-600">{player.fgm_cn}/{player.fga_cn}</td>
                <td className="px-3 py-2 text-center text-gray-600">{player.pgm3_cn}</td>
                <td className="px-3 py-2 text-center text-gray-600">{player.fgpct}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function App(props: GameStatsProps) {
  // Get team IDs from team_stats
  const homeTeamId = props.team_stats[0]?.home_team_id || '';
  const awayTeamId = props.team_stats[1]?.away_team_id || '';

  return (
    <div className="max-w-6xl mx-auto my-8 bg-white rounded-lg shadow-lg overflow-hidden">
      <GameHeader game_info={props.game_info} />

      <TeamStatsTable team_stats={props.team_stats} game_info={props.game_info} />

      <div className="p-6 bg-white">
        <h2 className="text-xl font-bold text-gray-800 mb-4">👤 Player Statistics</h2>

        <PlayerStatsTable
          player_stats={props.player_stats}
          team_id={homeTeamId}
          team_name={props.game_info.home_team}
        />

        <PlayerStatsTable
          player_stats={props.player_stats}
          team_id={awayTeamId}
          team_name={props.game_info.away_team}
        />
      </div>
    </div>
  );
}

function ErrorFallback({ error }: { error: string }) {
  return (
    <div className="max-w-2xl mx-auto my-8 p-8 bg-red-50 rounded-lg shadow-lg border-2 border-red-200">
      <h1 className="text-2xl font-bold text-red-800 mb-4">Validation Error</h1>
      <p className="text-red-600 font-mono text-sm whitespace-pre-wrap">{error}</p>
    </div>
  );
}

// Initialize the app
const rootElement = document.getElementById('game-stats-root');
if (rootElement) {
  const root = createRoot(rootElement);

  // In a real scenario, props would come from the MCP server via structuredContent
  // For now, we'll use default props for development
  const externalProps = {
    game_id: 'OT2025313104229',
    game_info: {
      league: 'NBA',
      home_team: 'Cleveland',
      away_team: 'Milwaukee',
      home_score: 118,
      away_score: 106,
      arena: 'Rocket Mortgage FieldHouse',
      date: '20251118',
      time: '09:00',
    },
    team_stats: [
      {
        home_team_id: 'OT31242',
        home_team_name: 'Cleveland',
        home_team_fgm_cn: '45',
        home_team_fga_cn: '88',
        home_team_pgm3_cn: '12',
        home_team_pga3_cn: '30',
        home_team_ftm_cn: '16',
        home_team_fta_cn: '20',
        home_team_oreb_cn: '10',
        home_team_dreb_cn: '35',
        home_team_assist_cn: '28',
        home_team_turnover_cn: '12',
        home_team_steal_cn: '8',
        home_team_block_cn: '5',
        home_team_pfoul_cn: '18',
      },
      {
        away_team_id: 'OT31238',
        away_team_name: 'Milwaukee',
        away_team_fgm_cn: '40',
        away_team_fga_cn: '92',
        away_team_pgm3_cn: '10',
        away_team_pga3_cn: '35',
        away_team_ftm_cn: '16',
        away_team_fta_cn: '22',
        away_team_oreb_cn: '8',
        away_team_dreb_cn: '32',
        away_team_assist_cn: '22',
        away_team_turnover_cn: '15',
        away_team_steal_cn: '6',
        away_team_block_cn: '3',
        away_team_pfoul_cn: '20',
      },
    ],
    player_stats: [],
  };

  // Validate props with Zod
  try {
    const validatedProps = GameStatsPropsSchema.parse(externalProps);
    root.render(<App {...validatedProps} />);
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errorMessage = error.errors
        .map(err => `${err.path.join('.')}: ${err.message}`)
        .join('\n');
      root.render(<ErrorFallback error={errorMessage} />);
    } else {
      root.render(<ErrorFallback error="Unknown error occurred" />);
    }
  }
}

export default App;
