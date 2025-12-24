import type {
  BasketballTeamInfo,
  RecentGameResult,
  TeamComparisonData,
} from '../types';

interface TeamComparisonProps {
  homeTeam: BasketballTeamInfo;
  awayTeam: BasketballTeamInfo;
  teamComparison?: TeamComparisonData;
}

/**
 * 양팀 비교 컴포넌트
 * - 팀 헤더 (앰블럼만 표시)
 * - 최근 5경기
 * - 시즌 통계 비교 (승률, 평균 득점, 필드골% 등)
 */
export function TeamComparison({
  homeTeam,
  awayTeam,
  teamComparison,
}: TeamComparisonProps) {
  const hasRecentGames = homeTeam.recentGames?.length || awayTeam.recentGames?.length;

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      {/* 헤더 */}
      <div className="px-3 py-2 bg-gray-50 border-b border-gray-200">
        <h3 className="text-sm font-semibold text-gray-800">양팀 비교</h3>
      </div>

      {/* 팀 헤더 - 앰블럼만 크게 표시 */}
      <div className="px-4 py-3 border-b border-gray-100">
        <div className="flex items-center justify-center gap-8">
          {/* 홈팀 앰블럼 */}
          <TeamLogo team={homeTeam} size="lg" />

          {/* VS */}
          <span className="text-xl font-bold text-gray-400">VS</span>

          {/* 원정팀 앰블럼 */}
          <TeamLogo team={awayTeam} size="lg" />
        </div>
      </div>

      {/* 최근 5경기 */}
      {hasRecentGames && (
        <div className="px-4 py-3 border-b border-gray-100">
          <div className="text-xs font-medium text-gray-500 mb-2 text-center">최근 5경기</div>
          <div className="flex items-center justify-between">
            <RecentGamesDisplay games={homeTeam.recentGames} align="left" />
            <RecentGamesDisplay games={awayTeam.recentGames} align="right" />
          </div>
        </div>
      )}

      {/* 시즌 통계 비교 */}
      {teamComparison && (
        <div className="px-4 py-3">
          <div className="text-xs font-medium text-gray-500 mb-3 text-center">시즌 통계</div>
          <div className="space-y-3">
            <StatCompareRow
              label="승률"
              homeValue={formatPercent(teamComparison.home.winRate)}
              awayValue={formatPercent(teamComparison.away.winRate)}
              homeRaw={parseFloat(teamComparison.home.winRate)}
              awayRaw={parseFloat(teamComparison.away.winRate)}
            />
            <StatCompareRow
              label="평균 득점"
              homeValue={teamComparison.home.avgPoints.toFixed(1)}
              awayValue={teamComparison.away.avgPoints.toFixed(1)}
              homeRaw={teamComparison.home.avgPoints}
              awayRaw={teamComparison.away.avgPoints}
            />
            <StatCompareRow
              label="평균 실점"
              homeValue={teamComparison.home.avgPointsAgainst.toFixed(1)}
              awayValue={teamComparison.away.avgPointsAgainst.toFixed(1)}
              homeRaw={teamComparison.home.avgPointsAgainst}
              awayRaw={teamComparison.away.avgPointsAgainst}
              lowerIsBetter
            />
            <StatCompareRow
              label="필드골 %"
              homeValue={formatPercent(teamComparison.home.fgPct)}
              awayValue={formatPercent(teamComparison.away.fgPct)}
              homeRaw={parseFloat(teamComparison.home.fgPct)}
              awayRaw={parseFloat(teamComparison.away.fgPct)}
            />
            <StatCompareRow
              label="3점슛 %"
              homeValue={formatPercent(teamComparison.home.threePct)}
              awayValue={formatPercent(teamComparison.away.threePct)}
              homeRaw={parseFloat(teamComparison.home.threePct)}
              awayRaw={parseFloat(teamComparison.away.threePct)}
            />
            <StatCompareRow
              label="리바운드"
              homeValue={teamComparison.home.avgRebounds.toFixed(1)}
              awayValue={teamComparison.away.avgRebounds.toFixed(1)}
              homeRaw={teamComparison.home.avgRebounds}
              awayRaw={teamComparison.away.avgRebounds}
            />
            <StatCompareRow
              label="어시스트"
              homeValue={teamComparison.home.avgAssists.toFixed(1)}
              awayValue={teamComparison.away.avgAssists.toFixed(1)}
              homeRaw={teamComparison.home.avgAssists}
              awayRaw={teamComparison.away.avgAssists}
            />
          </div>
        </div>
      )}
    </div>
  );
}

// 팀 로고
function TeamLogo({ team, size = 'md' }: { team: BasketballTeamInfo; size?: 'sm' | 'md' | 'lg' }) {
  const sizeClass = size === 'sm' ? 'w-8 h-8' : size === 'lg' ? 'w-16 h-16' : 'w-10 h-10';
  const textSize = size === 'sm' ? 'text-[10px]' : size === 'lg' ? 'text-base' : 'text-xs';

  return (
    <div className={`${sizeClass} flex items-center justify-center`}>
      {team.logo ? (
        <img src={team.logo} alt={team.name} className={`${sizeClass} object-contain`} />
      ) : (
        <div
          className={`${sizeClass} rounded-full flex items-center justify-center ${textSize} font-semibold bg-blue-50 text-gray-600`}
        >
          {team.shortName.slice(0, 2)}
        </div>
      )}
    </div>
  );
}

// 최근 5경기 표시
function RecentGamesDisplay({
  games,
  align,
}: {
  games?: RecentGameResult[];
  align: 'left' | 'right';
}) {
  if (!games || games.length === 0) return null;

  return (
    <div className={`flex gap-1 ${align === 'right' ? 'flex-row-reverse' : ''}`}>
      {games.slice(0, 5).map((result, idx) => (
        <div
          key={idx}
          className={`w-6 h-6 flex items-center justify-center text-[11px] font-bold rounded ${
            result === 'W'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-600'
          }`}
        >
          {result}
        </div>
      ))}
    </div>
  );
}

// 통계 비교 행
function StatCompareRow({
  label,
  homeValue,
  awayValue,
  homeRaw,
  awayRaw,
  lowerIsBetter = false,
}: {
  label: string;
  homeValue: string;
  awayValue: string;
  homeRaw: number;
  awayRaw: number;
  lowerIsBetter?: boolean;
}) {
  // 우위 판단
  let homeBetter = homeRaw > awayRaw;
  if (lowerIsBetter) homeBetter = homeRaw < awayRaw;
  const awayBetter = !homeBetter && homeRaw !== awayRaw;

  return (
    <div className="flex items-center justify-between text-sm">
      <span className={homeBetter ? 'text-blue-600 font-bold' : 'text-gray-600'}>
        {homeValue}
      </span>
      <span className="text-xs text-gray-500">{label}</span>
      <span className={awayBetter ? 'text-blue-600 font-bold' : 'text-gray-600'}>
        {awayValue}
      </span>
    </div>
  );
}

// 퍼센트 포맷
// - 0.741 -> 74.1% (비율로 전달된 경우)
// - 58.60 -> 58.6% (이미 퍼센트로 전달된 경우)
function formatPercent(value: string): string {
  const num = parseFloat(value);
  if (isNaN(num)) return value;
  // 이미 퍼센트 값인지 확인 (1보다 크면 이미 퍼센트)
  if (num > 1) {
    return `${num.toFixed(1)}%`;
  }
  return `${(num * 100).toFixed(1)}%`;
}

export default TeamComparison;
