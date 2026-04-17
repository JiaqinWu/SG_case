
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path
from millify import millify # shortens values (10_000 ---> 10k)

# Visual constants
PALETTE = ["#0d5c63", "#44a1a0", "#ee6c4d", "#f4a261", "#2a6f97", "#6b4e71"]
# One stable color per hub for maps / legends (5 hubs).
HUB_COLOR_ACCENT = ["#0d5c63", "#c45c3e", "#287a8c", "#6b4e71", "#d4a03a"]

SECTOR_ORDER = ["North", "East", "South"]
SECTOR_COLOR_MAP = {"North": "#0d5c63", "East": "#ee6c4d", "South": "#1e6fa8"}
SECTOR_SYMBOL_MAP = {"North": "circle", "East": "square", "South": "diamond"}
PAGE_STYLE = """
<style>
    .block-container { padding-top: 0.75rem; max-width: 1400px; }
    div[data-testid="stVerticalBlockBorderWrapper"] { border-color: rgba(13, 92, 99, 0.16) !important; box-shadow: 0 2px 14px rgba(13, 92, 99, 0.05); }
    h1 { letter-spacing: -0.03em; color: #0d5c63 !important; }
    h2, h3 { color: #0a3d42 !important; letter-spacing: -0.02em; }
    .pres-hero {
        border-left: 5px solid #0d5c63;
        background: linear-gradient(135deg, #f6fbfc 0%, #ffffff 55%, #faf8f5 100%);
        padding: 1.1rem 1.35rem 1.15rem 1.35rem;
        border-radius: 0 12px 12px 0;
        margin-bottom: 0.5rem;
        box-shadow: 0 2px 16px rgba(13, 92, 99, 0.07);
        border: 1px solid rgba(13, 92, 99, 0.1);
        border-left-width: 5px;
    }
    .pres-hero .pres-title { font-size: 1.85rem; font-weight: 700; color: #063a40; letter-spacing: -0.035em; line-height: 1.2; margin: 0 0 0.35rem 0; }
    .pres-hero .pres-sub { font-size: 1.05rem; color: #3d5659; line-height: 1.45; margin: 0; max-width: 52rem; }
    .pres-filter-hint { font-size: 0.88rem; color: #5a6e72; margin-top: 0.35rem; }
    .how-read { font-size: 0.92rem; color: #3d534f; background: #f0f8f9; border-radius: 10px; padding: 0.75rem 1rem; border: 1px solid rgba(13,92,99,0.12); margin: 0.5rem 0 1rem 0; line-height: 1.5; }
    [data-testid="stMetric"] {
        background: linear-gradient(180deg, #ffffff 0%, #f4fafb 100%);
        border: 1px solid rgba(13, 92, 99, 0.14);
        border-radius: 12px;
        padding: 0.85rem 1rem 0.95rem 1rem !important;
        box-shadow: 0 2px 10px rgba(13, 92, 99, 0.06);
    }
    [data-testid="stMetricValue"] {
        font-weight: 700;
        font-size: 1.35rem !important;
        letter-spacing: -0.03em;
        color: #062d32 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.78rem !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #3d6a70 !important;
    }
    [data-testid="stMetricDelta"] { font-weight: 600; }

    /* Tab bar — pill strip, calmer than default Streamlit chrome */
    div[data-testid="stTabs"] { margin-top: 0.75rem; }
    div[data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 6px !important;
        background: linear-gradient(180deg, #eef7f8 0%, #e4f0f2 100%) !important;
        border: 1px solid rgba(13, 92, 99, 0.16) !important;
        border-radius: 14px !important;
        padding: 8px 10px !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.7);
    }
    div[data-testid="stTabs"] [data-baseweb="tab"] {
        border-radius: 10px !important;
        border: none !important;
        padding: 10px 18px !important;
        font-size: 0.93rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.01em !important;
        color: #3a5559 !important;
        background: transparent !important;
        min-height: 2.65rem !important;
    }
    div[data-testid="stTabs"] [data-baseweb="tab"]:hover {
        background: rgba(255,255,255,0.55) !important;
        color: #0d5c63 !important;
    }
    div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(180deg, #ffffff 0%, #f5fcfc 100%) !important;
        color: #0d5c63 !important;
        font-weight: 650 !important;
        box-shadow: 0 2px 10px rgba(13, 92, 99, 0.12), 0 1px 2px rgba(0,0,0,0.04) !important;
    }
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        background: transparent !important;
    }
    div[data-testid="stTabs"] [data-baseweb="tab-border"] {
        display: none !important;
    }
    div[data-testid="stTabs"] [role="tabpanel"] { padding-top: 0.6rem !important; }
    /* Subsection titles (markdown ###) inside tab panels */
    div[data-testid="stTabs"] [data-testid="stMarkdownContainer"] h3 {
        font-size: 1.12rem !important;
        font-weight: 650 !important;
        color: #0d5c63 !important;
        letter-spacing: -0.02em;
        margin: 1.15rem 0 0.4rem 0 !important;
        padding-bottom: 0.2rem;
        border-bottom: 1px solid rgba(13, 92, 99, 0.12);
    }
</style>
"""


