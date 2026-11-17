import altair as alt
import pandas as pd
import streamlit as st

from model import COMPANY, EDUCATION, LOCATION, ROLES, load_model, predict_salary

st.set_page_config(page_title="Employee Salary Estimator", page_icon="🌸", layout="wide")

# ---------------------------------------------------------------- styling
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Poppins:wght@400;500;600&display=swap');

/* ===== Page background: soft cream with pastel glows and a dotted texture ===== */
.stApp {
  font-family: 'Poppins', sans-serif;
  background:
    radial-gradient(rgba(155,126,222,.16) 1.2px, transparent 1.2px),
    radial-gradient(700px 480px at 6% -5%, rgba(205,180,246,.55), transparent 62%),
    radial-gradient(800px 520px at 100% 2%, rgba(255,200,221,.55), transparent 60%),
    radial-gradient(900px 560px at 60% 112%, rgba(186,236,214,.50), transparent 60%),
    #fbf7ff;
  background-size: 26px 26px, auto, auto, auto, auto;
  background-attachment: fixed;
}
header[data-testid="stHeader"] {background: transparent;}
footer {visibility: hidden;}
.block-container {padding-top: 3.2rem; max-width: 1200px;}

/* ===== Sidebar ===== */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #efe6fb 0%, #fde7ef 60%, #fff1e6 100%);
  border-right: 1px solid rgba(155,126,222,.28);
  box-shadow: 6px 0 28px rgba(155,126,222,.14);
}
[data-testid="stSidebar"] > div:first-child {background: transparent;}
[data-testid="stSidebar"] .block-container {padding-top: 1rem;}
[data-testid="stSidebar"] label p {font-size: .86rem; font-weight: 500;}
[data-testid="stSidebar"] div[data-baseweb="select"] > div {
  background: rgba(255,255,255,.80); border: 1px solid rgba(155,126,222,.32); border-radius: 12px;
}
[data-testid="stSidebar"] div[data-baseweb="select"] > div:hover {border-color: #9b7ede;}
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
  background: rgba(255,255,255,.55); border: 1px solid rgba(155,126,222,.22);
  border-radius: 18px; padding: 4px 6px; box-shadow: 0 6px 18px rgba(155,126,222,.10);
}
.side-brand {display:flex; align-items:center; gap:14px; padding:16px 16px; margin-bottom:14px;
  border-radius:20px; background: linear-gradient(135deg, #cdb4f6, #f7b6d2);
  border: 1px solid rgba(255,255,255,.75); box-shadow: 0 8px 22px rgba(155,126,222,.30);}
.side-brand .avatar {width:46px; height:46px; border-radius:15px; display:flex; align-items:center;
  justify-content:center; font-size:1.5rem; background: rgba(255,255,255,.60);}
.side-brand .side-title {font-family:'Playfair Display', serif; font-weight:700; font-size:1.2rem;
  color:#3b2f4a; line-height:1.2;}
.side-brand .side-sub {font-size:.78rem; color:#5b4a78;}
.side-section {display:flex; align-items:center; gap:8px; font-size:.7rem; font-weight:600;
  letter-spacing:.14em; text-transform:uppercase; color:#7c5cc4; margin: 4px 0 6px 2px;}
.side-section .dot {width:8px; height:8px; border-radius:50%; background: linear-gradient(135deg,#9b7ede,#f4a6c0);}
.side-summary {margin-top:14px; padding:16px; border-radius:20px;
  background: linear-gradient(160deg, rgba(168,230,207,.55), rgba(205,180,246,.40));
  border: 1px solid rgba(94,196,160,.45); color:#3b2f4a;}
.side-summary .lbl {font-size:.7rem; text-transform:uppercase; letter-spacing:.14em; color:#2f9e7a; font-weight:600;}
.side-summary .row {display:flex; justify-content:space-between; align-items:center; padding:7px 0;
  border-bottom:1px dashed rgba(124,92,196,.30); font-size:.88rem;}
.side-summary .row:last-child {border-bottom:none;}
.side-summary .row b {font-size:1rem;}

/* ===== Hero ===== */
.hero {background: linear-gradient(135deg,#cdb4f6 0%,#f7b6d2 55%,#ffd8b5 100%);
       padding: 30px 36px; border-radius: 26px; color: #3b2f4a; margin-bottom: 18px;
       box-shadow: 0 14px 34px rgba(155,126,222,.30); border: 1px solid rgba(255,255,255,.80);}
.hero .title {font-family:'Playfair Display', serif; font-size: 2.4rem; font-weight: 700;
       line-height: 1.15; color:#3b2f4a;}
.hero .subtitle {margin-top: 8px; font-size: 1rem; color:#4b3b63;}
.chip {display:inline-block; padding:5px 14px; border-radius:999px; margin:2px 6px 2px 0;
       background: rgba(255,255,255,.75); border:1px solid rgba(155,126,222,.35);
       font-size:.83rem; color:#5b4a78;}

/* ===== KPI cards ===== */
.kpi {border-radius:22px; padding:20px 24px; border:1px solid rgba(155,126,222,.20);
      background: rgba(255,255,255,.78); height: 100%;
      box-shadow: 0 10px 26px rgba(155,126,222,.16);}
.kpi .label {font-size:.76rem; opacity:.75; text-transform:uppercase; letter-spacing:.09em; font-weight:600;}
.kpi .value {font-family:'Playfair Display', serif; font-size:2.25rem; font-weight:700;
      margin:6px 0 2px 0; line-height:1.1;}
.kpi .sub {font-size:.9rem; opacity:.75; margin-bottom:8px;}
.kpi.a {border-top:5px solid #9b7ede;}
.kpi.b {border-top:5px solid #f4a09a;}
.kpi.d {border-top:5px solid #5ec4a0;}
.badge {display:inline-block; padding:3px 12px; border-radius:999px; font-weight:600; font-size:.84rem;}
.badge.up {background:rgba(94,196,160,.22); color:#1f8a66;}
.badge.down {background:rgba(240,120,120,.22); color:#c0392b;}
.badge.flat {background:rgba(150,140,170,.22); color:#6b5f80;}

/* ===== Tabs ===== */
button[data-baseweb="tab"] {font-weight:500;}
.footer-note {text-align:center; opacity:.6; font-size:.85rem; margin-top:34px;}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="Loading model...")
def get_model():
    return load_model()


bundle = get_model()
pipe = bundle["pipeline"]


def section(title):
    st.markdown(f'<div class="side-section"><span class="dot"></span>{title}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown(
        """
<div class="side-brand">
  <div class="avatar">🌸</div>
  <div><div class="side-title">Employee Profile</div>
  <div class="side-sub">Configure the candidate details</div></div>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        section("Job details")
        job_role = st.selectbox("💼 Job role", list(ROLES))
        company_size = st.selectbox("🏢 Company size", list(COMPANY), index=1)
        location_tier = st.selectbox("📍 City tier", list(LOCATION))

    with st.container(border=True):
        section("Qualifications")
        education = st.selectbox("🎓 Education", list(EDUCATION), index=2)
        skills_count = st.slider("🛠️ Relevant skills", 0, 10, 5)
        certifications = st.slider("📜 Certifications", 0, 5, 1)

    with st.container(border=True):
        section("Experience comparison")
        years_a = st.slider("Scenario A · years of experience", 0.0, 30.0, 2.0, 0.5)
        years_b = st.slider("Scenario B · years of experience", 0.0, 30.0, 7.0, 0.5)

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

with st.sidebar:
    st.markdown(
        f"""
<div class="side-summary">
  <div class="lbl">Live prediction</div>
  <div class="row"><span>Scenario A · {years_a:g} yrs</span><b>₹ {salary_a:.2f} LPA</b></div>
  <div class="row"><span>Scenario B · {years_b:g} yrs</span><b>₹ {salary_b:.2f} LPA</b></div>
  <div class="row"><span>Difference</span><b>{diff:+.2f} LPA</b></div>
</div>
""",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------- hero
st.markdown(
    """
<div class="hero">
  <div class="title">🌸 Employee Salary Estimator</div>
  <div class="subtitle">Predict annual salary (LPA = lakhs per annum) from experience, education and job
  features, then change the years of experience to compare scenarios.</div>
</div>
""",
    unsafe_allow_html=True,
)

chips = [
    job_role,
    education,
    location_tier,
    company_size,
    f"{skills_count} skill{'s' if skills_count != 1 else ''}",
    f"{certifications} certification{'s' if certifications != 1 else ''}",
]
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

SCEN_COLORS = alt.Scale(domain=["A", "B"], range=["#8b6fd6", "#f08a7e"])

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
    area = base.mark_area(interpolate="monotone", opacity=0.28, color="#b8a2ea")
    line = base.mark_line(interpolate="monotone", strokeWidth=3, color="#8b6fd6")

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
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
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
