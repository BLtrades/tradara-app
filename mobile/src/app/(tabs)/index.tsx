import { Text, View } from 'react-native';
import { Heading, Page, styles } from '../../components/ui';

export default function Radar() { return <Page><Heading subtitle="Construction opportunities in South Australia.">Opportunity Radar</Heading>
  <View style={styles.card}><Text style={styles.muted}>Native project discovery is being connected to Tradara’s public project sources. Your company preferences and saved pipeline are available in the other tabs.</Text></View>
</Page>; }
