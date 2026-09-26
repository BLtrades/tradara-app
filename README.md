# Tradara — Construction Opportunity Intelligence

Tradara is a deploy-ready Streamlit application that turns South Australian
development information into personalised construction opportunity signals.

## Product modules

- Company Profile
- Tradara Radar
- Tradara Score / company-fit ranking
- Trade-window timing signals
- Sales Pipeline
- Capacity Planner
- Performance Intelligence
- Public SA development-data integration
- Marketing website in `/website`

## Recommended GitHub repository

`tradara-app`

Upload the CONTENTS of this ZIP to the repository root.

Required root files:

- `app.py`
- `requirements.txt`
- `runtime.txt`
- `.streamlit/config.toml`

## Streamlit deployment URL

For the BLtrades GitHub account on the `main` branch:

`https://github.com/BLtrades/tradara-app/blob/main/app.py`

## Run locally

    pip install -r requirements.txt
    streamlit run app.py

## Website

The `/website` folder contains the public marketing site.

After Streamlit gives you the public application URL, replace every `APP_URL`
inside `website/index.html` with that URL.

Recommended eventual structure:

- main brand website: `tradara.[your chosen domain]`
- application: `app.tradara.[your chosen domain]`

Domain availability and trademark clearance are not asserted by this package.

## Prototype storage

The running app uses Supabase authentication, profiles and pipeline records.
Apply `supabase_schema.sql` in the Supabase SQL Editor and configure the
`SUPABASE_URL` and public anon `SUPABASE_KEY` as Streamlit secrets. Never put
the service role key in Streamlit secrets. The unused legacy `cloud_store.py`
module has been removed.

## Accuracy

Tradara produces prospecting signals, not guarantees. A high Tradara Score does
not prove that a contractor is unappointed or that a project will commence at an
estimated time. Users should verify project and procurement information before
outreach.
