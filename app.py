import pandas as pd
import streamlit as st

from model import COMPANY, EDUCATION, LOCATION, ROLES, load_model, predict_salary

st.set_page_config(page_title="Employee Salary Estimator", page_icon="💼", layout="wide")


@st.cache_resource(show_spinner="Loading model...")
def get_model():
    return load_model()


bundle = get_model()
pipe = bundle["pipeline"]

st.title("💼 Employee Salary Estimator")
st.caption("Estimate annual salary (LPA = lakhs per annum) from experience, education and job features.")

# ---------------- Sidebar inputs ----------------
with st.sidebar:
    st.header("Employee profile")
    job_role = st.selectbox("Job role", list(ROLES))
    education = st.selectbox("Education", list(EDUCATION), index=2)
    location_tier = st.selectbox("City tier", list(LOCATION))
    company_size = st.selectbox("Company size", list(COMPANY), index=1)
    skills_count = st.slider("Relevant skills", 0, 10, 5)
    certifications = st.slider("Certifications", 0, 5, 1)

    st.header("Experience comparison")
    years_a = st.slider("Scenario A: years of experience", 0.0, 30.0, 2.0, 0.5)
    years_b = st.slider("Scenario B: years of experience", 0.0, 30.0, 7.0, 0.5)

profile = dict(
    job_role=job_role,
    education=education,
    location_tier=location_tier,
    company_size=company_size,
    skills_count=skills_count,
    certifications=certifications,
)

salary_a = predict_salary(pipe, years_experience=years_a, **profile)
salary_b = predict_salary(pipe, years_experience=years_b, **profile)
diff = salary_b - salary_a
pct = (diff / salary_a * 100) if salary_a else 0.0

# ---------------- Results ----------------
c1, c2, c3 = st.columns(3)
c1.metric(f"Scenario A ({years_a:g} yrs)", f"₹ {salary_a:.2f} LPA", f"≈ ₹ {salary_a * 100000 / 12:,.0f} / month", delta_color="off")
c2.metric(f"Scenario B ({years_b:g} yrs)", f"₹ {salary_b:.2f} LPA", f"≈ ₹ {salary_b * 100000 / 12:,.0f} / month", delta_color="off")
c3.metric("Difference (B − A)", f"₹ {diff:+.2f} LPA", f"{pct:+.1f}%")

st.subheader("Salary vs. years of experience")
years_grid = [x / 2 for x in range(0, 61)]  # 0 to 30 in 0.5 steps
curve = pd.DataFrame(
    {
        "Years of experience": years_grid,
        "Predicted salary (LPA)": [predict_salary(pipe, years_experience=y, **profile) for y in years_grid],
    }
).set_index("Years of experience")
st.line_chart(curve)

# ---------------- Comparison log (for the examiner) ----------------
st.subheader("Comparison log")
st.write("Change the experience sliders, press the button, and compare the saved runs below.")

if "log" not in st.session_state:
    st.session_state.log = []

b1, b2 = st.columns([1, 1])
if b1.button("➕ Add Scenario A and B to log"):
    for label, yrs, sal in (("A", years_a, salary_a), ("B", years_b, salary_b)):
        st.session_state.log.append(
            {"Scenario": label, "Experience (yrs)": yrs, **{k.replace("_", " ").title(): v for k, v in profile.items()},
             "Predicted salary (LPA)": round(sal, 2)}
        )
if b2.button("🗑️ Clear log"):
    st.session_state.log = []

if st.session_state.log:
    st.dataframe(pd.DataFrame(st.session_state.log), use_container_width=True)

with st.expander("About the model"):
    m = bundle["metrics"]
    st.write(
        f"Gradient boosting regressor trained on {m['rows']:,} rows ({m['source']}). "
        f"Hold-out R² = {m['r2']:.3f}, mean absolute error = {m['mae_lpa']:.2f} LPA. "
        "Experience, skills and certifications are constrained so predictions never decrease as they increase. "
        "Place a real dataset at `data/salary_data.csv` (columns: job_role, education, location_tier, "
        "company_size, years_experience, skills_count, certifications, salary_lpa) to train on real data."
    )
