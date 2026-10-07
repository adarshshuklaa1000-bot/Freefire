# Free Fire Like — GitHub + Vercel

This is the final Flask + HTML version.

## Files

- `app.py` — Flask website and same-origin API proxy
- `requirements.txt` — Python dependencies
- `templates/index.html` — responsive UI

## Vercel deployment

Vercel currently supports Flask with zero configuration. Put the project files in a GitHub repository and import that repository into Vercel.

No Termux is required for deployment.

## Important

The browser calls:

`/api/like`

The Flask server then calls:

`https://free-fire-ob55-like-api.vercel.app/like`

This keeps the browser from directly making a cross-origin request to the upstream API.

If the upstream API returns an application error such as:

`{"error":"Invalid UID or server","status":0}`

the website will show that error. A proxy cannot turn an upstream failure into a successful request.

## Health check

After deployment, opening `/health` should return:

`{"ok":true}`
