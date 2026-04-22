import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Data Cleaner", page_icon="🧹", layout="wide")

st.title("🧹 Data Cleaning Web App")
st.markdown("Upload a CSV file, clean it, and download the result.")

# ── Sidebar: cleaning options ──────────────────────────────────────────────
st.sidebar.header("⚙️ Cleaning Options")
remove_duplicates   = st.sidebar.checkbox("Remove duplicate rows",        value=True)
fill_numeric        = st.sidebar.checkbox("Fill missing numbers with 0",   value=True)
fill_text           = st.sidebar.checkbox("Fill missing text with 'Unknown'", value=True)
strip_whitespace    = st.sidebar.checkbox("Strip whitespace from text",    value=True)
lowercase_text      = st.sidebar.checkbox("Lowercase all text columns",    value=False)
drop_empty_cols     = st.sidebar.checkbox("Drop fully-empty columns",      value=True)

# ── File upload ────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])

if uploaded_file:
    # Read raw data
    df_raw = pd.read_csv(uploaded_file)

    # ── Raw data ──────────────────────────────────────────────────────────
    st.subheader("📋 Raw Data")
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows",    df_raw.shape[0])
    col2.metric("Columns", df_raw.shape[1])
    col3.metric("Missing values", int(df_raw.isnull().sum().sum()))
    st.dataframe(df_raw, use_container_width=True)

    with st.expander("🔍 Raw data info"):
        buf = io.StringIO()
        df_raw.info(buf=buf)
        st.text(buf.getvalue())
        st.write("**Missing values per column:**")
        st.dataframe(df_raw.isnull().sum().rename("Missing").reset_index()
                     .rename(columns={"index": "Column"}))

    # ── Clean ─────────────────────────────────────────────────────────────
    if st.button("🚀 Clean Data", type="primary"):
        df_clean = df_raw.copy()
        log = []

        if drop_empty_cols:
            before = df_clean.shape[1]
            df_clean.dropna(axis=1, how="all", inplace=True)
            dropped = before - df_clean.shape[1]
            if dropped:
                log.append(f"✅ Dropped {dropped} fully-empty column(s).")

        if remove_duplicates:
            before = len(df_clean)
            df_clean.drop_duplicates(inplace=True)
            removed = before - len(df_clean)
            log.append(f"✅ Removed {removed} duplicate row(s).")

        # Detect column types
        num_cols  = df_clean.select_dtypes(include="number").columns.tolist()
        text_cols = df_clean.select_dtypes(include="object").columns.tolist()

        if fill_numeric and num_cols:
            df_clean[num_cols] = df_clean[num_cols].fillna(0)
            log.append(f"✅ Filled missing numeric values with 0 in: {', '.join(num_cols)}.")

        if fill_text and text_cols:
            df_clean[text_cols] = df_clean[text_cols].fillna("Unknown")
            log.append(f"✅ Filled missing text values with 'Unknown' in: {', '.join(text_cols)}.")

        if strip_whitespace and text_cols:
            df_clean[text_cols] = df_clean[text_cols].apply(
                lambda col: col.str.strip() if col.dtype == object else col)
            log.append(f"✅ Stripped leading/trailing whitespace from text columns.")

        if lowercase_text and text_cols:
            df_clean[text_cols] = df_clean[text_cols].apply(
                lambda col: col.str.lower() if col.dtype == object else col)
            log.append(f"✅ Lowercased all text columns.")

        # ── Summary Report ────────────────────────────────────────────────
        duplicates_removed  = df_raw.shape[0] - df_raw.drop_duplicates().shape[0] if remove_duplicates else 0
        missing_before      = int(df_raw.isnull().sum().sum())
        missing_after       = int(df_clean.isnull().sum().sum())
        missing_handled     = missing_before - missing_after
        cols_dropped        = df_raw.shape[1] - df_clean.shape[1]
        rows_delta          = df_clean.shape[0] - df_raw.shape[0]   # negative = removed

        st.markdown("---")
        st.subheader("📊 Cleaning Summary Report")

        # ── Top KPI row ───────────────────────────────────────────────────
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Rows Before",    df_raw.shape[0])
        k2.metric("Rows After",     df_clean.shape[0],
                  delta=rows_delta, delta_color="inverse")
        k3.metric("Duplicates Removed", duplicates_removed,
                  delta=f"-{duplicates_removed}" if duplicates_removed else "0",
                  delta_color="inverse")
        k4.metric("Missing Values Handled", missing_handled,
                  delta=f"-{missing_handled}" if missing_handled else "0",
                  delta_color="inverse")
        k5.metric("Columns Dropped", cols_dropped,
                  delta=f"-{cols_dropped}" if cols_dropped else "0",
                  delta_color="inverse")

        st.markdown("")

        # ── Two-column detail cards ───────────────────────────────────────
        left, right = st.columns(2)

        with left:
            st.markdown("#### 🗂 Row Summary")
            row_summary = pd.DataFrame({
                "Metric": ["Total rows (before)", "Duplicate rows removed",
                            "Rows after cleaning", "Rows retained (%)"],
                "Value": [
                    df_raw.shape[0],
                    duplicates_removed,
                    df_clean.shape[0],
                    f"{df_clean.shape[0] / df_raw.shape[0] * 100:.1f}%" if df_raw.shape[0] else "—",
                ]
            })
            st.dataframe(row_summary, use_container_width=True, hide_index=True)

        with right:
            st.markdown("#### 🩹 Missing Values Summary")
            mv_summary = pd.DataFrame({
                "Metric": ["Missing values (before)", "Missing values (after)",
                           "Values filled / handled", "Completeness (after)"],
                "Value": [
                    missing_before,
                    missing_after,
                    missing_handled,
                    f"{(1 - missing_after / max(df_clean.size, 1)) * 100:.1f}%",
                ]
            })
            st.dataframe(mv_summary, use_container_width=True, hide_index=True)

        # ── Per-column missing values breakdown ───────────────────────────
        with st.expander("🔬 Per-column missing values breakdown"):
            col_stats = pd.DataFrame({
                "Column":          df_raw.columns,
                "Type":            df_raw.dtypes.astype(str).values,
                "Missing Before":  df_raw.isnull().sum().values,
                "Missing After":   [df_clean[c].isnull().sum() if c in df_clean.columns else "—"
                                    for c in df_raw.columns],
                "% Missing Before": (df_raw.isnull().mean() * 100).round(1).astype(str) + "%",
            })
            st.dataframe(col_stats, use_container_width=True, hide_index=True)

        # ── Cleaning log ──────────────────────────────────────────────────
        st.markdown("#### 📝 Step-by-step Cleaning Log")
        if log:
            for entry in log:
                st.write(entry)
        else:
            st.info("No changes were made (all options unchecked, or nothing to clean).")

        st.markdown("---")

        # ── Cleaned data table ────────────────────────────────────────────
        st.subheader("✨ Cleaned Data")
        st.dataframe(df_clean, use_container_width=True)

        # ── Download ──────────────────────────────────────────────────────
        st.subheader("⬇️ Download Cleaned CSV")
        csv_bytes = df_clean.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download cleaned_data.csv",
            data=csv_bytes,
            file_name="cleaned_data.csv",
            mime="text/csv",
        )

else:
    st.info("👆 Upload a CSV file to get started.")

    # Sample data hint
    with st.expander("💡 Need sample data? Click to see example CSV content"):
        sample = """Name,Age,City,Salary
Alice,30,New York,70000
Bob,,Los Angeles,
Alice,30,New York,70000
Charlie,25, Chicago ,50000
,28,Houston,60000
Diana,35,Phoenix,80000
"""
        st.code(sample, language="text")
        st.caption("Copy the above into a .csv file and upload it to test the app.")
