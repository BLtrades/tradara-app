# Tradara 1.0 — Step 1: Account Foundation

Target: a secure, recoverable, cross-device customer account before beta.

## Build checklist

- [x] Supabase email/password authentication
- [x] Row Level Security for profiles and pipeline
- [x] Cloud company profiles
- [x] Cloud pipeline
- [x] Session restore helpers
- [x] Password reset helper
- [x] Password update helper
- [x] Email update helper
- [x] Pipeline record deletion helper
- [x] Customer-data deletion helper
- [ ] Add account/settings UI to app.py
- [ ] Add Forgot Password UI
- [ ] Add password recovery callback flow
- [ ] Add change-password UI
- [ ] Add destructive-action confirmation UI
- [ ] Add protected server-side auth-user deletion function
- [ ] Test login on desktop and mobile
- [ ] Test same profile/pipeline on two devices
- [ ] Test logout and expired-session recovery
- [ ] Test RLS using two separate accounts

## Release gate

Step 1 is complete only when two different test accounts cannot read or mutate one another's profile/pipeline, password recovery works, and the same account reliably sees the same cloud data across phone and desktop.