def _fmt_count(n: int) -> str:
    if abs(n) < 1000:
        return str(int(n))
    return millify(float(n), precision=1)


def _fmt_score(x: float, precision: int = 2) -> str:
    return millify(float(x), precision=precision)


def _fmt_delta(d: float | None, precision: int = 2) -> str | None:
    if d is None or abs(d) < 1e-9:
        return None
    if d < 0:
        return "-" + millify(abs(float(d)), precision=precision)
    return millify(float(d), precision=precision)

st.set_page_config(
    page_title="Community Hubs | Insights",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)
DATA_DIR = Path(__file__).parent

# Ordered so box/bar charts show age groups left-to-right by life-course, not alphabetical / row order.
AGE_GROUP_ORDER = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]

SC_OPTIONS = ["bonding_score", "bridging_score", "linking_score", "overall_sc_score"]
SC_LABELS = {
    "bonding_score": "Bonding",
    "bridging_score": "Bridging",
    "linking_score": "Linking",
    "overall_sc_score": "Overall SC",
}

# Human-readable names for modelling drivers and chart axes (avoid raw column names in UI).
FEATURE_LABELS = {
    "visit_frequency_monthly": "Visit frequency (times per month)",
    "activity_types_count": "Number of activity types used",
    "perceived_safety": "Perceived safety",
    "perceived_accessibility": "Perceived accessibility",
    "awareness_of_programmes": "Awareness of programmes",
    "years_since_opening": "Years since hub opening",
    "outreach_intensity": "Outreach intensity",
    "resident_in_catchment_yes": "Lives in catchment (yes/no)",
    "recruited_by_volunteer_yes": "Recruited by volunteer (yes/no)",
    "amenity_diversity": "Amenity diversity (hub)",
    "integrated_programming_ratio": "Integrated programming share",
    "governance_openness": "Governance openness",
    "cci_total": "Community connectedness index (CCI)",
    # Raw respondent items (replace heart / hands / head hub scores in drivers)
    "q3_place_attachment": "Place attachment (survey item)",
    "q7_diverse_interactions": "Diverse interactions (survey item)",
    "q9_understand_governance": "Understands how hub is governed (survey item)",
}

MODIFIABLE_FEATURES = frozenset({
    "activity_types_count",
    "awareness_of_programmes",
    "outreach_intensity",
    "integrated_programming_ratio",
    "governance_openness",
    "visit_frequency_monthly",
    "perceived_accessibility",
})

HUB_METRIC_LABELS = {
    "hub_name": "Hub",
    "heart_score": "Heart score (emotional)",
    "head_score": "Head score (institutional)",
    "hands_score": "Hands score (programmes & practice)",
    "cci_total": "Community connectedness index (CCI)",
    "open_year": "Opening year",
    "years_since_opening": "Years since opening",
    "amenity_diversity": "Amenity diversity",
    "integrated_programming_ratio": "Integrated programming ratio",
    "governance_openness": "Governance openness",
}

SPATIAL_AXIS_LABELS = {
    "transit_access_score": "Transit access score",
    "service_gap_score": "Service gap score",
    "future_site_priority_score": "Future site priority score",
    "elderly_share_pct": "Elderly share (%)",
    "population_density_index": "Population density index",
}

OPS_Y_LABELS = {
    "attendance_total": "Total attendance (visits)",
    "integrated_programming_share": "Integrated programming share",
    "volunteers_active": "Active volunteers",
    "digital_engagement_total": "Digital engagement (sessions)",
}

@st.cache_data
def load_data():
    return (
        pd.read_csv(DATA_DIR/"hub_master.csv"),
        pd.read_csv(DATA_DIR/"respondent_survey.csv"),
        pd.read_csv(DATA_DIR/"programs_monthly.csv"),
        pd.read_csv(DATA_DIR/"spatial_context.csv"),
        pd.read_csv(DATA_DIR/"merged_modeling_dataset.csv"),
    )

hub_df, resp_df, ops_df, spatial_df, model_df = load_data()

HUB_ORDER = hub_df.sort_values("hub_id")["hub_name"].tolist()
HUB_COLOR_MAP = {name: HUB_COLOR_ACCENT[i % len(HUB_COLOR_ACCENT)] for i, name in enumerate(HUB_ORDER)}


