import { ActivityIndicator, KeyboardAvoidingView, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, View, type TextInputProps } from 'react-native';
import type { ReactNode } from 'react';
import { SafeAreaView, type Edge } from 'react-native-safe-area-context';

export const colors = { bg: '#10162e', card: '#1b2544', text: '#f5f7ff', muted: '#aeb9d2', accent: '#82e3bb', border: '#34415f', danger: '#ffacac' };
export function Page({ children, safeTop = false }: { children: ReactNode; safeTop?: boolean }) {
  const edges: Edge[] = safeTop ? ['top', 'right', 'bottom', 'left'] : ['right', 'bottom', 'left'];
  return <SafeAreaView style={styles.safeArea} edges={edges}>
    <KeyboardAvoidingView style={styles.safeArea} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      <ScrollView keyboardShouldPersistTaps="handled" keyboardDismissMode={Platform.OS === 'ios' ? 'interactive' : 'on-drag'} contentContainerStyle={styles.page}>{children}</ScrollView>
    </KeyboardAvoidingView>
  </SafeAreaView>;
}
export function Heading({ children, subtitle }: { children: ReactNode; subtitle?: string }) { return <View style={styles.heading}><Text style={styles.title}>{children}</Text>{subtitle && <Text style={styles.muted}>{subtitle}</Text>}</View>; }
export function Field({ label, ...props }: TextInputProps & { label: string }) { return <View style={styles.field}><Text style={styles.label}>{label}</Text><TextInput accessibilityLabel={props.accessibilityLabel || label} placeholderTextColor={colors.muted} style={[styles.input, props.multiline && { minHeight: 94, textAlignVertical: 'top' }]} {...props} /></View>; }
export function Button({ title, onPress, disabled, danger }: { title: string; onPress: () => void; disabled?: boolean; danger?: boolean }) { return <Pressable accessibilityRole="button" accessibilityLabel={title} accessibilityState={{ disabled: !!disabled }} disabled={disabled} onPress={onPress} style={[styles.button, danger && { backgroundColor: colors.danger }, disabled && { opacity: .5 }]}><Text style={styles.buttonText}>{title}</Text></Pressable>; }
export function Message({ text }: { text: string }) { return text ? <Text accessibilityRole="alert" style={styles.message}>{text}</Text> : null; }
export function Loading() { return <View accessibilityRole="progressbar" accessibilityLabel="Loading" style={styles.center}><ActivityIndicator color={colors.accent} /></View>; }
export const styles = StyleSheet.create({ safeArea: { flex: 1, backgroundColor: colors.bg }, page: { flexGrow: 1, backgroundColor: colors.bg, padding: 22, gap: 16 }, heading: { gap: 6, marginVertical: 12 }, title: { color: colors.text, fontSize: 28, fontWeight: '700' }, muted: { color: colors.muted, fontSize: 15, lineHeight: 22 }, label: { color: colors.text, fontSize: 15, marginBottom: 7 }, field: { marginBottom: 5 }, input: { color: colors.text, borderWidth: 1, borderColor: colors.border, borderRadius: 12, paddingHorizontal: 14, paddingVertical: 12, minHeight: 48, fontSize: 16 }, button: { backgroundColor: colors.accent, padding: 14, minHeight: 48, borderRadius: 12, alignItems: 'center', justifyContent: 'center' }, buttonText: { color: colors.bg, fontSize: 16, fontWeight: '700' }, message: { color: colors.danger, fontSize: 14 }, card: { backgroundColor: colors.card, borderRadius: 14, padding: 16, gap: 8 }, center: { flex: 1, backgroundColor: colors.bg, justifyContent: 'center' } });
