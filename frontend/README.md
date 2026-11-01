# AI Co-Founder for Startups — Frontend

React + Vite frontend for the AI Co-Founder startup workspace.

## Run locally

1. Open this folder in a terminal.
2. Install dependencies with `npm install`.
3. Start the frontend with `npm run dev`.
4. Open the local URL Vite prints (typically `http://localhost:5173`).

The API client currently targets `http://127.0.0.1:8000`. The backend must be running.

## Included updates

- Rebranded the sidebar and browser title to AI Co-Founder for Startups.
- Dashboard greeting and account verification use the backend `/auth/me` endpoint.
- Settings displays account details, session controls, and a saved greeting preference.
- Login and registration use a shared responsive visual design.
- Existing startup workflow pages and AI chat are retained.

Note: this frontend update does not add backend profile-editing or password-reset endpoints.
