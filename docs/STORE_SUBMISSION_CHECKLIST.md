# Tradara 1.0 store submission checklist

## Apple App Privacy draft

Based on the current repository, disclose data linked to the user for **App
Functionality**:

- Contact info: email address.
- User content / other data: company profile text and private pipeline notes.
- Identifiers: Supabase account/user identifier.
- Other financial info: estimated job values and revenue targets may qualify;
  confirm in App Store Connect guidance at submission time.

Do not select tracking unless tracking or advertising technology is added.
Do not submit this draft until production hosting/logging behaviour and all SDKs
in the native build have been reviewed.

## Google Play Data safety draft

- Data collected: email, account identifier, company/profile fields, private
  pipeline records and user-entered estimated values.
- Purpose: account management and app functionality/personalisation.
- Data sharing: no sale or third-party advertising sharing appears in current
  code. Supabase acts as a service provider; confirm contractual treatment.
- Security: data encrypted in transit by HTTPS; confirm encryption at rest in
  the selected Supabase plan/project.
- Deletion: in-app deletion and `website/delete-account.html` are implemented,
  but remain release blockers until live-tested and the external page is
  published at a stable public URL.

## App Review test account instructions

Create a dedicated non-production review account only after the production
auth flow is stable. The review note should include:

1. How to sign in and whether email confirmation is required.
2. Profile, Radar, Pipeline, Insights and Account navigation steps.
3. A note that Radar uses public South Australian development information and
   provides prospecting signals, not guarantees.
4. How to change a password and permanently delete the review account.
5. Any temporary limitation in test data or public data availability.

Never commit review-account credentials to GitHub. Enter them directly in the
store review console.

## Owner decisions still required

- Legal entity/trading name and Australian business contact details.
- Privacy contact email and stable public website/domain.
- Retention periods and any lawful retention exceptions after account deletion.
- Whether analytics, crash reporting, subscriptions, payments or advertising
  ship in version 1.0.
- Final Privacy Policy and Terms of Use approval.
