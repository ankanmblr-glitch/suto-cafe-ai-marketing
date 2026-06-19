# Deploy Suto Café PoC to GitHub + Streamlit Community Cloud

> **GitHub Pages cannot run Python apps** — it only serves static HTML.
> The free alternative that works identically is **Streamlit Community Cloud**
> (`share.streamlit.io`): it connects to your GitHub repo, runs the Python app,
> and gives you a public URL — all for free.

---

## Step 1 — Create a GitHub Repository

1. Go to [github.com](https://github.com) → **New repository**
2. Name it `suto-cafe-ai-marketing` (or any name you like)
3. Set to **Public** (required for free Streamlit Cloud hosting)
4. Do NOT initialise with README (we have our own files)
5. Click **Create repository**

---

## Step 2 — Push This Folder to GitHub

Open Command Prompt in `C:\personal\cafe\C_all_files\poc` and run:

```bat
git init
git add .
git commit -m "Initial Suto Café PoC"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/suto-cafe-ai-marketing.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

> ✅ The `.gitignore` already excludes `.env` (your real API keys) and `venv/`,
> so only source code gets pushed — secrets stay on your machine.

---

## Step 3 — Deploy on Streamlit Community Cloud (Free)

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Fill in:
   - **Repository:** `YOUR_USERNAME/suto-cafe-ai-marketing`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Click **Advanced settings** → **Secrets** → paste:

```toml
GROQ_API_KEY = "your_groq_key_here"
OPENWEATHER_API_KEY = "your_openweather_key_here"
DEMO_MODE = "false"
GROQ_MODEL = "llama-3.1-8b-instant"
CAFE_NAME = "Suto Café"
CAFE_LOCATION = "Siliguri, West Bengal"
```

6. Click **Deploy!**

The app will be live at:
`https://YOUR_USERNAME-suto-cafe-ai-marketing-app-XXXX.streamlit.app`

You can share this URL directly with the café owner for the PoC demo.

---

## Step 4 — Auto-Updates (Optional)

Every time you push new code to GitHub, Streamlit Cloud redeploys automatically.
No manual steps needed.

```bat
git add .
git commit -m "Update: fixed banner layout"
git push
```

→ App updates in ~60 seconds on the public URL.

---

## DEMO_MODE = "true" (Zero API Keys)

If you don't want to add real API keys to the cloud secrets, set:

```toml
DEMO_MODE = "true"
```

The app will run entirely on realistic mock data — perfect for a PoC demo
where you just want to show the client how everything looks and works.

---

## Summary: Why Not GitHub Pages?

| | GitHub Pages | Streamlit Community Cloud |
|---|---|---|
| Runs Python | ❌ No | ✅ Yes |
| Free | ✅ Yes | ✅ Yes |
| Public URL | ✅ Yes | ✅ Yes |
| Connected to GitHub | ✅ Yes | ✅ Yes |
| Auto-deploy on push | ✅ Yes | ✅ Yes |
| Runs Streamlit | ❌ Not possible | ✅ Native support |

GitHub Pages is HTML-only. Streamlit Community Cloud is the right tool here.
