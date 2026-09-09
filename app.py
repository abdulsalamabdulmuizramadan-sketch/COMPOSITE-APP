import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Composite Calculator", page_icon="🧪", layout="wide")

st.title("🧪 Eco-Friendly Epoxy Hybrid Composite Calculator")
st.caption("Calculate density, volume fractions, and mechanical strengths based on the Rule of Mixtures.")

# 2. Preset Samples Data (Samples A to D)
PRESETS = {
    "Sample A (15 wt.% Reinforcement)": [56.667, 28.333, 6.000, 6.000, 3.000],
    "Sample B (20 wt.% Reinforcement)": [53.333, 26.667, 8.000, 8.000, 4.000],
    "Sample C (25 wt.% Reinforcement)": [50.000, 25.000, 10.000, 10.000, 5.000],
    "Sample D (30 wt.% Reinforcement)": [46.667, 23.333, 12.000, 12.000, 6.000],
    "Custom Formulation": [53.333, 26.667, 8.000, 8.000, 4.000]
}

# 3. Default Material Properties
DEFAULT_CONSTITUENTS = [
    {"name": "Resin", "density": 1.05, "comp_strength": 95.00, "flex_strength": 62.50},
    {"name": "Hardener", "density": 0.95, "comp_strength": 95.00, "flex_strength": 62.50},
    {"name": "Cowhorn / Cowhoof", "density": 1.34, "comp_strength": 1018.96, "flex_strength": 981.40},
    {"name": "Cotton Wool", "density": 1.52, "comp_strength": 52.80, "flex_strength": 52.80},
    {"name": "Limestone", "density": 2.71, "comp_strength": 135.00, "flex_strength": 0.00}
]

# 4. User Dropdown Menu
selected_preset = st.selectbox("Select Sample Preset:", list(PRESETS.keys()))
default_weights = PRESETS[selected_preset]

st.markdown("### 📝 Constituent Input Table")
st.caption("You can click directly inside any cell below to change numbers.")

# Build Input Data Table
input_data = []
for i, item in enumerate(DEFAULT_CONSTITUENTS):
    input_data.append({
        "Constituent": item["name"],
        "Weight (%)": default_weights[i],
        "Density (g/cm³)": item["density"],
        "Compressive Strength (MPa)": item["comp_strength"],
        "Flexural Strength (MPa)": item["flex_strength"]
    })

df_input = pd.DataFrame(input_data)

# Interactive Table Editor
edited_df = st.data_editor(
    df_input,
    num_rows="fixed",
    use_container_width=True
)

# 5. Rule-of-Mixtures Math Calculations
edited_df["Weight / Density"] = edited_df["Weight (%)"] / edited_df["Density (g/cm³)"]
total_w_d = edited_df["Weight / Density"].sum()

edited_df["Volume (%)"] = (edited_df["Weight / Density"] / total_w_d) * 100
edited_df["Compressive Contribution (MPa)"] = (edited_df["Volume (%)"] / 100) * edited_df["Compressive Strength (MPa)"]
edited_df["Flexural Contribution (MPa)"] = (edited_df["Volume (%)"] / 100) * edited_df["Flexural Strength (MPa)"]

# Summary Metrics
total_weight = edited_df["Weight (%)"].sum()
pred_compressive = edited_df["Compressive Contribution (MPa)"].sum()
pred_flexural = edited_df["Flexural Contribution (MPa)"].sum()
composite_density = 100 / total_w_d

# 6. Display Summary Cards
st.markdown("### 📊 Calculated Composite Results")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Weight", f"{total_weight:.2f}%")
col2.metric("Composite Density", f"{composite_density:.4f} g/cm³")
col3.metric("Predicted Compressive Strength", f"{pred_compressive:.2f} MPa")
col4.metric("Predicted Flexural Strength", f"{pred_flexural:.2f} MPa")

# Display Full Results Table
final_df = edited_df[[
    "Constituent", "Weight (%)", "Density (g/cm³)", "Weight / Density", 
    "Volume (%)", "Compressive Contribution (MPa)", "Flexural Contribution (MPa)"
]]

st.dataframe(final_df, use_container_width=True)

# 7. Export Data to CSV Button
csv = final_df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="📥 Download Results as CSV (Excel)",
    data=csv,
    file_name=f"{selected_preset.replace(' ', '_')}_results.csv",
    mime="text/csv"
)
