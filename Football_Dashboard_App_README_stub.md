# Football Dashboard App

This repository contains a Streamlit dashboard for exploring the 2021-2022 football player statistics dataset.

Contents:
- `Football_Statics_App.py` — Streamlit app (already present in workspace).
- `2021_2022_Football_Player_Stats.csv` — dataset (already present).

Quick start

1. Create and activate your virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
Set-Location -LiteralPath 'C:\Users\efast\Football_Statics_App'
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the app:

```powershell
& '.\Football_Statics_App\Scripts\python.exe' -m streamlit run .\Football_Statics_App\Football_Statics_App.py --server.port 8501
```

Pushing to GitHub

- Using the GitHub CLI (recommended when authenticated):

```powershell
cd C:\Users\efast\Football_Statics_App
gh repo create YOUR_GITHUB_USERNAME/Football_Dashboard_App --public --source=. --remote=origin --push
```

- Or create a repo on github.com and then:

```powershell
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/Football_Dashboard_App.git
git branch -M main
git push -u origin main
```

Notes

- If you want me to create the GitHub repository for you and push the code, either authenticate the environment with `gh auth login` or provide a GitHub personal access token and I can use it (you can paste a token here or instruct me how you'd like to proceed).