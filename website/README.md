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
