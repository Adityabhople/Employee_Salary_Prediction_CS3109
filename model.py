"""Salary model: data generation, training, loading and prediction.

Run `python model.py` to (re)train and save the model locally.
If data/salary_data.csv exists it is used for training, otherwise a synthetic
dataset is generated from the rules below.
"""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR / "salary_model.joblib"
DATA_PATH = BASE_DIR / "data" / "salary_data.csv"

# Base salary (LPA) for a fresher: bachelor's degree, tier-2 city, mid-size company
ROLES = {
    "Software Engineer": 5.0,
    "Data Scientist": 7.0,
    "Data Analyst": 4.5,
    "Product Manager": 9.0,
    "Marketing Manager": 5.0,
    "HR Executive": 3.5,
    "Sales Executive": 3.5,
    "Accountant": 3.5,
}
EDUCATION = {
    "High School": 0.75,
    "Diploma": 0.85,
    "Bachelor Degree": 1.0,
    "Master Degree": 1.18,
    "PhD": 1.4,
}
LOCATION = {"Tier 1 (Metro)": 1.15, "Tier 2": 1.0, "Tier 3": 0.85}
COMPANY = {"Startup": 0.95, "Mid-size": 1.0, "Large / MNC": 1.2}

CATEGORICAL = ["job_role", "education", "location_tier", "company_size"]
NUMERIC = ["years_experience", "skills_count", "certifications"]
TARGET = "salary_lpa"


def _rule_salary(row):
    exp_mult = 1 + 1.4 * (1 - np.exp(-row["years_experience"] / 8))
    return (
        ROLES[row["job_role"]]
        * EDUCATION[row["education"]]
        * LOCATION[row["location_tier"]]
        * COMPANY[row["company_size"]]
        * exp_mult
        * (1 + 0.025 * row["skills_count"])
        * (1 + 0.03 * row["certifications"])
    )


def generate_synthetic_data(n=6000, seed=42):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame(
        {
            "job_role": rng.choice(list(ROLES), n),
            "education": rng.choice(list(EDUCATION), n, p=[0.05, 0.1, 0.45, 0.32, 0.08]),
            "location_tier": rng.choice(list(LOCATION), n, p=[0.45, 0.35, 0.2]),
            "company_size": rng.choice(list(COMPANY), n, p=[0.3, 0.35, 0.35]),
            "years_experience": rng.uniform(0, 25, n).round(1),
            "skills_count": rng.integers(0, 11, n),
            "certifications": rng.integers(0, 6, n),
        }
    )
    base = df.apply(_rule_salary, axis=1)
    df[TARGET] = (base * rng.lognormal(0, 0.06, n)).round(2)
    return df


def load_training_data():
    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH)
    return generate_synthetic_data()


def build_pipeline():
    categories = [list(ROLES), list(EDUCATION), list(LOCATION), list(COMPANY)]
    pre = ColumnTransformer(
        [
            ("num", "passthrough", NUMERIC),
            (
                "cat",
                OneHotEncoder(categories=categories, sparse_output=False, handle_unknown="ignore"),
                CATEGORICAL,
            ),
        ]
    )
    n_onehot = sum(len(c) for c in categories)
    # more experience / skills / certifications should never lower the prediction
    monotonic = [1, 1, 1] + [0] * n_onehot
    model = HistGradientBoostingRegressor(
        monotonic_cst=monotonic, max_iter=300, learning_rate=0.08, random_state=42
    )
    return Pipeline([("pre", pre), ("model", model)])


def train_model(save=True):
    df = load_training_data()
    X, y = df[CATEGORICAL + NUMERIC], df[TARGET]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
    pipe = build_pipeline()
    pipe.fit(X_tr, y_tr)
    pred = pipe.predict(X_te)
    metrics = {
        "r2": float(r2_score(y_te, pred)),
        "mae_lpa": float(mean_absolute_error(y_te, pred)),
        "rows": int(len(df)),
        "source": "data/salary_data.csv" if DATA_PATH.exists() else "synthetic data",
    }
    bundle = {"pipeline": pipe, "metrics": metrics}
    if save:
        joblib.dump(bundle, MODEL_PATH)
    return bundle


def load_model():
    if MODEL_PATH.exists():
        try:
            return joblib.load(MODEL_PATH)
        except Exception:
            pass  # saved with a different library version: retrain
    return train_model(save=False)


def predict_salary(pipe, job_role, education, location_tier, company_size,
                   years_experience, skills_count, certifications):
    row = pd.DataFrame(
        [
            {
                "job_role": job_role,
                "education": education,
                "location_tier": location_tier,
                "company_size": company_size,
                "years_experience": years_experience,
                "skills_count": skills_count,
                "certifications": certifications,
            }
        ]
    )
    return float(pipe.predict(row)[0])


if __name__ == "__main__":
    result = train_model(save=True)
    print("Model saved to", MODEL_PATH)
    print(result["metrics"])