def _prepare_spatial(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["sector"] = out["micro_area"].astype(str).str.split("-", n=1).str[-1].str.strip()
    seen = set(out["sector"].unique())
    cats = [s for s in SECTOR_ORDER if s in seen] + [x for x in seen if x not in SECTOR_ORDER]
    out["sector"] = pd.Categorical(out["sector"], categories=cats, ordered=True)
    return out


st.markdown(PAGE_STYLE, unsafe_allow_html=True)
st.markdown(
    """
    <div class="pres-hero">
        <p class="pres-title">Community hubs — planning & impact</p>
        <p class="pres-sub">A single view of hub capacity, resident social capital, drivers of outcomes, operations, and spatial priorities. Use this flow to brief stakeholders: <strong>where we are</strong> → <strong>what drives outcomes</strong> → <strong>what we could change</strong>.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

hub_names = ["All hubs"] + hub_df["hub_name"].tolist()

with st.container(border=True):
    st.markdown("**Scope** — choose what the charts focus on")
    f1, f2 = st.columns(2)
    with f1:
        selected_hub = st.selectbox("Hub", hub_names, index=0, help="All hubs or one hub across every tab.")
    with f2:
        selected_sc = st.selectbox(
            "Outcome to spotlight",
            SC_OPTIONS,
            index=1,
            format_func=lambda k: SC_LABELS.get(k, k),
            help="Used for KPIs, driver analysis, and several charts.",
        )
    st.markdown(
        '<p class="pres-filter-hint">Filters apply to every tab below. Switch tabs to walk through the story.</p>',
        unsafe_allow_html=True,
    )

if selected_hub == "All hubs":
    resp_f, ops_f, spatial_f, hub_f, model_f = resp_df.copy(), ops_df.copy(), spatial_df.copy(), hub_df.copy(), model_df.copy()
else:
    resp_f = resp_df[resp_df["hub_name"] == selected_hub].copy()
    ops_f = ops_df[ops_df["hub_name"] == selected_hub].copy()
    spatial_f = spatial_df[spatial_df["hub_name"] == selected_hub].copy()
    hub_f = hub_df[hub_df["hub_name"] == selected_hub].copy()
    model_f = model_df[model_df["hub_name"] == selected_hub].copy()

resp_f["age_group"] = pd.Categorical(resp_f["age_group"], categories=AGE_GROUP_ORDER, ordered=True)

def normalized(s):
    return (s - s.mean()) / (s.std(ddof=0) + 1e-9)

def add_flags(df):
    out = df.copy()
    out["resident_in_catchment_yes"] = (out["resident_in_catchment"] == "Yes").astype(int)
    out["recruited_by_volunteer_yes"] = (out["recruited_by_volunteer"] == "Yes").astype(int)
    return out

demo = add_flags(model_df)

# Driver demo: no heart / hands / head hub composite scores — use raw survey + hub/programme fields from merged_modeling_dataset.
driver_vars = {
    "bonding_score": {"visit_frequency_monthly":0.18,"activity_types_count":0.10,"perceived_safety":0.16,"q3_place_attachment":0.24,"years_since_opening":0.12,"outreach_intensity":0.10,"resident_in_catchment_yes":0.10},
    "bridging_score": {"visit_frequency_monthly":0.10,"activity_types_count":0.22,"perceived_accessibility":0.12,"q7_diverse_interactions":0.22,"amenity_diversity":0.14,"integrated_programming_ratio":0.12,"recruited_by_volunteer_yes":0.08},
    "linking_score": {"visit_frequency_monthly":0.08,"awareness_of_programmes":0.16,"q9_understand_governance":0.26,"governance_openness":0.18,"outreach_intensity":0.10,"recruited_by_volunteer_yes":0.10,"years_since_opening":0.12},
    "overall_sc_score": {"visit_frequency_monthly":0.12,"activity_types_count":0.12,"awareness_of_programmes":0.12,"cci_total":0.24,"integrated_programming_ratio":0.12,"governance_openness":0.14,"perceived_accessibility":0.14},
}

def _feature_label(var: str) -> str:
    return FEATURE_LABELS.get(var, var.replace("_", " ").title())


def global_driver_table(outcome):
    rows = []
    for var, w in driver_vars[outcome].items():
        imp = abs(w * normalized(demo[var])).mean()
        rows.append({
            "feature_id": var,
            "feature": _feature_label(var),
            "importance": imp,
            "modifiable": var in MODIFIABLE_FEATURES,
        })
    return pd.DataFrame(rows).sort_values("importance", ascending=False)

def local_driver_table(outcome, respondent_id):
    rows = []
    for var, w in driver_vars[outcome].items():
        zval = float(normalized(demo[var])[demo["respondent_id"] == respondent_id].iloc[0])
        rows.append({
            "feature_id": var,
            "feature": _feature_label(var),
            "contribution": w * zval,
            "modifiable": var in MODIFIABLE_FEATURES,
        })
    return pd.DataFrame(rows).sort_values("contribution", ascending=False)


LEVER_TYPE_LABELS = {
    True: "Modifiable (policy & operations)",
    False: "Non-modifiable (resident context)",
}

SHAP_LEVER_COLORS = {
    LEVER_TYPE_LABELS[True]: "#0d5c63",
    LEVER_TYPE_LABELS[False]: "#8a6fa8",
}


def global_signed_driver_table(outcome):
    """Cohort-average signed effect w·z (can be negative) — complements the magnitude-only global view."""
    rows = []
    for var, w in driver_vars[outcome].items():
        signed = float((w * normalized(demo[var])).mean())
        rows.append({
            "feature_id": var,
            "feature": _feature_label(var),
            "signed_effect": signed,
            "modifiable": var in MODIFIABLE_FEATURES,
        })
    return pd.DataFrame(rows)


def _z_for_person(respondent_id: str, outcome: str) -> dict[str, float]:
    return {
        var: float(normalized(demo[var])[demo["respondent_id"] == respondent_id].iloc[0])
        for var in driver_vars[outcome]
    }


def mock_counterfactual_score(outcome: str, respondent_id: str, delta_z: dict[str, float]) -> tuple[float, float, float]:
    """Returns (observed_y, counterfactual_y, delta_y) using linear Σ w·Δz on modifiable drivers only (mock)."""
    y_obs = float(model_df.loc[model_df["respondent_id"] == respondent_id, outcome].iloc[0])
    d_y = 0.0
    for var, w in driver_vars[outcome].items():
        if var not in MODIFIABLE_FEATURES:
            continue
        d_y += w * float(delta_z.get(var, 0.0))
    return y_obs, y_obs + d_y, d_y

def _base_figure_style(fig):
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Source Sans Pro, Lucida Grande, Verdana, sans-serif", size=13),
        colorway=PALETTE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(248,250,252,0.95)",
        margin=dict(l=48, r=24, t=56, b=48),
        title=dict(font=dict(size=15)),
        legend=dict(bgcolor="rgba(255,255,255,0.85)"),
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="rgba(13,92,99,0.08)", zeroline=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(13,92,99,0.08)", zeroline=False)


def show_chart(fig, *, presentation: bool = False, **kwargs):
    _base_figure_style(fig)
    if presentation:
        fig.update_layout(
            title=dict(font=dict(size=17, color="#0a3d42")),
            font=dict(size=12),
        )
    st.plotly_chart(fig, use_container_width=True, **kwargs)


def _legend_hub_row():
    """Wide horizontal legend tuned for the five hub swatches."""
    return dict(
        title=dict(text="Hub", font=dict(size=15, color="#0a3d42", family="Source Sans Pro, sans-serif")),
        orientation="h",
        yanchor="top",
        y=-0.32,
        x=0.5,
        xanchor="center",
        traceorder="normal",
        itemsizing="constant",
        itemwidth=56,
        bgcolor="rgba(255,255,255,0.97)",
        bordercolor="#0d5c63",
        borderwidth=1.5,
        font=dict(size=14, color="#1a3a40"),
        tracegroupgap=20,
    )


def _legend_sector_row():
    """Legend for North / East / South sectors (micro-areas)."""
    return dict(
        title=dict(text="Sector (catchment)", font=dict(size=15, color="#0a3d42")),
        orientation="h",
        yanchor="top",
        y=-0.09,
        x=0.5,
        xanchor="center",
        itemsizing="constant",
        itemwidth=48,
        bgcolor="rgba(255,255,255,0.97)",
        bordercolor="#0d5c63",
        borderwidth=1.5,
        font=dict(size=14),
    )


def show_opportunity_scatter(fig, *, height: int = 560, **kwargs):
    _base_figure_style(fig)
    fig.update_layout(
        margin=dict(l=60, r=60, t=88, b=140),
        legend=_legend_sector_row(),
        title=dict(font=dict(size=17, color="#0a3d42"), pad=dict(t=8, b=12)),
        height=height,
    )
    fig.update_traces(
        marker=dict(line=dict(width=1.6, color="rgba(255,255,255,0.95)"), opacity=0.96, sizemode="diameter")
    )
    fig.for_each_annotation(
        lambda a: a.update(
            text=f"<b>{a.text.split('=')[-1].strip()}</b>" if "=" in a.text else f"<b>{a.text}</b>",
            font=dict(size=12, color="#0d3d42"),
            bordercolor="rgba(13,92,99,0.2)",
            borderwidth=1,
            bgcolor="rgba(246,252,252,0.95)",
            align="left",
        )
    )
    st.plotly_chart(fig, use_container_width=True, **kwargs)


def show_priority_bar(fig, **kwargs):
    _base_figure_style(fig)
    fig.update_layout(
        margin=dict(l=56, r=48, t=72, b=220),
        legend=_legend_hub_row(),
        height=620,
        barmode="relative",
        title=dict(font=dict(size=17, color="#0a3d42")),
    )
    fig.update_xaxes(tickangle=-35, tickfont=dict(size=12), automargin=True)
    st.plotly_chart(fig, use_container_width=True, **kwargs)

def _delta_vs_baseline(series_filtered, series_all):
    m_f = float(series_filtered.mean())
    m_a = float(series_all.mean())
    d = round(m_f - m_a, 3)
    if abs(d) < 1e-9:
        return None
    return d

st.subheader("At a glance")
st.caption("Key numbers for your current hub filter and spotlight outcome — same scope on every tab below.")
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Hubs in view", _fmt_count(len(hub_f)))
with k2:
    st.metric("Respondents", _fmt_count(len(resp_f)))
with k3:
    d_sc = _delta_vs_baseline(resp_f[selected_sc], resp_df[selected_sc]) if selected_hub != "All hubs" else None
    st.metric(
        f"Avg {SC_LABELS[selected_sc]}",
        _fmt_score(float(resp_f[selected_sc].mean())),
        delta=_fmt_delta(d_sc),
        delta_color="normal",
    )
with k4:
    d_cci = _delta_vs_baseline(hub_f["cci_total"], hub_df["cci_total"]) if selected_hub != "All hubs" else None
    st.metric(
        "Avg CCI (hub capacity)",
        _fmt_score(float(hub_f["cci_total"].mean())),
        delta=_fmt_delta(d_cci),
        delta_color="normal",
    )

a1, a2, a3, a4 = st.columns(4)
with a1:
    d = _delta_vs_baseline(resp_f["bonding_score"], resp_df["bonding_score"]) if selected_hub != "All hubs" else None
    st.metric("Avg bonding", _fmt_score(float(resp_f["bonding_score"].mean())), delta=_fmt_delta(d), delta_color="normal")
with a2:
    d = _delta_vs_baseline(resp_f["bridging_score"], resp_df["bridging_score"]) if selected_hub != "All hubs" else None
    st.metric("Avg bridging", _fmt_score(float(resp_f["bridging_score"].mean())), delta=_fmt_delta(d), delta_color="normal")
with a3:
    d = _delta_vs_baseline(resp_f["linking_score"], resp_df["linking_score"]) if selected_hub != "All hubs" else None
    st.metric("Avg linking", _fmt_score(float(resp_f["linking_score"].mean())), delta=_fmt_delta(d), delta_color="normal")
with a4:
    d = _delta_vs_baseline(resp_f["overall_sc_score"], resp_df["overall_sc_score"]) if selected_hub != "All hubs" else None
    st.metric("Avg overall SC", _fmt_score(float(resp_f["overall_sc_score"].mean())), delta=_fmt_delta(d), delta_color="normal")

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Hub & capacity", "Social capital", "Drivers & scenarios", "Operations", "Spatial priorities"]
)

with tab1:
    st.subheader("Hub & capacity")
    st.caption("Heart / Head / Hands and CCI summarise each hub’s profile in one place.")
    st.markdown("### Data table")
    _hub_cols = ["hub_name", "heart_score", "head_score", "hands_score", "cci_total", "open_year", "years_since_opening", "amenity_diversity", "integrated_programming_ratio", "governance_openness"]
    st.dataframe(hub_f[_hub_cols].rename(columns=HUB_METRIC_LABELS), use_container_width=True)
    st.markdown("### Profile comparison")
    bars = hub_f.melt(id_vars=["hub_name"], value_vars=["heart_score", "head_score", "hands_score", "cci_total"], var_name="metric", value_name="score")
    bars["metric"] = bars["metric"].map(lambda m: HUB_METRIC_LABELS.get(m, m))
    fig = px.bar(
        bars,
        x="hub_name",
        y="score",
        color="metric",
        barmode="group",
        title="Heart, Head, Hands & CCI — side by side",
        color_discrete_sequence=PALETTE,
        labels={"hub_name": "Hub", "score": "Score"},
    )
    show_chart(fig, presentation=True)

with tab2:
    st.subheader("Social capital")
    st.caption("Resident-level outcomes by hub, age, and audience — who experiences what.")
    st.markdown("### Mean scores by hub")
    sc_comp = resp_f.groupby("hub_name")[["bonding_score", "bridging_score", "linking_score", "overall_sc_score"]].mean().reset_index()
    sc_long = sc_comp.melt(id_vars="hub_name", var_name="dimension", value_name="score")
    sc_long["dimension"] = sc_long["dimension"].map(SC_LABELS)
    fig = px.bar(
        sc_long,
        x="hub_name",
        y="score",
        color="dimension",
        barmode="group",
        title="Mean social capital scores by hub",
        color_discrete_sequence=PALETTE,
        labels={"hub_name": "Hub", "score": "Mean score"},
    )
    show_chart(fig, presentation=True)
    st.markdown("### Spotlight outcome — distribution")
    x1,x2 = st.columns(2)
    with x1:
        fig = px.box(
            resp_f,
            x="age_group",
            y=selected_sc,
            color="age_group",
            title=f"{SC_LABELS[selected_sc]} by age band",
            color_discrete_sequence=PALETTE,
            category_orders={"age_group": AGE_GROUP_ORDER},
            labels={selected_sc: SC_LABELS[selected_sc], "age_group": "Age group"},
        )
        # Plotly sometimes ignores pandas.Categorical order on box plots — pin axis order explicitly.
        fig.update_xaxes(
            type="category",
            categoryorder="array",
            categoryarray=[a for a in AGE_GROUP_ORDER if a in set(resp_f["age_group"].astype(str))],
        )
        show_chart(fig, presentation=True)
    with x2:
        fig = px.box(
            resp_f,
            x="user_archetype",
            y=selected_sc,
            color="user_archetype",
            title=f"{SC_LABELS[selected_sc]} by audience type",
            color_discrete_sequence=PALETTE,
            labels={selected_sc: SC_LABELS[selected_sc], "user_archetype": "User archetype"},
        )
        show_chart(fig, presentation=True)
    st.markdown("### Reach by age")
    mix = resp_f.groupby(["hub_name", "age_group"], observed=True).size().reset_index(name="n")
    fig = px.bar(
        mix,
        x="hub_name",
        y="n",
        color="age_group",
        title="Respondent counts by hub and age band",
        color_discrete_sequence=PALETTE,
        category_orders={"age_group": AGE_GROUP_ORDER},
        labels={"hub_name": "Hub", "n": "Respondents", "age_group": "Age group"},
    )
    show_chart(fig, presentation=True)

with tab3:
    st.subheader("What drives the outcome?")
    st.markdown(
        '<div class="how-read"><strong>How to read the driver charts:</strong> Bars extend <strong>left</strong> if a factor '
        "tends to <strong>lower</strong> the score, and <strong>right</strong> if it <strong>raises</strong> it. "
        "<strong>Teal</strong> = policy or operations you can change; <strong>purple</strong> = resident or context factors held fixed in scenarios below.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("### Cohort-level drivers")
    g = global_driver_table(selected_sc)
    g_plot = g.assign(
        lever_type=g["modifiable"].map(LEVER_TYPE_LABELS),
    )
    fig = px.bar(
        g_plot,
        x="importance",
        y="feature",
        color="lever_type",
        orientation="h",
        title=f"1 · Which factors matter most? (typical strength) — {SC_LABELS[selected_sc]}",
        color_discrete_map=SHAP_LEVER_COLORS,
        category_orders={"lever_type": [LEVER_TYPE_LABELS[True], LEVER_TYPE_LABELS[False]]},
        labels={"importance": "Strength of driver (higher = more influence)", "feature": "Driver", "lever_type": "Type"},
    )
    fig.update_layout(legend_title_text="Teal = modifiable · Purple = context")
    show_chart(fig, presentation=True)

    gs = global_signed_driver_table(selected_sc)
    gs_plot = gs.assign(
        lever_type=gs["modifiable"].map(LEVER_TYPE_LABELS),
    )
    gs_plot = gs_plot.assign(_abs=np.abs(gs_plot["signed_effect"])).sort_values("_abs", ascending=True)
    fig = px.bar(
        gs_plot,
        x="signed_effect",
        y="feature",
        color="lever_type",
        orientation="h",
        title=f"2 · Cohort average: does each factor help or hurt {SC_LABELS[selected_sc]}?",
        color_discrete_map=SHAP_LEVER_COLORS,
        category_orders={"lever_type": [LEVER_TYPE_LABELS[True], LEVER_TYPE_LABELS[False]]},
        labels={
            "signed_effect": "Effect on score (← hurts · helps →)",
            "feature": "Driver",
            "lever_type": "Type",
        },
    )
    fig.update_xaxes(zeroline=True, zerolinewidth=2, zerolinecolor="rgba(60,60,60,0.6)")
    fig.update_layout(legend_title_text="Teal = modifiable · Purple = context")
    fig.update_yaxes(title_text="")
    show_chart(fig, presentation=True)

    st.markdown("### One resident — deep dive")
    person = st.selectbox("Choose respondent ID", resp_f["respondent_id"].tolist(), index=0)
    loc = local_driver_table(selected_sc, person)
    loc_plot = loc.assign(lever_type=loc["modifiable"].map(LEVER_TYPE_LABELS))
    loc_plot = loc_plot.assign(_abs=np.abs(loc_plot["contribution"])).sort_values("_abs", ascending=True)
    fig = px.bar(
        loc_plot,
        x="contribution",
        y="feature",
        color="lever_type",
        orientation="h",
        title=f"3 · Resident {person}: factor-by-factor impact on {SC_LABELS[selected_sc]}",
        color_discrete_map=SHAP_LEVER_COLORS,
        category_orders={"lever_type": [LEVER_TYPE_LABELS[True], LEVER_TYPE_LABELS[False]]},
        labels={
            "contribution": "Effect on score (← hurts · helps →)",
            "feature": "Driver",
            "lever_type": "Type",
        },
    )
    fig.update_xaxes(zeroline=True, zerolinewidth=2, zerolinecolor="rgba(60,60,60,0.6)")
    fig.update_layout(legend_title_text="Teal = modifiable · Purple = context")
    fig.update_yaxes(title_text="")
    show_chart(fig, presentation=True)

    scope = f"{selected_sc}_{person}".replace(" ", "_")
    mod_keys = [v for v in driver_vars[selected_sc] if v in MODIFIABLE_FEATURES]
    nm_keys = [v for v in driver_vars[selected_sc] if v not in MODIFIABLE_FEATURES]
    z_baseline = _z_for_person(person, selected_sc)

    st.markdown("### Scenario lab — what-if (demo model)")
    with st.expander("Open scenario controls & live prediction", expanded=True):
        st.markdown(
            "Use the sliders to **simulate** how shifting **modifiable** factors might change the spotlight outcome. "
            "The **model output updates live** as you drag. Context factors stay fixed for the selected resident."
        )
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("Load demo: positive shifts", key=f"wi_up_{scope}"):
                rng = np.random.default_rng(42)
                for v in mod_keys:
                    st.session_state[f"wiz_{scope}_{v}"] = float(rng.uniform(0.25, 1.15))
        with b2:
            if st.button("Load demo: negative shifts", key=f"wi_dn_{scope}"):
                rng = np.random.default_rng(7)
                for v in mod_keys:
                    st.session_state[f"wiz_{scope}_{v}"] = float(rng.uniform(-1.35, -0.2))
        with b3:
            if st.button("Clear all shifts", key=f"wi_rs_{scope}"):
                for v in mod_keys:
                    st.session_state[f"wiz_{scope}_{v}"] = 0.0

        st.markdown("**Fixed for this resident (not on sliders)**")
        nm_df = pd.DataFrame(
            {"Factor": [_feature_label(v) for v in nm_keys], "Baseline position": [f"{z_baseline[v]:.2f}" for v in nm_keys]}
        )
        st.dataframe(nm_df, use_container_width=True, hide_index=True)

        st.markdown("**Programme levers you can move**")
        delta_z = {}
        for v in mod_keys:
            k = f"wiz_{scope}_{v}"
            if k not in st.session_state:
                st.session_state[k] = 0.0
            delta_z[v] = st.slider(
                _feature_label(v),
                -2.0,
                2.0,
                step=0.05,
                key=k,
                help="Standardised shift vs this person’s baseline. Demo rule: new score ≈ current + weighted sum of shifts.",
            )

        y_obs, y_cf, d_y = mock_counterfactual_score(selected_sc, person, delta_z)
        _omin = float(model_df[selected_sc].min())
        _omax = float(model_df[selected_sc].max())
        _span = max(_omax - _omin, 1e-9)
        _prog = float(np.clip((y_cf - _omin) / _span, 0.0, 1.0))

        st.divider()
        with st.container(border=True):
            st.markdown(f"#### Model readout · {SC_LABELS[selected_sc]}")
            st.caption(
                f"Simplified linear demo (not production ML). Cohort range for this outcome: {_omin:.2f}–{_omax:.2f}. "
                "The bar shows where your scenario sits in that band."
            )
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Today (observed)", f"{y_obs:.3f}")
            with c2:
                st.metric(
                    "Scenario (after sliders)",
                    f"{y_cf:.3f}",
                    delta=f"{d_y:+.3f} vs today",
                    delta_color="normal",
                )
            st.progress(_prog)
            st.caption("Illustrative position along the cohort min–max range for this outcome.")

    st.markdown("### Compare two hubs")
    a,b = st.columns(2)
    with a:
        hub_a = st.selectbox("Hub A", hub_df["hub_name"].tolist(), index=0)
    with b:
        hub_b = st.selectbox("Hub B", hub_df["hub_name"].tolist(), index=1)
    a_ids = model_df[model_df["hub_name"] == hub_a]["respondent_id"].head(25).tolist()
    b_ids = model_df[model_df["hub_name"] == hub_b]["respondent_id"].head(25).tolist()
    a_df = pd.concat([local_driver_table(selected_sc, rid) for rid in a_ids]).groupby("feature_id", as_index=False)["contribution"].mean()
    b_df = pd.concat([local_driver_table(selected_sc, rid) for rid in b_ids]).groupby("feature_id", as_index=False)["contribution"].mean()
    gap = a_df.merge(b_df, on="feature_id", suffixes=("_a", "_b"))
    gap["gap_a_minus_b"] = gap["contribution_a"] - gap["contribution_b"]
    gap["feature"] = gap["feature_id"].map(_feature_label)
    fig = px.bar(
        gap.sort_values("gap_a_minus_b"),
        x="gap_a_minus_b",
        y="feature",
        orientation="h",
        title=f"4 · Comparing two hubs: {hub_a} vs {hub_b} (average driver difference)",
        color_discrete_sequence=PALETTE,
        labels={
            "gap_a_minus_b": f"Extra impact at {hub_a} vs {hub_b} (← favours {hub_b} · favours {hub_a} →)",
            "feature": "Driver",
        },
    )
    fig.update_xaxes(zeroline=True, zerolinewidth=1.5, zerolinecolor="rgba(60,60,60,0.5)")
    show_chart(fig, presentation=True)

with tab4:
    st.subheader("Operations")
    st.caption(
        "Monthly delivery indicators for the selected hub filter: footfall, how much programming is cross-cutting, "
        "volunteer engagement, and digital reach."
    )
    _mo = ops_f["month"].min()
    _mx = ops_f["month"].max()
    _hlist = ", ".join(sorted(ops_f["hub_name"].unique()))
    st.caption(f"**Series:** {_mo} → {_mx} · **Hubs in view:** {_hlist}")

    om1, om2, om3 = st.columns(3)
    with om1:
        st.metric("Peak monthly attendance (in view)", f"{int(ops_f['attendance_total'].max()):,}")
    with om2:
        st.metric("Avg integrated programming share", f"{ops_f['integrated_programming_share'].mean():.0%}")
    with om3:
        st.metric("Avg active volunteers / month", f"{int(round(ops_f['volunteers_active'].mean())):,}")

    st.markdown("### Footfall — monthly attendance")
    fig = px.line(
        ops_f,
        x="month",
        y="attendance_total",
        color="hub_name",
        markers=True,
        title="1 · Total visits by hub (monthly)",
        color_discrete_map=HUB_COLOR_MAP,
        labels={"month": "Month", "attendance_total": OPS_Y_LABELS["attendance_total"], "hub_name": "Hub"},
    )
    fig.update_layout(hovermode="x unified")
    fig.update_yaxes(title_text="Visits", rangemode="tozero")
    show_chart(fig, presentation=True)

    st.markdown("### Programme mix & people")
    o1, o2 = st.columns(2)
    with o1:
        fig = px.line(
            ops_f,
            x="month",
            y="integrated_programming_share",
            color="hub_name",
            markers=True,
            title="2 · Share of integrated programming",
            color_discrete_map=HUB_COLOR_MAP,
            labels={"month": "Month", "integrated_programming_share": OPS_Y_LABELS["integrated_programming_share"], "hub_name": "Hub"},
        )
        fig.update_yaxes(title_text="Share of programme", tickformat=".0%", range=[0, 1])
        fig.update_layout(hovermode="x unified")
        show_chart(fig, presentation=True)
    with o2:
        fig = px.line(
            ops_f,
            x="month",
            y="volunteers_active",
            color="hub_name",
            markers=True,
            title="3 · Active volunteers",
            color_discrete_map=HUB_COLOR_MAP,
            labels={"month": "Month", "volunteers_active": OPS_Y_LABELS["volunteers_active"], "hub_name": "Hub"},
        )
        fig.update_yaxes(title_text="Volunteers", rangemode="tozero")
        fig.update_layout(hovermode="x unified")
        show_chart(fig, presentation=True)

    st.markdown("### Digital engagement")
    fig = px.line(
        ops_f,
        x="month",
        y="digital_engagement_total",
        color="hub_name",
        markers=True,
        title="4 · Digital engagement (proxy volume)",
        color_discrete_map=HUB_COLOR_MAP,
        labels={"month": "Month", "digital_engagement_total": OPS_Y_LABELS["digital_engagement_total"], "hub_name": "Hub"},
    )
    fig.update_yaxes(title_text="Sessions (proxy)", rangemode="tozero")
    fig.update_layout(hovermode="x unified")
    show_chart(fig, presentation=True)

with tab5:
    st.subheader("Spatial priorities")
    st.caption("Catchment micro-areas: transit access vs service gap, bubble size = investment priority.")
    st.markdown("### Opportunity map")
    sp = _prepare_spatial(spatial_f)
    hubs_in_view = [h for h in HUB_ORDER if h in set(sp["hub_name"])]
    sec_in_view = [s for s in SECTOR_ORDER if s in set(sp["sector"])]
    n_hub = len(hubs_in_view)
    facet_wrap = max(1, min(n_hub, 3))
    n_rows = max(1, (n_hub + facet_wrap - 1) // facet_wrap)
    scatter_height = min(1200, max(500, 160 + n_rows * 380))

    fig = px.scatter(
        sp,
        x="transit_access_score",
        y="service_gap_score",
        size="future_site_priority_score",
        facet_col="hub_name",
        facet_col_wrap=facet_wrap,
        facet_col_spacing=0.11,
        facet_row_spacing=0.18,
        color="sector",
        color_discrete_map={k: v for k, v in SECTOR_COLOR_MAP.items() if k in sec_in_view},
        symbol="sector",
        symbol_map={k: v for k, v in SECTOR_SYMBOL_MAP.items() if k in sec_in_view},
        category_orders={"hub_name": hubs_in_view, "sector": sec_in_view},
        size_max=5,
        hover_name="micro_area",
        hover_data=["hub_name", "sector", "elderly_share_pct", "population_density_index", "future_site_priority_score"],
        title="Opportunity map — one panel per hub · sector = color + shape",
        labels={
            "transit_access_score": SPATIAL_AXIS_LABELS["transit_access_score"],
            "service_gap_score": SPATIAL_AXIS_LABELS["service_gap_score"],
            "future_site_priority_score": SPATIAL_AXIS_LABELS["future_site_priority_score"],
            "hub_name": "Hub",
        },
    )
    show_opportunity_scatter(fig, height=scatter_height)

    st.markdown("### Priority ranking")
    bar_df = sp.sort_values("future_site_priority_score", ascending=False)
    fig = px.bar(
        bar_df,
        x="micro_area",
        y="future_site_priority_score",
        color="hub_name",
        color_discrete_map=HUB_COLOR_MAP,
        category_orders={"hub_name": hubs_in_view, "micro_area": bar_df["micro_area"].tolist()},
        title="Ranking micro-areas for future investment priority",
        labels={
            "micro_area": "Micro-area",
            "future_site_priority_score": SPATIAL_AXIS_LABELS["future_site_priority_score"],
            "hub_name": "Hub",
        },
    )
    fig.update_traces(
        texttemplate="%{y:.0f}",
        textposition="outside",
        textfont=dict(size=12, color="#0d3d42"),
        marker_line_width=0.6,
        marker_line_color="rgba(255,255,255,0.7)",
    )
    show_priority_bar(fig)
