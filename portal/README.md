# Enterprise Code Review Portal

Microsoft-style review console that wraps the Open Code Review (`ocr`) CLI.

## Run locally

From the repository root, in PowerShell:

```powershell
.\portal\start.ps1
```

Or start the two processes yourself:

```powershell
# API — http://127.0.0.1:8080
python -m pip install -r portal\backend\requirements.txt
python -m uvicorn app.main:app --app-dir portal\backend --host 127.0.0.1 --port 8080

# UI — http://127.0.0.1:5173
cd portal\frontend
npm install
npm run dev
```

Open **http://127.0.0.1:5173**. The UI proxies `/api` to the backend.

## Inputs

- **Git HTTPS URL** on github.com, gitlab.com, dev.azure.com, or bitbucket.org
- **Local folder** on this machine (default sample: `portal/fixtures/sample-python`)

## Configuration

LLM settings come from the root `.env` file (`AZURE_OPENAI_*`). The API key is never shown in the UI.

Authentication defaults to `AUTH_MODE=dev_bypass`. To require Microsoft Entra ID:

```
AUTH_MODE=entra
AZURE_TENANT_ID=...
AZURE_CLIENT_ID=...
```

Optional local-path allowlist:

```
PORTAL_LOCAL_ROOTS=C:\src,C:\Parag-Personal
```

If unset, any existing non-system directory on this machine can be scanned (workstation mode).
