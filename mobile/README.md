# Tradara mobile

Expo SDK 57 app sharing the web product's Supabase auth, `profiles`, and `pipeline` tables.

1. Apply `../supabase_schema.sql` in your Supabase project.
2. The client is configured with Tradara's Supabase project URL and publishable key. For an isolated test project, copy `.env.example` to `.env` and override both values. Never use a secret or service role key in a client.
3. Run `npm ci`, then `npx expo start`. Use an iOS or Android device/simulator.

The native Radar source adapter, password recovery and release identifiers remain launch work. Do not submit this build yet. Account deletion requires the `delete_my_account` RPC from the schema to be installed by the project owner. Live authentication and RLS need testing against the configured project.
