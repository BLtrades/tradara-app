export type InsightRow = { status: string; trade: string; est_value: number | string | null };

export function buildInsights(rows: InsightRow[], revenueTarget: number) {
  const target = Number.isFinite(revenueTarget) && revenueTarget >= 0 ? revenueTarget : 0;
  let won = 0; let quoted = 0; let active = 0;
  const trades = new Map<string, { decisions: number; wins: number }>();

  for (const row of rows) {
    const value = Number(row.est_value);
    const amount = Number.isFinite(value) && value > 0 ? value : 0;
    if (row.status === 'Won') won += amount;
    if (row.status === 'Quoted') quoted += amount;
    if (['Saved', 'Contacted', 'Quoted'].includes(row.status)) active += 1;
    if (row.status === 'Won' || row.status === 'Lost') {
      const trade = row.trade.trim() || 'Unspecified';
      const current = trades.get(trade) || { decisions: 0, wins: 0 };
      current.decisions += 1;
      if (row.status === 'Won') current.wins += 1;
      trades.set(trade, current);
    }
  }

  const performance = [...trades.entries()].map(([trade, result]) => ({
    trade,
    ...result,
    winRate: result.wins / result.decisions,
  })).sort((a, b) => b.decisions - a.decisions || a.trade.localeCompare(b.trade));

  return { target, won, quoted, active, unfilled: Math.max(0, target - won), performance };
}
