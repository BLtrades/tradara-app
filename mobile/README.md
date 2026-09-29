# Tradara mobile

Expo SDK 57 app sharing the web product's Supabase auth, `profiles`, and `pipeline` tables.

1. Apply `../supabase_schema.sql` in your Supabase project.
2. The client is configured with Tradara's Supabase project URL and publishable key. For an isolated test project, copy `.env.example` to `.env` and override both values. Never use a secret or service role key in a client.
3. Run `npm ci`, then `npx expo start`. Use an iOS or Android device/simulator.

Radar queries the same public Location SA layer as the web app and ranks matching developments locally. Run `npm test` to check scoring parity with the web core. The source must be reachable from the device; failures appear in the Radar screen.

For native password recovery, add `tradara://reset-password` to Supabase Auth's allowed redirect URLs, then test the email link in an installed development build. Expo Go is insufficient for validating the custom scheme. Release identifiers remain launch work. Do not submit this build yet. Account deletion requires the `delete_my_account` RPC from the schema to be installed by the project owner. Live authentication, RLS, and physical device flows need testing against the configured project.
