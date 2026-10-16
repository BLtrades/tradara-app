# Tradara 1.0 data inventory

This inventory reflects the application code and `supabase_schema.sql` on the
date of this document. It is the engineering source for Apple privacy labels,
Google Play Data safety answers and the public privacy policy. Re-check it
before every store submission.

## Data collected

| Data | Purpose | Linked to account | User can edit/delete |
|---|---|---:|---:|
| Email address and Supabase user ID | Authentication and account recovery | Yes | Email through Auth; account deletion pending live verification |
| Company name, base location and company description | Personalise opportunity rankings | Yes | Yes |
| Trades and preferred project types | Personalise opportunity rankings | Yes | Yes |
| Travel distance, job-value range and revenue target | Filtering and capacity planning | Yes | Yes |
| Saved development reference, trade, pipeline stage, notes and estimated value | Customer-managed sales pipeline | Yes | Yes |
| Record creation/update dates | Sync and ordering | Yes | Removed with associated record/account |

## Data not collected by current application code

- Precise GPS location, contacts, photos, microphone, camera or device identifiers.
- Payment-card or bank-account information.
- Advertising identifiers or cross-app tracking data.
- Health, biometric, government identity or sensitive demographic information.
- User-generated public content; pipeline data is private to its owner under RLS.

## Third parties and network services

- **Supabase:** authentication and Postgres storage. Production region,
  sub-processors, retention and backup behaviour must be confirmed in the
  Supabase project and reflected in the final privacy policy.
- **Location SA / PlanSA:** public development records are requested by the
  application. The current request contains no Tradara account identifier.
- **Streamlit hosting:** serves the application. Hosting logs and cookies must
  be checked against the production deployment before final disclosures.

## Security controls present in the repository

- Supabase Row Level Security restricts profile and pipeline rows to
  `auth.uid() = user_id`.
- Public clients use the Supabase anon key; a service-role key must never be
  shipped to web or mobile clients.
- Profile and pipeline foreign keys use `on delete cascade`.
- Automated schema checks require RLS coverage for select, insert, update and
  delete operations and keep account deletion authenticated and self-scoped.

## Required verification before declaring compliance

1. Test two separate accounts concurrently and prove neither can read or alter
   the other's records.
2. Apply and test the account-deletion function in draft PR #1 with a
   disposable account, including cascade behaviour and expired/remaining JWTs.
3. Confirm Supabase project region, backup retention and production log policy.
4. Confirm whether analytics, crash reporting, advertising or payments will be
   added; each changes the store disclosures.
5. Have the final privacy policy and retention wording reviewed by the product
   owner and qualified Australian counsel.
