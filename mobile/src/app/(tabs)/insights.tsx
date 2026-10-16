import { useCallback, useState } from 'react';
import { useFocusEffect } from 'expo-router';
import { Text, View } from 'react-native';
import { Button, Heading, Loading, Message, Page, colors, styles } from '../../components/ui';
import { buildInsights, type InsightRow } from '../../lib/insights';
import { useSession } from '../../lib/session';
import { supabase } from '../../lib/supabase';

const money = (value: number) => `$${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;

export default function Insights() {
  const { session } = useSession();
  const [rows, setRows] = useState<InsightRow[]>([]); const [target, setTarget] = useState(50000);
  const [loading, setLoading] = useState(true); const [message, setMessage] = useState('');
  const refresh = useCallback(async () => {
    if (!supabase || !session) { setLoading(false); return; }
    setLoading(true); setMessage('');
    try {
      const [profile, pipeline] = await Promise.all([
        supabase.from('profiles').select('revenue_target').eq('user_id', session.user.id).maybeSingle(),
        supabase.from('pipeline').select('status,trade,est_value').eq('user_id', session.user.id),
      ]);
      if (profile.error) throw profile.error;
      if (pipeline.error) throw pipeline.error;
      setTarget(Number(profile.data?.revenue_target ?? 50000));
      setRows(pipeline.data || []);
    } catch { setMessage('Insights could not load. Check your connection and try again.'); }
    finally { setLoading(false); }
  }, [session]);
  useFocusEffect(useCallback(() => { void refresh(); }, [refresh]));
  const insight = buildInsights(rows, target);

  return <Page><Heading subtitle="Compare secured work with your target and learn from completed opportunities.">Capacity & performance</Heading>
    <Button title="Refresh insights" onPress={() => { void refresh(); }} disabled={loading} />
    <Message text={message} />
    {loading ? <Loading /> : <>
      <View style={styles.card}>
        <Text style={styles.label}>Capacity</Text>
        <Text style={{ color: colors.text, fontSize: 18 }}>Target: {money(insight.target)}</Text>
        <Text style={styles.muted}>Won: {money(insight.won)} · Unfilled: {money(insight.unfilled)}</Text>
        <Text style={styles.muted}>Quoted: {money(insight.quoted)} · Active opportunities: {insight.active}</Text>
      </View>
      <Text style={styles.label}>Performance by trade</Text>
      {!insight.performance.length && <Text style={styles.muted}>Mark opportunities Won or Lost to start measuring performance.</Text>}
      {insight.performance.map(row => <View key={row.trade} style={styles.card}>
        <Text style={{ color: colors.text, fontSize: 18, fontWeight: '700' }}>{row.trade}</Text>
        <Text style={styles.muted}>{row.wins} wins from {row.decisions} decisions · {Math.round(row.winRate * 100)}% win rate</Text>
      </View>)}
    </>}
  </Page>;
}
