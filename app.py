import altair as alt
import pandas as pd
import streamlit as st

from model import COMPANY, EDUCATION, LOCATION, ROLES, load_model, predict_salary

st.set_page_config(page_title="Employee Salary Estimator", page_icon="💼", layout="wide")

# ---------------------------------------------------------------- styling
st.markdown(
    """
<style>
.block-container {padding-top: 1.6rem; max-width: 1200px;}
footer {visibility: hidden;}
.hero {background: linear-gradient(135deg,#4f46e5 0%,#7c3aed 50%,#db2777 100%);
       padding: 28px 34px; border-radius: 22px; color: #fff; margin-bottom: 18px;
       box-shadow: 0 12px 32px rgba(79,70,229,.35);}
.hero .title {font-size: 2.3rem; font-weight: 800; line-height: 1.15; color:#fff;}
.hero .subtitle {margin-top: 8px; font-size: 1.05rem; opacity: .92; color:#fff;}
.chip {display:inline-block; padding:5px 14px; border-radius:999px; margin:2px 6px 2px 0;
       background: rgba(99,102,241,.16); border:1px solid rgba(99,102,241,.35); font-size:.85rem;}
.kpi {border-radius:18px; padding:20px 24px; border:1px solid rgba(128,128,160,.28);
      background: rgba(128,128,160,.10); height: 100%;}
.kpi .label {font-size:.8rem; opacity:.75; text-transform:uppercase; letter-spacing:.08em; font-weight:600;}
.kpi .value {font-size:2.2rem; font-weight:800; margin:6px 0 2px 0; line-height:1.1;}
.kpi .sub {font-size:.92rem; opacity:.75; margin-bottom:8px;}
.kpi.a {border-top:5px solid #6366f1;}
.kpi.b {border-top:5px solid #ec4899;}
.kpi.d {border-top:5px solid #10b981;}
.badge {display:inline-block; padding:3px 12px; border-radius:999px; font-weight:700; font-size:.85rem;}
.badge.up {background:rgba(16,185,129,.18); color:#10b981;}
.badge.down {background:rgba(239,68,68,.18); color:#ef4444;}
.badge.flat {background:rgba(148,163,184,.22); color:#94a3b8;}
.footer-note {text-align:center; opacity:.55; font-size:.85rem; margin-top:34px;}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="Loading model...")
def get_model():
    return load_model()


bundle = get_model()
pipe = bundle["pipeline"]

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("## 🧑‍💼 Employee profile")
    job_role = st.selectbox("💼 Job role", list(ROLES))
    education = st.selectbox("🎓 Education", list(EDUCATION), index=2)
    location_tier = st.selectbox("📍 City tier", list(LOCATION))
    company_size = st.selectbox("🏢 Company size", list(COMPANY), index=1)
    skills_count = st.slider("🛠️ Relevant skills", 0, 10, 5)
    certifications = st.slider("📜 Certifications", 0, 5, 1)

    st.markdown("## ⏱️ Experience comparison")
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

# ---------------------------------------------------------------- predictions
salary_a = predict_salary(pipe, years_experience=years_a, **profile)
salary_b = predict_salary(pipe, years_experience=years_b, **profile)
diff = salary_b - salary_a
pct = (diff / salary_a * 100) if salary_a else 0.0

# ---------------------------------------------------------------- hero
st.markdown(
    """
<div class="hero">
  <div class="title">💼 Employee Salary Estimator</div>
  <div class="subtitle">Predict annual salary (LPA = lakhs per annum) from experience, education and job
  features, then change the years of experience to compare scenarios.</div>
</div>
""",
    unsafe_allow_html=True,
)

chips = [job_role, education, location_tier, company_size, f"{skills_count} skills", f"{certifications} certifications"]
st.markdown("".join(f'<span class="chip">{c}</span>' for c in chips), unsafe_allow_html=True)
st.write("")


def kpi(cls, label, value, sub, badge=""):
    return (
        f'<div class="kpi {cls}"><div class="label">{label}</div>'
        f'<div class="value">{value}</div><div class="sub">{sub}</div>{badge}</div>'
    )


if diff > 0.005:
    badge_cls, arrow = "up", "▲"
elif diff < -0.005:
    badge_cls, arrow = "down", "▼"
else:
    badge_cls, arrow = "flat", "■"

c1, c2, c3 = st.columns(3)
c1.markdown(
    kpi("a", f"Scenario A · {years_a:g} yrs", f"₹ {salary_a:.2f} LPA", f"≈ ₹ {salary_a * 100000 / 12:,.0f} / month"),
    unsafe_allow_html=True,
)
c2.markdown(
    kpi("b", f"Scenario B · {years_b:g} yrs", f"₹ {salary_b:.2f} LPA", f"≈ ₹ {salary_b * 100000 / 12:,.0f} / month"),
    unsafe_allow_html=True,
)
c3.markdown(
    kpi(
        "d",
        "Difference (B − A)",
        f"₹ {diff:+.2f} LPA",
        f"≈ ₹ {diff * 100000 / 12:+,.0f} / month",
        f'<span class="badge {badge_cls}">{arrow} {pct:+.1f}%</span>',
    ),
    unsafe_allow_html=True,
)
st.write("")

if abs(years_b - years_a) < 1e-9:
    st.info("Scenario A and B use the same experience. Move the Scenario B slider to see how salary changes.")
else:
    direction = "increases" if diff >= 0 else "decreases"
    st.success(
        f"Going from **{years_a:g}** to **{years_b:g}** years of experience, the predicted salary "
        f"{direction} by **₹ {abs(diff):.2f} LPA ({abs(pct):.1f}%)** for this profile."
    )

# ---------------------------------------------------------------- tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Experience curve", "🔍 Role & education", "📋 Comparison log", "ℹ️ About model"])

SCEN_COLORS = alt.Scale(domain=["A", "B"], range=["#6366f1", "#ec4899"])

# ---- Tab 1: experience curve
with tab1:
    years_grid = [x / 2 for x in range(0, 61)]
    curve = pd.DataFrame(
        {
            "Years": years_grid,
            "Salary": [predict_salary(pipe, years_experience=y, **profile) for y in years_grid],
        }
    )
    base = alt.Chart(curve).encode(
        x=alt.X("Years:Q", title="Years of experience"),
        y=alt.Y("Salary:Q", title="Predicted salary (LPA)"),
    )
    area = base.mark_area(interpolate="monotone", opacity=0.22, color="#6366f1")
    line = base.mark_line(interpolate="monotone", strokeWidth=3, color="#6366f1")

    pts = pd.DataFrame(
        {
            "Scenario": ["A", "B"],
            "Years": [years_a, years_b],
            "Salary": [salary_a, salary_b],
            "Label": [f"A: {salary_a:.1f}", f"B: {salary_b:.1f}"],
        }
    )
    marks = alt.Chart(pts).encode(
        x="Years:Q",
        y="Salary:Q",
        color=alt.Color("Scenario:N", scale=SCEN_COLORS, legend=alt.Legend(title=None, orient="top")),
        tooltip=["Scenario", "Years", alt.Tooltip("Salary:Q", format=".2f")],
    )
    rules = marks.mark_rule(strokeDash=[5, 5], opacity=0.6)
    dots = marks.mark_point(size=260, filled=True, opacity=1)
    labels = marks.encode(text="Label:N").mark_text(dy=-20, fontWeight="bold", fontSize=13)

    st.altair_chart((area + line + rules + dots + labels).properties(height=400))

    st.markdown("##### Salary milestones for this profile")
    milestones = [0, 1, 2, 3, 5, 8, 10, 15, 20, 25, 30]
    sal0 = predict_salary(pipe, years_experience=0, **profile)
    rows = []
    for y in milestones:
        s = predict_salary(pipe, years_experience=y, **profile)
        rows.append(
            {
                "Experience (yrs)": y,
                "Salary (LPA)": round(s, 2),
                "Monthly (₹)": f"{s * 100000 / 12:,.0f}",
                "Growth vs fresher": f"{(s / sal0 - 1) * 100:+.0f}%" if sal0 else "-",
            }
        )
    st.dataframe(pd.DataFrame(rows), hide_index=True)

# ---- Tab 2: role and education comparison
with tab2:
    left, right = st.columns(2)

    def compare_df(options, field):
        recs = []
        for opt in options:
            p = dict(profile)
            p[field] = opt
            recs.append({"Option": opt, "Scenario": "A", "Salary": predict_salary(pipe, years_experience=years_a, **p)})
            recs.append({"Option": opt, "Scenario": "B", "Salary": predict_salary(pipe, years_experience=years_b, **p)})
        return pd.DataFrame(recs)

    def grouped_bar(df, title):
        order = list(df[df["Scenario"] == "B"].sort_values("Salary", ascending=False)["Option"])
        return (
            alt.Chart(df)
            .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
            .encode(
                x=alt.X("Option:N", sort=order, title=None, axis=alt.Axis(labelAngle=-35)),
                xOffset="Scenario:N",
                y=alt.Y("Salary:Q", title="Salary (LPA)"),
                color=alt.Color("Scenario:N", scale=SCEN_COLORS, legend=alt.Legend(title=None, orient="top")),
                tooltip=["Option", "Scenario", alt.Tooltip("Salary:Q", format=".2f")],
            )
            .properties(height=360, title=title)
        )

    with left:
        st.altair_chart(grouped_bar(compare_df(list(ROLES), "job_role"), "Same profile, different job role"))
    with right:
        st.altair_chart(grouped_bar(compare_df(list(EDUCATION), "education"), "Same profile, different education"))

# ---- Tab 3: comparison log
with tab3:
    st.write("Change the sliders, add the runs to the log, and compare them side by side.")
    if "log" not in st.session_state:
        st.session_state.log = []

    b1, b2, _ = st.columns([1.2, 1, 3])
    if b1.button("➕ Add Scenario A and B"):
        for label, yrs, sal in (("A", years_a, salary_a), ("B", years_b, salary_b)):
            st.session_state.log.append(
                {
                    "Scenario": label,
                    "Experience (yrs)": yrs,
                    **{k.replace("_", " ").title(): v for k, v in profile.items()},
                    "Predicted salary (LPA)": round(sal, 2),
                }
            )
    if b2.button("🗑️ Clear log"):
        st.session_state.log = []

    if st.session_state.log:
        log_df = pd.DataFrame(st.session_state.log)
        st.dataframe(log_df, hide_index=True)
        st.download_button("⬇️ Download log as CSV", log_df.to_csv(index=False), "salary_comparison_log.csv", "text/csv")
    else:
        st.caption("No runs saved yet.")

# ---- Tab 4: about
with tab4:
    m = bundle["metrics"]
    k1, k2, k3 = st.columns(3)
    k1.metric("R² (hold-out)", f"{m['r2']:.3f}")
    k2.metric("Mean absolute error", f"{m['mae_lpa']:.2f} LPA")
    k3.metric("Training rows", f"{m['rows']:,}")
    st.write(
        f"Gradient boosting regressor trained on **{m['source']}**. Experience, skills and certifications are "
        "constrained so predictions never decrease as they increase. To use real data, add "
        "`data/salary_data.csv` with columns `job_role, education, location_tier, company_size, "
        "years_experience, skills_count, certifications, salary_lpa`."
    )

st.markdown('<div class="footer-note">Employee Salary Estimator · built with Streamlit</div>', unsafe_allow_html=True)
