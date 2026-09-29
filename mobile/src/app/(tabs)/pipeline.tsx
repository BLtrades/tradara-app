import { useCallback, useState } from 'react';
import { useFocusEffect } from 'expo-router';
import { Alert, Pressable, Text, View } from 'react-native';
import { Button, Field, Heading, Message, Page, colors, styles } from '../../components/ui';
import { supabase } from '../../lib/supabase';
import { useSession } from '../../lib/session';

type Lead = { id: number; development: string; trade: string; status: string; notes: string; est_value: number };
const statuses = ['Saved', 'Contacted', 'Quoted', 'Won', 'Lost', 'Not relevant'];
export default function Pipeline() {
  const { session } = useSession(); const [rows, setRows] = useState<Lead[]>([]); const [development, setDevelopment] = useState('');
  const [trade, setTrade] = useState(''); const [message, setMessage] = useState(''); const [busy, setBusy] = useState(false);
  const [editing, setEditing] = useState<number | null>(null); const [notes, setNotes] = useState('');
  const refresh = useCallback(async () => {
    if (!supabase || !session) return;
    const { data, error } = await supabase.from('pipeline').select('id,development,trade,status,notes,est_value').eq('user_id', session.user.id).order('last_updated', { ascending: false });
    if (error) setMessage(error.message); else setRows(data || []);
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
  function edit(row: Lead) { setEditing(row.id); setNotes(row.notes); }
  return <Page><Heading subtitle="Track each lead from saved to won.">Pipeline</Heading>
    <Field label="Development" value={development} onChangeText={setDevelopment} placeholder="Project or development name" />
    <Field label="Trade" value={trade} onChangeText={setTrade} placeholder="Electrical, plumbing…" />
    <Button title="Add opportunity" onPress={add} disabled={busy || !development.trim() || !trade.trim()} /><Message text={message} />
    {rows.length === 0 && <Text style={styles.muted}>No saved opportunities yet.</Text>}
    {rows.map(row => <View key={row.id} style={styles.card}>
      <Text style={{ color: colors.text, fontSize: 18, fontWeight: '700' }}>{row.development}</Text><Text style={styles.muted}>{row.trade} · {row.status}</Text>
      {!!row.notes && <Text style={styles.muted}>{row.notes}</Text>}
      <Pressable accessibilityRole="button" onPress={() => Alert.alert('Move opportunity', undefined, statuses.map(status => ({ text: status, onPress: () => { void update(row, { status }); } })).concat([{ text: 'Cancel', onPress: () => {} }]))}><Text style={{ color: colors.accent, paddingVertical: 10 }}>Change status</Text></Pressable>
      {editing === row.id ? <><Field label="Notes" value={notes} onChangeText={setNotes} multiline /><Button title="Save notes" onPress={() => { void update(row, { notes }); setEditing(null); }} /></> : <Button title="Edit notes" onPress={() => edit(row)} />}
    </View>)}
  </Page>;
}
