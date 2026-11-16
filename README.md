# Employee Salary Estimator

Streamlit app that estimates employee salary (in LPA) from job role, education,
years of experience, city tier, company size, skills and certifications.
Change the years of experience (Scenario A vs B) and compare the predicted salary.

## Files
| File | Purpose |
|---|---|
| `app.py` | Streamlit UI |
| `model.py` | Data generation, training, loading, prediction |
| `requirements.txt` | Python dependencies |
| `.streamlit/config.toml` | Theme / server settings |
| `data/salary_data.csv` | Optional real dataset (not included) |

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python model.py                  # optional: pre-train and save the model
streamlit run app.py
```

## Push to GitHub
```bash
git init
git add .
git commit -m "Employee salary estimator"
git branch -M main
git remote add origin https://github.com/<your-username>/salary-predictor.git
git push -u origin main
```
Create the empty repo `salary-predictor` on github.com first (no README).

## Deploy on Streamlit Community Cloud
1. Go to https://share.streamlit.io and sign in with GitHub.
2. Click **Create app** -> **Deploy a public app from GitHub**.
3. Repository: `<your-username>/salary-predictor`, Branch: `main`, Main file path: `app.py`.
4. Click **Deploy**. Every `git push` to `main` redeploys automatically.

## Using real data
Add `data/salary_data.csv` with columns
`job_role, education, location_tier, company_size, years_experience, skills_count, certifications, salary_lpa`,
commit and push. The app retrains on it at startup.
