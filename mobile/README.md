# Tradara mobile

Expo SDK 57 app sharing the web product's Supabase auth, `profiles`, and `pipeline` tables.

1. Apply `../supabase_schema.sql` in your Supabase project.
2. Copy `.env.example` to `.env` and set the project URL and publishable/anon key. Never use the service role key in a client.
3. Run `npm ci`, then `npx expo start`. Use an iOS or Android device/simulator.

The native Radar source adapter, cross-platform pipeline notes editor, password recovery and release identifiers remain launch work. Do not submit this build yet. Account deletion requires the `delete_my_account` RPC from the schema to be installed by the project owner.
