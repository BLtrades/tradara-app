import { useCallback, useState } from 'react';
import { useFocusEffect } from 'expo-router';
import { Alert, Pressable, Text, View } from 'react-native';
import { Button, Field, Heading, Loading, Message, Page, colors, styles } from '../../components/ui';
import { supabase } from '../../lib/supabase';
import { useSession } from '../../lib/session';

type Lead = { id: number; development: string; trade: string; status: string; notes: string; est_value: number };
const statuses = ['Saved', 'Contacted', 'Quoted', 'Won', 'Lost', 'Not relevant'];
export default function Pipeline() {
  const { session } = useSession(); const [rows, setRows] = useState<Lead[]>([]); const [development, setDevelopment] = useState('');
  const [trade, setTrade] = useState(''); const [message, setMessage] = useState(''); const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<number | null>(null); const [notes, setNotes] = useState(''); const [value, setValue] = useState('');
  const [choosing, setChoosing] = useState<number | null>(null);
  const refresh = useCallback(async () => {
    if (!supabase || !session) { setLoading(false); return; }
    setLoading(true);
    try {
      const { data, error } = await supabase.from('pipeline').select('id,development,trade,status,notes,est_value').eq('user_id', session.user.id).order('last_updated', { ascending: false });
      if (error) setMessage(error.message); else setRows(data || []);
    } catch { setMessage('Pipeline could not load. Check your connection and try again.'); }
    finally { setLoading(false); }
  }, [session]);
  useFocusEffect(useCallback(() => { void refresh(); }, [refresh]));
  async function add() {
    if (!supabase || !session || !development.trim() || !trade.trim()) return;
    setBusy(true);
    const { error } = await supabase.from('pipeline').insert({ user_id: session.user.id, development: development.trim(), trade: trade.trim() });
    setMessage(error?.message ?? 'Opportunity saved.'); if (!error) { setDevelopment(''); setTrade(''); await refresh(); } setBusy(false);
  }
  async function update(row: Lead, changes: Partial<Lead>) {
    if (!supabase || !session) return;
    const { error } = await supabase.from('pipeline').update({ ...changes, last_updated: new Date().toISOString().slice(0, 10) }).eq('id', row.id).eq('user_id', session.user.id);
    setMessage(error?.message ?? 'Pipeline updated.'); if (!error) await refresh();
  }
  function edit(row: Lead) { setEditing(row.id); setNotes(row.notes); setValue(String(row.est_value)); }
  async function saveDetails(row: Lead) {
    const amount = Number(value);
    if (!Number.isFinite(amount) || amount < 0) { setMessage('Enter a valid estimated value.'); return; }
    await update(row, { notes, est_value: amount }); setEditing(null);
  }
  function remove(row: Lead) { Alert.alert('Remove opportunity?', `${row.development} will be removed from your pipeline.`, [
    { text: 'Cancel', style: 'cancel' }, { text: 'Remove', style: 'destructive', onPress: async () => {
      if (!supabase || !session) return;
      const { error } = await supabase.from('pipeline').delete().eq('id', row.id).eq('user_id', session.user.id);
      setMessage(error?.message ?? 'Opportunity removed.'); if (!error) await refresh();
    } },
  ]); }
  return <Page><Heading subtitle="Track each lead from saved to won.">Pipeline</Heading>
    <Field label="Development" value={development} onChangeText={setDevelopment} placeholder="Project or development name" />
    <Field label="Trade" value={trade} onChangeText={setTrade} placeholder="Electrical, plumbing…" />
    <Button title="Add opportunity" onPress={add} disabled={busy || !development.trim() || !trade.trim()} /><Message text={message} />
    {loading && <Loading />}
    {!loading && rows.length === 0 && <Text style={styles.muted}>No saved opportunities yet.</Text>}
    {rows.map(row => <View key={row.id} style={styles.card}>
      <Text style={{ color: colors.text, fontSize: 18, fontWeight: '700' }}>{row.development}</Text><Text style={styles.muted}>{row.trade} · {row.status}</Text>
      {!!row.notes && <Text style={styles.muted}>{row.notes}</Text>}
      <Text style={styles.muted}>Estimated value: ${Number(row.est_value || 0).toLocaleString()}</Text>
      <Pressable accessibilityRole="button" onPress={() => setChoosing(choosing === row.id ? null : row.id)}><Text style={{ color: colors.accent, paddingVertical: 10 }}>Change status</Text></Pressable>
      {choosing === row.id && <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8 }}>{statuses.map(status => <Pressable key={status} accessibilityRole="button" onPress={() => { void update(row, { status }); setChoosing(null); }}
        style={{ padding: 12, borderRadius: 12, backgroundColor: status === row.status ? colors.accent : colors.bg }}><Text style={{ color: status === row.status ? colors.bg : colors.text }}>{status}</Text></Pressable>)}</View>}
      {editing === row.id ? <><Field label="Notes" value={notes} onChangeText={setNotes} multiline /><Field label="Estimated value ($)" value={value} onChangeText={setValue} keyboardType="numeric" /><Button title="Save details" onPress={() => { void saveDetails(row); }} /></> : <Button title="Edit details" onPress={() => edit(row)} />}
      <Button title="Remove opportunity" onPress={() => remove(row)} danger />
    </View>)}
  </Page>;
}
