import streamlit as st
import pandas as pd
from matplotlib_venn import venn2
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Fruits & Vegetables Venn Diagram", layout="wide")

st.title("🍎 Fruits & Vegetables — Unsafe Sample Summary & Venn Diagram")

uploaded_file = st.file_uploader("📤 Upload your Monitoring CSV file", type=["csv", "xlsx"])

if uploaded_file:
    # Read file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("✅ File uploaded successfully!")

    # --- Identify key columns ---
    # You can adjust these column names if your dataset differs
    col_commodity = "Commodity"
    col_metal = "Metal Contaminants Unsafe"
    col_pesticide = "Pesticide Residue Unsafe"

    # Ensure boolean-type unsafe indicators
    df[col_metal] = df[col_metal].astype(bool)
    df[col_pesticide] = df[col_pesticide].astype(bool)

    # Sidebar controls
    commodities = ["Overall"] + sorted(df[col_commodity].unique())
    selected_commodity = st.sidebar.selectbox("Select Commodity", commodities)
    st.sidebar.markdown("---")
    font_size = st.sidebar.slider("Font Size", 8, 24, 14)
    fig_size = st.sidebar.slider("Figure Size", 3, 10, 5)

    # Filter data if specific commodity selected
    if selected_commodity != "Overall":
        data = df[df[col_commodity] == selected_commodity]
    else:
        data = df

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

    # --- Summary Table (Overall + Commodity-wise) ---
    st.subheader("📊 No. of Unsafe Samples Summary")

    summary_list = []
    # Overall summary
    overall_metal = len(df[(df[col_metal]) & (~df[col_pesticide])])
    overall_pest = len(df[(df[col_pesticide]) & (~df[col_metal])])
    overall_both = len(df[(df[col_metal]) & (df[col_pesticide])])
    summary_list.append(["Overall", overall_metal, overall_pest, overall_both])

    # Commodity-wise summary
    for com in sorted(df[col_commodity].unique()):
        d = df[df[col_commodity] == com]
        m_only = len(d[(d[col_metal]) & (~d[col_pesticide])])
        p_only = len(d[(d[col_pesticide]) & (~d[col_metal])])
        both_unsafe = len(d[(d[col_metal]) & (d[col_pesticide])])
        summary_list.append([com, m_only, p_only, both_unsafe])

    summary_df = pd.DataFrame(summary_list, columns=[
        "Commodity", "Metal Contaminants", "Pesticide Residue", "Both"
    ])

    st.dataframe(summary_df, use_container_width=True)

    # --- Download as Excel ---
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

    # --- Download as CSV ---
    csv_data = summary_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Summary (CSV)",
        data=csv_data,
        file_name="Unsafe_Samples_Summary.csv",
        mime="text/csv"
    )

else:
    st.info("👆 Please upload your monitoring dataset to begin.")








































# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt
# from matplotlib_venn import venn2_unweighted
# from io import BytesIO

# # --- Streamlit Page Config ---
# st.set_page_config(page_title="F&V Venn Diagram", layout="wide")
# st.title("🍎 Fruits & Vegetables — Test Category Venn Diagram")

# # --- File Upload ---
# uploaded_file = st.file_uploader("📤 Upload CSV or Excel File", type=["csv", "xlsx"])

# if uploaded_file:
#     # --- Read file dynamically ---
#     if uploaded_file.name.endswith(".csv"):
#         df = pd.read_csv(uploaded_file)
#     else:
#         df = pd.read_excel(uploaded_file)

#     st.success(f"✅ File loaded successfully with {len(df)} rows.")

#     # --- Basic column checks ---
#     required_cols = {"Order ID", "Commodity", "Parameter Name", "Parameter Result", "Parameter Limit", "Test Category"}
#     if not required_cols.issubset(df.columns):
#         st.error(f"❌ Missing required columns. Found: {list(df.columns)}")
#         st.stop()

#     # --- Normalize text ---
#     df["Test Category"] = df["Test Category"].str.strip().str.title()
#     df["Commodity"] = df["Commodity"].str.strip()

#     # --- Sidebar Controls ---
#     st.sidebar.header("🎛 Customize View")
#     show_all = st.sidebar.checkbox("Show All Commodities", value=False)
#     commodities = sorted(df["Commodity"].dropna().unique())
#     selected_commodity = st.sidebar.selectbox("Select Commodity", ["Overall"] + commodities)
#     fig_width = st.sidebar.slider("Figure Width", 3, 10, 6)
#     fig_height = st.sidebar.slider("Figure Height", 3, 10, 6)
#     label_font = st.sidebar.slider("Label Font Size", 8, 24, 14)
#     value_font = st.sidebar.slider("Value Font Size", 8, 24, 12)

#     # --- Helper: Plot Function ---
#     def plot_venn(data, title):
#         # Sets of order IDs by category
#         pesticide_orders = set(data.loc[data["Test Category"] == "Pesticide Residue", "Order ID"])
#         metal_orders = set(data.loc[data["Test Category"] == "Metal Contaminants", "Order ID"])

#         # Create Venn diagram
#         fig, ax = plt.subplots(figsize=(fig_width, fig_height))
#         v = venn2_unweighted([pesticide_orders, metal_orders],
#                              set_labels=("Pesticide Residue", "Metal Contaminants"))

#         # Font styling
#         if v.set_labels:
#             for lbl in v.set_labels:
#                 if lbl:
#                     lbl.set_fontsize(label_font)
#         if v.subset_labels:
#             for lbl in v.subset_labels:
#                 if lbl:
#                     lbl.set_fontsize(value_font)

#         # 🆕 Updated title text
#         display_title = "Non-Compliant Samples" if title == "Overall" else f"Non-Compliant Samples — {title}"
#         plt.title(display_title, fontsize=label_font + 2)
#         plt.tight_layout()
#         return fig

#     # --- Main Display Logic ---
#     if show_all:
#         st.subheader("📊 Commodity-wise Venn Diagrams")
#         all_coms = ["Overall"] + commodities
#         for com in all_coms:
#             st.markdown(f"### 🥦 {com}")
#             subset = df if com == "Overall" else df[df["Commodity"] == com]
#             fig = plot_venn(subset, com)
#             st.pyplot(fig)
#     else:
#         st.subheader(f"📈 Venn Diagram: {selected_commodity}")
#         subset = df if selected_commodity == "Overall" else df[df["Commodity"] == selected_commodity]
#         fig = plot_venn(subset, selected_commodity)
#         st.pyplot(fig)

#         # --- Download as PNG ---
#         buffer = BytesIO()
#         fig.savefig(buffer, format="png", dpi=300, bbox_inches="tight")
#         st.download_button(
#             label="📥 Download Venn as PNG",
#             data=buffer.getvalue(),
#             file_name=f"{selected_commodity}_Venn.png",
#             mime="image/png"
#         )

# else:
#     st.info("👆 Please upload your Fruits & Vegetables monitoring data file to begin.")
