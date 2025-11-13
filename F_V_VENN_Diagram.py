import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib_venn import venn2_unweighted
from io import BytesIO
# --- Streamlit Page Config ---
st.set_page_config(page_title="F&V Venn Diagram", layout="wide")
st.title("🍎 Fruits & Vegetables — Test Category Venn Diagram")

# --- File Upload ---
uploaded_file = st.file_uploader("📤 Upload CSV or Excel File", type=["csv", "xlsx"])

if uploaded_file:
    # --- Read file dynamically ---
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success(f"✅ File loaded successfully with {len(df)} rows.")

    # --- Basic column checks ---
    required_cols = {"Order ID", "Commodity", "Parameter Name", "Parameter Result", "Parameter Limit", "Test Category"}
    if not required_cols.issubset(df.columns):
        st.error(f"❌ Missing required columns. Found: {list(df.columns)}")
        st.stop()

    # --- Normalize text ---
    df["Test Category"] = df["Test Category"].str.strip().str.title()
    df["Commodity"] = df["Commodity"].str.strip()

    # --- Sidebar Controls ---
    st.sidebar.header("🎛 Customize View")
    show_all = st.sidebar.checkbox("Show All Commodities", value=False)
    commodities = sorted(df["Commodity"].dropna().unique())
    selected_commodity = st.sidebar.selectbox("Select Commodity", ["Overall"] + commodities)
    fig_width = st.sidebar.slider("Figure Width", 3, 10, 6)
    fig_height = st.sidebar.slider("Figure Height", 3, 10, 6)
    label_font = st.sidebar.slider("Label Font Size", 8, 24, 14)
    value_font = st.sidebar.slider("Value Font Size", 8, 24, 12)

    # --- Helper: Plot Function ---
    def plot_venn(data, title):
        # Sets of order IDs by category
        pesticide_orders = set(data.loc[data["Test Category"] == "Pesticide Residue", "Order ID"])
        metal_orders = set(data.loc[data["Test Category"] == "Metal Contaminants", "Order ID"])

        # Create Venn diagram
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        v = venn2_unweighted([pesticide_orders, metal_orders],
                             set_labels=("Pesticide Residue", "Metal Contaminants"))

        # Font styling
        if v.set_labels:
            for lbl in v.set_labels:
                if lbl:
                    lbl.set_fontsize(label_font)
        if v.subset_labels:
            for lbl in v.subset_labels:
                if lbl:
                    lbl.set_fontsize(value_font)

        plt.title(title, fontsize=label_font + 2)
        plt.tight_layout()
        return fig

    # --- Main Display Logic ---
    if show_all:
        st.subheader("📊 Commodity-wise Venn Diagrams")
        all_coms = ["Non-Compliant Samples"] + commodities
        for com in all_coms:
            st.markdown(f"### 🥦 {com}")
            subset = df if com == "Non-Compliant Samples" else df[df["Commodity"] == com]
            fig = plot_venn(subset, com)
            st.pyplot(fig)
    else:
        st.subheader(f"📈 Venn Diagram: {selected_commodity}")
        subset = df if selected_commodity == "Non-Compliant Samples" else df[df["Commodity"] == selected_commodity]
        fig = plot_venn(subset, selected_commodity)
        st.pyplot(fig)

        # --- Download as PNG ---
        buffer = BytesIO()
        fig.savefig(buffer, format="png", dpi=300, bbox_inches="tight")
        st.download_button(
            label="📥 Download Venn as PNG",
            data=buffer.getvalue(),
            file_name=f"{selected_commodity}_Venn.png",
            mime="image/png"
        )

else:
    st.info("👆 Please upload your Fruits & Vegetables monitoring data file to begin.")
