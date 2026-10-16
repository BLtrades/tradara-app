# Tradara 1.0 device and store test plan

Use this runbook after the owner approves the permanent iOS bundle identifier
and Android package name and connects the relevant developer accounts. Record
the build URLs, device models, operating-system versions and test results in the
release ticket. Never commit signing credentials or review-account passwords.

## 1. Final configuration gate

1. Add `ios.bundleIdentifier` and `android.package` to `mobile/app.json`.
2. Add the Expo project owner and project ID produced by `eas init`.
3. In Supabase Auth, allow `tradara://reset-password` as a redirect URL.
4. Confirm the production Supabase URL uses only the publishable client key.
5. Run from `mobile/`:

       npm ci --legacy-peer-deps
       npm test
       npm run typecheck
       npm run lint
       EXPO_OFFLINE=1 npx expo-doctor

## 2. Installable preview builds

Create an Android APK and an iOS internal-distribution build:

    npx eas-cli@latest build --profile preview --platform android
    npx eas-cli@latest build --profile preview --platform ios

The iOS command requires an Apple Developer account and registered test device.
Install the resulting builds on at least one supported iPhone and one Android
phone. Do not treat Expo Go or a browser export as physical-device approval.

## 3. Required account and isolation tests

Use two disposable accounts, A and B:

- Create, confirm, sign in and sign out on both platforms.
- Save a distinct profile and pipeline item in each account.
- Confirm each record appears on web and phone for its owner.
- Confirm account A cannot read or change account B's profile or pipeline.
- Request password recovery, open the native deep link, set a new password and
  verify the old password no longer works.
- Delete account A in-app. Confirm its profile and pipeline rows are removed,
  its old session cannot access data and the email can be registered again.
- Repeat deletion for account B using the published HTTPS deletion page.

## 4. Product smoke tests

- Radar loads Location SA data and handles offline/server failure safely.
- Profile fields save, reload and affect opportunity ranking.
- Pipeline add, edit, status, notes and estimated value persist across devices.
- Settings, recovery, deletion, invalid links and back navigation work.
- Text is readable, controls meet touch-target expectations and keyboard input
  does not hide the focused field on both phone sizes.
- Relaunching after force-close restores a valid session without exposing a
  different user's data.

## 5. Store builds and review

After every item above passes:

    npx eas-cli@latest build --profile production --platform all
    npx eas-cli@latest submit --profile production --platform ios
    npx eas-cli@latest submit --profile production --platform android

Submit first to TestFlight and Google Play internal/closed testing. Complete the
privacy disclosures from `docs/STORE_SUBMISSION_CHECKLIST.md`, enter the review
account directly in each store console and keep PR #5 unmerged until the build,
legal, hosting and live Supabase gates are all approved.
