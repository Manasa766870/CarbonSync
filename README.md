# Carbon Sync — Streamlit starter

A starter frontend + Python backend + SQLite database for the Carbon Sync campus carbon-footprint project.

## Included
- Landing page
- Sign up and login (passwords are salted and PBKDF2-hashed)
- English, Telugu and Hindi interface labels
- User profile with hostel and department
- Chat interface with persistent message history
- SQLite database for users, messages and activities
- Agent HTTP client adapter to connect the AI agent running on another laptop

## Requirements
- Python 3.10+
- Internet access only when installing packages / contacting the remote agent

## Run locally (Windows PowerShell)

```powershell
cd Carbon_Sync
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

The app opens at `http://localhost:8501`. The SQLite database is created automatically at `data/carbon_sync.db`.

## Connect your teammate's AI agent

The frontend expects an HTTP endpoint configured as `AGENT_API_URL`.

Request JSON:
```json
{
  "message": "I travelled 5 km by bus today",
  "user_id": 1,
  "language": "en",
  "session_id": "a-session-identifier"
}
```

Expected response JSON:
```json
{
  "reply": "Your activity has been recorded..."
}
```

Ask the AI-agent teammate to expose a small HTTP API that accepts this request and returns this response. The API should authenticate requests before public deployment. If the agent is running on another laptop, `localhost` on your laptop will NOT point to their laptop. Use the teammate's reachable LAN IP or a deployed HTTPS URL, and ensure the firewall allows the port.

## Notes / next integration steps
- The chatbot stores conversation messages locally and calls the configured agent endpoint.
- Without `AGENT_API_URL`, it displays a clear "agent not connected" message instead of inventing carbon calculations.
- The activities table is ready for the Tracker Agent to write verified calculation results. The current starter dashboard does not fabricate activity records or emission totals.
- Add a campus admin role and consent/visibility rules before sharing individual or hostel/department data.
- For a real deployment, use HTTPS, secure secrets, proper authentication/session management, backups, and a production database. Streamlit's simple session login is a hackathon prototype, not production-grade identity management.
- Add verified, versioned emission-factor sources and their units/boundaries before calculating or comparing emissions.
