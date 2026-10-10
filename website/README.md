# Tradara Website

`website/index.html` is a standalone responsive marketing site.

## Link it to the app

After deploying the Streamlit app, copy its public URL.

Open `website/index.html` and replace every occurrence of:

    APP_URL

with the deployed Streamlit URL, for example:

    https://your-app.streamlit.app

Then deploy the `website` folder to any static host (Cloudflare Pages, Netlify,
GitHub Pages, your own web host, etc.).

For a polished production setup, use:
- `tradara.com.au` -> marketing website
- `app.tradara.com.au` -> application

No domain name is included in this package.

## Account deletion page

`delete-account.html` provides a web path to permanently delete a Tradara
account, company profile and pipeline without reinstalling the app. It uses
the project's publishable Supabase key and keeps the signed-in token only in
memory for the deletion request. Serve it and its two `.mjs` files over HTTPS
on the same host as the marketing site. Do not add a secret or service-role key.

Before listing its public URL in Google Play, verify that
`supabase_schema.sql` has installed `delete_my_account`, test deletion with a
disposable account, and confirm the cascaded records are gone. The public URL
must stay available after launch. A built page in this repository is not yet
a published deletion resource.
