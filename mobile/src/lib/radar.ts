// The same Location SA layer and scoring windows used by tradara_core.py.
const SOURCE = 'https://lsa4.geohub.sa.gov.au/server/rest/services/LSA/LocationSAViewerV34/MapServer/259/query';
const TRADE_INTEL: Record<string, { keywords: string[]; start: number; end: number; phase: string }> = {
  Earthworks: { keywords: ['land division', 'subdivision', 'earthworks'], start: 0, end: 3, phase: 'Site preparation' },
  Concreter: { keywords: ['dwelling', 'townhouse', 'units', 'apartment', 'building'], start: 1, end: 5, phase: 'Foundations / structure' },
  Bricklayer: { keywords: ['dwelling', 'townhouse', 'units', 'apartment', 'building'], start: 3, end: 8, phase: 'Structure / envelope' },
  Carpenter: { keywords: ['dwelling', 'townhouse', 'units', 'apartment', 'building'], start: 2, end: 8, phase: 'Framing / fit-out' },
  Roofer: { keywords: ['dwelling', 'townhouse', 'units', 'apartment', 'building'], start: 4, end: 9, phase: 'Building envelope' },
  Plumber: { keywords: ['dwelling', 'townhouse', 'units', 'apartment', 'building', 'commercial'], start: 3, end: 10, phase: 'Rough-in / fit-off' },
  Electrician: { keywords: ['dwelling', 'townhouse', 'units', 'apartment', 'building', 'commercial'], start: 3, end: 11, phase: 'Rough-in / fit-off' },
  HVAC: { keywords: ['apartment', 'commercial', 'shop', 'office', 'building', 'units'], start: 4, end: 11, phase: 'Services / fit-off' },
  Plasterer: { keywords: ['dwelling', 'townhouse', 'units', 'apartment', 'building'], start: 6, end: 11, phase: 'Internal fit-out' },
  Tiler: { keywords: ['dwelling', 'townhouse', 'units', 'apartment', 'building'], start: 7, end: 12, phase: 'Internal finishes' },
  Painter: { keywords: ['dwelling', 'townhouse', 'units', 'apartment', 'building'], start: 8, end: 13, phase: 'Finishes' },
  Landscaper: { keywords: ['dwelling', 'townhouse', 'units', 'apartment', 'land division', 'subdivision'], start: 9, end: 15, phase: 'External completion' },
  Fencer: { keywords: ['dwelling', 'townhouse', 'units', 'land division', 'subdivision'], start: 8, end: 15, phase: 'External completion' },
};
export const trades = Object.keys(TRADE_INTEL);
export type Profile = { preferred_trades?: string[]; preferred_project_types?: string[] } | null;
export type Opportunity = { score: number; action: string; trade: string; phase: string; development: string; description: string; decisionDate: string | null; sourceUrl: string; why: string };
type Attributes = Record<string, unknown>;

function validDate(value: unknown): Date | null {
  if (typeof value !== 'number' || !Number.isFinite(value) || value <= 0) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}
export function scoreFeatures(data: unknown, selected: string[], profile: Profile, now = new Date()): Opportunity[] {
  if (!data || typeof data !== 'object' || !('features' in data) || !Array.isArray(data.features)) return [];
  const rows: Opportunity[] = [];
  for (const feature of data.features) {
    const attributes: Attributes | undefined = feature && typeof feature === 'object' ? feature.attributes || feature.properties : undefined;
    if (!attributes || typeof attributes !== 'object') continue;
    const description = String(attributes.description || '');
    const lower = description.toLowerCase();
    const decisionDate = validDate(attributes.decisiondate);
    const ageMonths = decisionDate ? Math.max(0, (now.getTime() - decisionDate.getTime()) / 86400000 / 30.44) : null;
    for (const trade of selected) {
      const intel = TRADE_INTEL[trade];
      if (!intel) continue;
      const hits = intel.keywords.filter(keyword => lower.includes(keyword)).length;
      if (!hits) continue;
      let score = Math.min(40, 20 + hits * 7);
      if (/(approved|granted|consent)/.test(String(attributes.decision || '').toLowerCase())) score += 20;
      let action = 'VERIFY TIMING';
      if (ageMonths !== null) {
        if (ageMonths < intel.start) { action = 'CONTACT NOW — pre-position'; score += 20; }
        else if (ageMonths <= intel.end) { action = 'CONTACT NOW — trade window'; score += 30; }
        else if (ageMonths <= intel.end + 3) { action = 'LATE WINDOW — verify'; score += 8; }
        else { action = 'LIKELY PASSED — verify'; score -= 15; }
      }
      const reasons: string[] = [];
      if (profile) {
        if ((profile.preferred_project_types || []).some(type => lower.includes(type.toLowerCase()))) { score += 8; reasons.push('preferred project type'); }
        if ((profile.preferred_trades || []).includes(trade)) { score += 8; reasons.push('core company trade'); }
        if (action.startsWith('CONTACT NOW')) { score += 5; reasons.push('good timing'); }
      }
      const rawUrl = attributes.applicationurl || attributes.urlonly;
      const sourceUrl = typeof rawUrl === 'string' && /^https:\/\//i.test(rawUrl) ? rawUrl : '';
      rows.push({ score: Math.max(0, Math.min(100, score)), action, trade, phase: intel.phase,
        development: String(attributes.developmentnumber || 'Unknown'), description: description || 'No description',
        decisionDate: decisionDate?.toISOString().slice(0, 10) || null, sourceUrl,
        why: profile ? reasons.join(', ') || 'general company fit' : 'Complete your company profile to personalise this score' });
    }
  }
  return rows.sort((a, b) => b.score - a.score);
}

export async function fetchOpportunities(signal?: AbortSignal): Promise<unknown> {
  const params = new URLSearchParams({ where: '1=1', outFields: 'decision,description,developmentnumber,decisiondate,applicationurl,urlonly', returnGeometry: 'false', f: 'json', resultRecordCount: '1000', orderByFields: 'decisiondate DESC' });
  const response = await fetch(`${SOURCE}?${params}`, { signal });
  if (!response.ok) throw new Error(`Location SA returned ${response.status}`);
  const data: unknown = await response.json();
  if (!data || typeof data !== 'object' || !('features' in data) || !Array.isArray(data.features)) throw new Error('Location SA returned an unexpected response');
  return data;
}
