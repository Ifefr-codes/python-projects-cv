"""
Interactive Engineering Data Dashboard
----------------------------------------
Loads a CSV/Excel dataset and visualizes it with Plotly charts and KPI cards.
Usage: streamlit run dashboard_app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Engineering Data Dashboard",
    page_icon="📊",
    layout="wide",
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .kpi-card {
        background: #f0f4f8;
        border-radius: 10px;
        padding: 16px 20px;
        border-left: 4px solid #1A3A5C;
        margin-bottom: 8px;
    }
    .kpi-label { font-size: 12px; color: #666; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-value { font-size: 28px; font-weight: 700; color: #1A3A5C; }
    .kpi-sub   { font-size: 12px; color: #888; }
</style>
""", unsafe_allow_html=True)

# ── SAMPLE DATA GENERATOR ─────────────────────────────────────────────────────

def generate_sample_data():
    import numpy as np
    from datetime import datetime, timedelta
    dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(180)]
    np.random.seed(42)
    df = pd.DataFrame({
        "date":        dates,
        "temperature": np.random.normal(85, 10, 180).round(2),
        "pressure":    np.random.normal(250, 30, 180).round(2),
        "flow_rate":   np.random.normal(120, 20, 180).round(2),
        "efficiency":  np.random.normal(78, 8, 180).clip(50, 100).round(2),
        "unit":        np.random.choice(["Unit A", "Unit B", "Unit C"], 180),
        "status":      np.random.choice(["Normal", "Warning", "Critical"], 180, p=[0.75, 0.15, 0.10]),
    })
    return df


# ── DATA LOADER ───────────────────────────────────────────────────────────────

@st.cache_data
def load_data(uploaded_file):
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    else:
        return pd.read_excel(uploaded_file)


# ── KPI CARD ──────────────────────────────────────────────────────────────────

def kpi_card(label, value, sub=""):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)


# ── MAIN APP ──────────────────────────────────────────────────────────────────

st.title("📊 Engineering Data Dashboard")
st.caption("Upload your CSV or Excel dataset to explore trends and KPIs interactively.")

# Sidebar
with st.sidebar:
    st.header("⚙️ Data Source")
    use_sample = st.checkbox("Use sample data", value=True)
    uploaded_file = None

    if not use_sample:
        uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])

# Load data
if use_sample:
    df = generate_sample_data()
    st.info("📋 Using built-in sample dataset (180 days of sensor readings).")
elif uploaded_file:
    df = load_data(uploaded_file)
    st.success(f"✅ Loaded: **{uploaded_file.name}**")
else:
    st.info("👈 Upload a file or enable sample data in the sidebar.")
    st.stop()

# ── SIDEBAR FILTERS ───────────────────────────────────────────────────────────

with st.sidebar:
    st.header("🔍 Filters")

    # Date filter (if date column exists)
    date_cols = [c for c in df.columns if "date" in c.lower() or "time" in c.lower()]
    if date_cols:
        date_col = st.selectbox("Date column", date_cols)
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        min_d, max_d = df[date_col].min(), df[date_col].max()
        date_range = st.date_input("Date range", [min_d, max_d])
        if len(date_range) == 2:
            df = df[(df[date_col] >= pd.Timestamp(date_range[0])) &
                    (df[date_col] <= pd.Timestamp(date_range[1]))]

    # Category filter (if categorical column exists)
    cat_cols = [c for c in df.select_dtypes(include="object").columns
                if df[c].nunique() <= 20]
    if cat_cols:
        cat_col = st.selectbox("Filter by category", ["(none)"] + cat_cols)
        if cat_col != "(none)":
            options = df[cat_col].unique().tolist()
            selected = st.multiselect("Select values", options, default=options)
            df = df[df[cat_col].isin(selected)]

    st.markdown("---")
    st.caption(f"Showing **{len(df):,}** rows")

# ── KPI CARDS ─────────────────────────────────────────────────────────────────

st.subheader("Key Metrics")
num_cols = df.select_dtypes(include="number").columns.tolist()
kpi_cols = num_cols[:4]  # Show first 4 numeric columns as KPIs

cols = st.columns(len(kpi_cols)) if kpi_cols else []
for i, col_name in enumerate(kpi_cols):
    with cols[i]:
        mean_val = df[col_name].mean()
        max_val  = df[col_name].max()
        kpi_card(
            col_name.replace("_", " ").title(),
            f"{mean_val:.1f}",
            f"Max: {max_val:.1f}"
        )

st.divider()

# ── CHART SECTION ─────────────────────────────────────────────────────────────

st.subheader("📈 Visualizations")

if num_cols:
    tab1, tab2, tab3 = st.tabs(["Time Series", "Distribution", "Correlation"])

    with tab1:
        y_col = st.selectbox("Select metric", num_cols, key="ts_y")
        color_col = cat_cols[0] if cat_cols else None

        if date_cols:
            fig = px.line(
                df.sort_values(date_col), x=date_col, y=y_col,
                color=color_col,
                title=f"{y_col.replace('_', ' ').title()} Over Time",
                template="plotly_white",
            )
        else:
            fig = px.line(df, y=y_col, color=color_col,
                          title=f"{y_col.replace('_', ' ').title()} Trend",
                          template="plotly_white")

        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        hist_col = st.selectbox("Select column", num_cols, key="hist_col")
        fig2 = px.histogram(
            df, x=hist_col, color=cat_cols[0] if cat_cols else None,
            nbins=30, title=f"Distribution of {hist_col.replace('_', ' ').title()}",
            template="plotly_white", marginal="box",
        )
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        if len(num_cols) >= 2:
            c1, c2 = st.columns(2)
            x_axis = c1.selectbox("X axis", num_cols, index=0)
            y_axis = c2.selectbox("Y axis", num_cols, index=min(1, len(num_cols)-1))
            fig3 = px.scatter(
                df, x=x_axis, y=y_axis,
                color=cat_cols[0] if cat_cols else None,
                trendline="ols",
                title=f"{x_axis.title()} vs {y_axis.title()}",
                template="plotly_white",
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Need at least 2 numeric columns for correlation chart.")

# ── DATA TABLE ────────────────────────────────────────────────────────────────

st.divider()
with st.expander("📋 View Raw Data"):
    st.dataframe(df.head(200), use_container_width=True)

    # Download cleaned data
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    st.download_button(
        "⬇️ Download as Excel",
        data=buffer.getvalue(),
        file_name="dashboard_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
