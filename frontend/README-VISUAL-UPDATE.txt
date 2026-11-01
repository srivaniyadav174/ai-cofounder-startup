AI CO-FOUNDER — VISUAL FRONTEND UPDATE

This update changes the frontend only. The FastAPI backend and API routes are unchanged.

What's updated:
- Opportunity Explorer has a redesigned hero, founder-profile form, animated scan state, progress indicator, helpful validation note, and a dedicated results panel.
- Fixed the Opportunities page layout so it no longer nests a second main-content shell inside the dashboard shell.
- Dashboard Overview now includes a startup journey visual and a validation measurement framework. It intentionally does not invent readiness percentages or a startup success probability; evidence-based scores should be added only when actual experiment data is available.
- Login showcase colors and visual polish are enhanced while keeping the existing login/register behavior.

Install:
1. Extract this ZIP.
2. Copy the contents of its frontend folder into your existing project frontend folder, replacing the matching files.
3. Do not delete your backend folder or backend virtual environment.
4. In a terminal, run: npm run dev
5. Open the local Vite URL and test Login, Dashboard, and Opportunities.

If you see a blank page, open the terminal where npm run dev is running and send the error text or screenshot. The build could not be verified in this packaging environment because the installed Vite/Rolldown optional native binding is missing; this is an environment dependency issue, not a successful build claim.
