import streamlit as st
import pandas as pd
from matplotlib_venn import venn2
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Fruits & Vegetables Venn Diagram", layout="wide")

st.title("🍎 Fruits & Vegetables — Unsafe Sample Summary & Venn Diagram")

uploaded_file = st.file_uploader("📤 Upload your Key Parameter CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # --- Read File ---
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success(f"✅ File uploaded successfully with {len(df)} rows and {len(df.columns)} columns!")

    # --- Auto-detect columns ---
    cols_lower = [c.lower() for c in df.columns]

    # Commodity column
    col_commodity = next((c for c in df.columns if "commodity" in c.lower()), None)
    # Metal unsafe column
    col_metal = next((c for c in df.columns if ("metal" in c.lower() and "unsafe" in c.lower()) or "metal_unsafe" in c.lower()), None)
    # Pesticide unsafe column
    col_pesticide = next((c for c in df.columns if ("pesticide" in c.lower() and "unsafe" in c.lower()) or "pest_unsafe" in c.lower()), None)

    # --- Validate ---
    missing = [name for name, col in {
        "Commodity": col_commodity,
        "Metal Contaminants Unsafe": col_metal,
        "Pesticide Residue Unsafe": col_pesticide
    }.items() if col is None]

    if missing:
        st.error(f"❌ Missing expected columns: {', '.join(missing)}\n\nColumns found: {list(df.columns)}")
        st.stop()

    # Convert to bool safely
    df[col_metal] = df[col_metal].apply(lambda x: str(x).strip().lower() in ["1", "true", "yes", "unsafe", "fail", "non-compliant"])
    df[col_pesticide] = df[col_pesticide].apply(lambda x: str(x).strip().lower() in ["1", "true", "yes", "unsafe", "fail", "non-compliant"])

    # --- Sidebar Controls ---
    commodities = ["Overall"] + sorted(df[col_commodity].dropna().unique().tolist())
    selected_commodity = st.sidebar.selectbox("Select Commodity", commodities)
    st.sidebar.markdown("---")
    font_size = st.sidebar.slider("Font Size", 8, 24, 14)
    fig_size = st.sidebar.slider("Figure Size", 3, 10, 5)

    # --- Filter data ---
    data = df if selected_commodity == "Overall" else df[df[col_commodity] == selected_commodity]

    # --- Compute counts ---
    metal_only = len(data[(data[col_metal]) & (~data[col_pesticide])])
    pesticide_only = len(data[(data[col_pesticide]) & (~data[col_metal])])
    both = len(data[(data[col_metal]) & (data[col_pesticide])])

    # --- Draw Venn Diagram ---
    st.subheader(f"Venn Diagram — {selected_commodity}")
    fig, ax = plt.subplots(figsize=(fig_size, fig_size))
    venn = venn2(subsets=(metal_only, pesticide_only, both),
                 set_labels=("Metal Contaminants", "Pesticide Residue"))
    for text in venn.set_labels:
        text.set_fontsize(font_size)
    for text in venn.subset_labels:
        if text:
            text.set_fontsize(font_size)
    st.pyplot(fig)

    # --- Summary Table ---
    st.subheader("📊 No. of Unsafe Samples Summary")

    summary_list = []

    # Overall summary
    overall_metal = len(df[(df[col_metal]) & (~df[col_pesticide])])
    overall_pest = len(df[(df[col_pesticide]) & (~df[col_metal])])
    overall_both = len(df[(df[col_metal]) & (df[col_pesticide])])
    summary_list.append(["Overall", overall_metal, overall_pest, overall_both])

    # Commodity-wise
    for com in sorted(df[col_commodity].dropna().unique()):
        d = df[df[col_commodity] == com]
        m_only = len(d[(d[col_metal]) & (~d[col_pesticide])])
        p_only = len(d[(d[col_pesticide]) & (~d[col_metal])])
        both_unsafe = len(d[(d[col_metal]) & (d[col_pesticide])])
        summary_list.append([com, m_only, p_only, both_unsafe])

    summary_df = pd.DataFrame(summary_list, columns=[
        "Commodity", "Metal Contaminants", "Pesticide Residue", "Both"
    ])

    st.dataframe(summary_df, use_container_width=True)

    # --- Download Excel ---
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        summary_df.to_excel(writer, index=False, sheet_name="Unsafe Summary")
    buffer.seek(0)
    st.download_button(
        label="📥 Download Summary (Excel)",
        data=buffer,
        file_name="Unsafe_Samples_Summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # --- Download CSV ---
    csv_data = summary_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Summary (CSV)",
        data=csv_data,
        file_name="Unsafe_Samples_Summary.csv",
        mime="text/csv"
    )

else:
    st.info("👆 Please upload your Key Parameter dataset to begin.")
