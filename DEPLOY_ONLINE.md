# Deploy AI Resume Checker Online

## 1) Push project to GitHub

1. Create a new GitHub repo.
2. Upload this project folder.
3. Keep these files in repo:
   - `app.py`
   - `requirements.txt`
   - `.streamlit/config.toml`
4. Do **not** upload `.env` (already ignored).

## 2) Option A: Streamlit Community Cloud (easiest)

1. Go to https://share.streamlit.io
2. Connect your GitHub account and select this repository.
3. Main file path: `app.py`
4. In **Advanced settings > Secrets**, add:

```toml
GEMINI_API_KEY = "your_real_key_here"
```

5. Click **Deploy**.

## 3) Option B: Render (more control)

1. Go to https://render.com and create a **Web Service**.
2. Connect GitHub repo.
3. Configure:
   - Build command: `pip install -r requirements.txt`
   - Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
4. Add environment variable:
   - `GEMINI_API_KEY=your_real_key_here`
5. Deploy service.
45 x 5
1 Hidden Terminal
I UPLOADED ALL FILES OF THE AI REMUME CHEAKER FOLDER

Perfect — now do these exact next steps to make it live online:

Click the green Commit changes button (you are on that screen now).
After commit, open https://share.streamlit.io


## 4) Important notes for your current app

- Your app uses local JSON files (`users.json`, `jobs.json`, `applications.json`, etc.) as storage.
- On free cloud instances, file changes may reset after restart/redeploy.
- For production, move storage to a real DB (PostgreSQL/MongoDB) and object storage for uploaded resumes.

## 5) Quick local test before deploy

```bash
pip install -r requirements.txt
streamlit run app.py
```

If app runs locally and `GEMINI_API_KEY` is set, it should run online too.
