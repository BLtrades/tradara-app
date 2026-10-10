import { useCallback, useEffect, useState } from 'react';
import { Linking, Pressable, Text, View } from 'react-native';
import { useFocusEffect } from 'expo-router';
import { Button, Heading, Loading, Message, Page, colors, styles } from '../../components/ui';
import { useSession } from '../../lib/session';
import { supabase } from '../../lib/supabase';
import { fetchOpportunities, scoreFeatures, trades, type Opportunity, type Profile } from '../../lib/radar';

export default function Radar() {
  const { session } = useSession();
  const [profile, setProfile] = useState<Profile>(null);
  const [selected, setSelected] = useState<string[]>(['Electrician']);
  const [data, setData] = useState<unknown>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [saved, setSaved] = useState<string[]>([]);

  useFocusEffect(useCallback(() => {
    let active = true;
    if (supabase && session) supabase.from('profiles').select('preferred_trades,preferred_project_types').eq('user_id', session.user.id).maybeSingle().then(({ data: next, error }) => {
      if (!active) return;
      if (error) { setMessage(error.message); return; }
      setProfile(next);
      const preferred = (next?.preferred_trades || []).filter((trade: string) => trades.includes(trade));
      if (preferred.length) setSelected(preferred);
    });
    return () => { active = false; };
  }, [session]));

  useEffect(() => {
    const controller = new AbortController();
    fetchOpportunities(controller.signal).then(next => { setData(next); setMessage(''); })
      .catch(error => { if (!controller.signal.aborted) setMessage(`Radar could not load: ${error instanceof Error ? error.message : 'try again'}`); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, []);

  async function refresh() {
    setLoading(true); setMessage('');
    try { setData(await fetchOpportunities()); }
    catch (error) { setMessage(`Radar could not load: ${error instanceof Error ? error.message : 'try again'}`); }
    finally { setLoading(false); }
  }
  async function save(row: Opportunity) {
    if (!supabase || !session) return;
    try {
      const { error } = await supabase.from('pipeline').upsert({ user_id: session.user.id, development: row.development, trade: row.trade, status: 'Saved' }, { onConflict: 'user_id,development,trade', ignoreDuplicates: true });
      if (error) setMessage(error.message);
      else { setSaved(previous => [...previous, `${row.development}:${row.trade}`]); setMessage('Saved to your pipeline.'); }
    } catch { setMessage('Opportunity could not be saved. Check your connection and try again.'); }
  }
  const opportunities = scoreFeatures(data, selected, profile).filter(row => row.score >= 55).slice(0, 15);
  return <Page><Heading subtitle="Recent South Australian development decisions. Verify each project before contacting anyone.">Opportunity Radar</Heading>
    <Text style={styles.label}>Your trades</Text>
    <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8 }}>{trades.map(trade => <Pressable key={trade} accessibilityRole="checkbox" accessibilityState={{ checked: selected.includes(trade) }}
      onPress={() => setSelected(previous => previous.includes(trade) ? previous.filter(item => item !== trade) : [...previous, trade])}
      style={{ borderColor: colors.border, borderWidth: 1, borderRadius: 18, paddingHorizontal: 12, paddingVertical: 10, backgroundColor: selected.includes(trade) ? colors.accent : colors.card }}>
      <Text style={{ color: selected.includes(trade) ? colors.bg : colors.text }}>{trade}</Text></Pressable>)}</View>
    <Button title="Refresh opportunities" onPress={() => { void refresh(); }} disabled={loading} /><Message text={message} />
    {loading && <Loading />}
    {!loading && !opportunities.length && <Text style={styles.muted}>No matches at 55 points for these trades. Try another trade or refresh the source.</Text>}
    {opportunities.map((row, index) => <View key={`${row.development}:${row.trade}:${index}`} style={styles.card}>
      <Text style={{ color: colors.accent, fontSize: 22, fontWeight: '700' }}>{row.score}/100 · {row.trade}</Text>
      <Text style={{ color: colors.text, fontWeight: '700' }}>{row.action} · {row.phase}</Text>
      <Text style={styles.muted}>{row.description}</Text>
      <Text style={styles.muted}>Application {row.development}{row.decisionDate ? ` · decision ${row.decisionDate}` : ''}</Text>
      <Text style={styles.muted}>Why it fits: {row.why}</Text>
      {row.sourceUrl ? <Button title="Verify project at source" onPress={() => { void Linking.openURL(row.sourceUrl).catch(() => setMessage('Could not open the project link.')); }} /> : null}
      <Button title={saved.includes(`${row.development}:${row.trade}`) ? 'Saved' : 'Save to pipeline'} disabled={saved.includes(`${row.development}:${row.trade}`)} onPress={() => { void save(row); }} />
    </View>)}
    <Text style={styles.muted}>Source: Location SA development applications. Scores and timing are prospecting signals, not confirmation of available work.</Text>
  </Page>;
}
