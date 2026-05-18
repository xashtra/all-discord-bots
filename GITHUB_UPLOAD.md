# 🚀 How to Upload Discord Counting Bot 2 to GitHub

This guide will show you exactly how to upload the **Discord Counting Bot 2** project to a GitHub repository, ensuring your configuration remains completely secure and deployable to Railway.

---

## 📂 1. Files & Folders to Upload

You should upload **all 9 files** currently located inside the `C:\coading\discord count bot 2` directory. There are no subdirectories that need to be committed.

Here is the checklist of files to upload and their purpose:

| File Name | Should Be Uploaded? | Purpose |
| :--- | :--- | :--- |
| `main.py` | **Yes** | The core Python source code of the bot. |
| `requirements.txt` | **Yes** | Tells GitHub & Railway what Python libraries (`discord.py-self`, `curl_cffi`) are needed. |
| `Procfile` | **Yes** | Tells cloud hosts how to run the bot. |
| `railway.json` | **Yes** | Specifies the Railway Nixpacks build instructions. |
| `runtime.txt` | **Yes** | Tells Railway which Python version to install. |
| `COMMANDS.md` | **Yes** | User documentation detailing all the commands. |
| `RAILWAY_SETUP.md` | **Yes** | Step-by-step guide for setting up Railway environment variables. |
| `PROJECT.md` | **Yes** | Standard project information and roadmap tracker. |
| `.gitignore` | **Yes** | **Crucial File!** Tells Git to completely ignore local environment files (like `.env`) and virtual environments. |

### ⚠️ IMPORTANT: Files/Folders NOT to Upload
Do **NOT** upload:
- `.env` file (if you have created one locally) — it contains your sensitive Discord account token.
- `.venv` or `venv` or `ENV` folders — these are massive local Python installation directories and should not be tracked.
- `__pycache__` folders — these are system-generated Python cache folders.

*Note: The included `.gitignore` will automatically prevent these sensitive files and large folders from being uploaded.*

---

## 🖥️ Method A: Upload Using Git (Command Line) — Recommended

If you have **Git** installed on your Windows machine, open your terminal (PowerShell or Git Bash) inside the directory `C:\coading\discord count bot 2` and run the following commands:

### Step 1: Initialize Git
```powershell
git init
```

### Step 2: Add Files
This staging command prepares all of your project files (while respecting the `.gitignore` rules):
```powershell
git add .
```

### Step 3: Create First Commit
```powershell
git commit -m "feat: implement dynamic prefix, VC binding, and custom control channel commands"
```

### Step 4: Rename default branch to `main`
```powershell
git branch -M main
```

### Step 5: Connect to GitHub
1. Go to your [GitHub Account](https://github.com/) and click **New Repository**.
2. Give it a name (e.g., `discord-count-bot-2`), choose **Private** (recommended for selfbots), and do **NOT** check "Add a README", "Add .gitignore", or "Choose a license" (since they are already in your project).
3. Click **Create repository**.
4. Copy the two lines under "...or push an existing repository from the command line". They will look like this:
```powershell
git remote add origin https://github.com/YOUR_USERNAME/discord-count-bot-2.git
git push -u origin main
```

---

## 🌐 Method B: Upload via GitHub Website (No CLI)

If you don't have Git installed on your computer, you can upload your files directly through your web browser:

1. Go to [GitHub](https://github.com/) and create a new **Private** repository named `discord-count-bot-2`. Do **NOT** add a README, `.gitignore`, or license.
2. Once the repository is created, click the link that says **"uploading an existing file"** in the introduction setup box.
3. Open your Windows File Explorer, navigate to `C:\coading\discord count bot 2`.
4. Select all 9 files listed in Section 1 and **drag and drop** them into the browser upload box on GitHub.
5. Wait for all files to load.
6. Scroll down, write a commit message (e.g. `Initial commit of customized bot`), and click **Commit changes**.

---

## 🚀 Connecting to Railway

Once your files are on GitHub:
1. Log in to [Railway](https://railway.app/).
2. Click **+ New Project** -> **Deploy from GitHub repo**.
3. Select your `discord-count-bot-2` repository.
4. Add your **Variables** (`TOKEN`, `OWNER_ID`, `PREFIX`, `VOICE_CHANNEL_ID`) in Railway's Service panel, and Railway will instantly deploy the bot!
