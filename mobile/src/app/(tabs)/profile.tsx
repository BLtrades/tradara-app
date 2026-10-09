import { useCallback, useState } from 'react';
import { useFocusEffect } from 'expo-router';
import { Button, Field, Heading, Loading, Message, Page } from '../../components/ui';
import { supabase } from '../../lib/supabase';
import { useSession } from '../../lib/session';

export default function Profile() {
  const { session } = useSession(); const [name, setName] = useState(''); const [location, setLocation] = useState('');
  const [description, setDescription] = useState(''); const [trades, setTrades] = useState(''); const [types, setTypes] = useState('');
  const [distance, setDistance] = useState('50'); const [minValue, setMinValue] = useState('5000'); const [maxValue, setMaxValue] = useState('250000');
  const [target, setTarget] = useState('50000'); const [message, setMessage] = useState(''); const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  useFocusEffect(useCallback(() => {
    let active = true;
    if (supabase && session) void (async () => {
      try {
        const { data, error } = await supabase.from('profiles').select('*').eq('user_id', session.user.id).maybeSingle();
        if (!active) return;
        if (error) { setMessage(error.message); return; }
        if (data) { setName(data.company_name); setLocation(data.base_location); setDescription(data.company_description); setTrades(data.preferred_trades.join(', ')); setTypes(data.preferred_project_types.join(', ')); setDistance(String(data.max_distance_km)); setMinValue(String(data.min_job_value)); setMaxValue(String(data.max_job_value)); setTarget(String(data.revenue_target)); }
      } catch {
        if (active) setMessage('Profile could not load. Check your connection and try again.');
      } finally {
        if (active) setLoading(false);
      }
    })();
    else setLoading(false);
    return () => { active = false; };
  }, [session]));
  async function save() {
    if (!supabase || !session) return;
    const km = Number(distance); const minimum = Number(minValue); const maximum = Number(maxValue); const revenue = Number(target);
    if (![km, minimum, maximum, revenue].every(value => Number.isFinite(value) && value >= 0)) { setMessage('Enter valid non-negative profile values.'); return; }
    if (minimum > maximum) { setMessage('Minimum job value cannot exceed the maximum.'); return; }
    setBusy(true); setMessage('');
    try {
      const split = (value: string) => value.split(',').map(x => x.trim()).filter(Boolean);
      const { error } = await supabase.from('profiles').upsert({ user_id: session.user.id, company_name: name.trim(), base_location: location.trim(), company_description: description.trim(), preferred_trades: split(trades), preferred_project_types: split(types), max_distance_km: km, min_job_value: minimum, max_job_value: maximum, revenue_target: revenue, updated_at: new Date().toISOString() });
      setMessage(error?.message ?? 'Profile saved.');
    } catch { setMessage('Profile could not be saved. Check your connection and try again.'); }
    finally { setBusy(false); }
  }
  return <Page><Heading subtitle="Your preferences shape your opportunity matches.">Company profile</Heading>
    {loading && <Loading />}
    <Field label="Company name" value={name} onChangeText={setName} />
    <Field label="Base location" value={location} onChangeText={setLocation} placeholder="Adelaide, SA" />
    <Field label="Services" value={description} onChangeText={setDescription} multiline />
    <Field label="Trades (comma separated)" value={trades} onChangeText={setTrades} />
    <Field label="Preferred project types (comma separated)" value={types} onChangeText={setTypes} />
    <Field label="Maximum distance (km)" value={distance} onChangeText={setDistance} keyboardType="numeric" />
    <Field label="Minimum job value ($)" value={minValue} onChangeText={setMinValue} keyboardType="numeric" />
    <Field label="Maximum job value ($)" value={maxValue} onChangeText={setMaxValue} keyboardType="numeric" />
    <Field label="Revenue target ($)" value={target} onChangeText={setTarget} keyboardType="numeric" />
    <Message text={message} /><Button title="Save profile" onPress={save} disabled={busy} />
  </Page>;
}
