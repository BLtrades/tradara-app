# Tradara 1.0 — Store Release Plan

Goal: ship one Tradara product across web, iPhone and Android, backed by the same Supabase account and data model.

## Release gates

- [x] Supabase authentication foundation
- [x] Per-user profiles and pipeline with Row Level Security
- [x] Responsive web application
- [ ] Verify computer-to-phone cloud sync
- [x] Add Settings / Account screen
- [x] Add in-app account deletion
- [x] Add external account-deletion web page for Google Play
- [ ] Publish Privacy Policy and Terms of Use
- [x] Add password reset and account recovery
- [x] Add production error handling and empty/loading states
- [x] Complete mobile navigation and touch targets
- [ ] Add app icon, splash screen and store artwork (icons included; final store artwork pending)
- [x] Build native iOS/Android shell against Tradara backend
- [ ] Configure production bundle identifiers
- [ ] Test on physical iPhone and Android devices
- [ ] Complete Apple privacy disclosure
- [ ] Complete Google Play Data safety form
- [ ] Prepare App Review test account/instructions
- [ ] TestFlight release
- [ ] Google Play internal/closed testing release
- [ ] Production submission

## Engineering progress notes

- Store disclosure drafts and a code-derived data inventory are maintained in
  `/docs`. They are preparation material, not final legal approval.
- Installable web icons are included in `/website/icons`; native store artwork
  and splash screens remain open until the native shell and bundle IDs exist.
- The Expo mobile foundation now includes native Radar, Pipeline, Profile,
  Settings and recovery screens. Radar uses the Location SA layer and scoring
  windows used by the web app. Automated scoring checks pass, but real device
  and live Supabase flows remain release gates.
- An external account-deletion page is implemented under `/website` and has
  request-flow tests. It needs a stable HTTPS deployment and a live disposable
  account test before its Google Play gate can be checked.
- The native router now catches unexpected screen failures with a retry path;
  cloud-backed screens distinguish loading, empty and failure states.

## Architecture

Tradara Web / Tradara iOS / Tradara Android
                 |
              Supabase
     Auth + Postgres + RLS + user data

All clients must use the same account identity and cloud records. No production customer data should depend on local SQLite or device-only storage.

## Store compliance

Because Tradara supports account creation, account deletion must be readily discoverable. Apple requires users to be able to initiate account deletion in the app. Google Play requires an in-app deletion path plus an external web resource for deletion requests. Associated user data should be deleted unless retention is legitimately required and disclosed.

## Product standard before submission

Tradara should feel like a mobile product rather than a web page placed inside a generic wrapper. Core Radar, Pipeline, Profile and Settings flows must be touch-friendly and reliable. Authentication, privacy controls, account deletion, cloud persistence and recovery are release blockers.
