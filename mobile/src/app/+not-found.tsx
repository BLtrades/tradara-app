import { router } from 'expo-router';
import { Button, Heading, Page } from '../components/ui';

export default function NotFound() {
  return <Page>
    <Heading subtitle="This link is invalid or no longer available.">Page not found</Heading>
    <Button title="Return to Tradara" onPress={() => router.replace('/')} />
  </Page>;
}
