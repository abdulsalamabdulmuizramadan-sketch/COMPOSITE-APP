import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Composite Calculator & Report Generator", page_icon="🧪", layout="wide")

st.title("🧪 Eco-Friendly Composite Calculator & Methodology Report Generator")
st.caption("Calculate Rule-of-Mixtures batching, evaluate voids, compare formulations, and export printable methodology reports.")

# 2. Preset Formulations Data
PRESETS = {
    "F0 (Neat Epoxy - Control)": {"matrix": 100.0, "reinf": 0.0},
    "F1 (15 wt.% Reinforcement)": {"matrix": 85.0, "reinf": 15.0},
    "F2 (20 wt.% Reinforcement)": {"matrix": 80.0, "reinf": 20.0},
    "F3 (25 wt.% Reinforcement)": {"matrix": 75.0, "reinf": 25.0},
    "F4 (30 wt.% Reinforcement)": {"matrix": 70.0, "reinf": 30.0},
    "Custom Formulation": {"matrix": 80.0, "reinf": 20.0}
}

# Sidebar Controls
st.sidebar.header("⚙️ Formulation & Mold Controls")
selected_preset = st.sidebar.selectbox("Load Standard Formulation Preset:", list(PRESETS.keys()))

st.sidebar.markdown("---")
st.sidebar.subheader("1. Weight Percentages")

if selected_preset == "Custom Formulation":
    reinf_wt = st.sidebar.slider("Total Reinforcement (wt. %):", min_value=0.0, max_value=50.0, value=20.0, step=1.0)
    matrix_wt = 100.0 - reinf_wt
else:
    reinf_wt = PRESETS[selected_preset]["reinf"]
    matrix_wt = PRESETS[selected_preset]["matrix"]

st.sidebar.info(f"**Matrix:** {matrix_wt:.1f} wt. % | **Reinforcement:** {reinf_wt:.1f} wt. %")

# Constituent Ratios
st.sidebar.markdown("---")
st.sidebar.subheader("2. Ratio Splits")
r_resin = st.sidebar.number_input("Resin Ratio Part", value=2.0, min_value=0.1)
r_hardener = st.sidebar.number_input("Hardener Ratio Part", value=1.0, min_value=0.1)
r_cotton = st.sidebar.number_input("Cotton Wool Ratio Part", value=2.0, min_value=0.0)
r_cowhorn = st.sidebar.number_input("Cow-horn/Hoof Ratio Part", value=2.0, min_value=0.0)
r_limestone = st.sidebar.number_input("Limestone Ratio Part", value=1.0, min_value=0.0)

sum_m = r_resin + r_hardener
sum_r = r_cotton + r_cowhorn + r_limestone if reinf_wt > 0 else 1.0

wt_resin = matrix_wt * (r_resin / sum_m)
wt_hardener = matrix_wt * (r_hardener / sum_m)

if reinf_wt > 0:
    wt_cotton = reinf_wt * (r_cotton / sum_r)
    wt_cowhorn = reinf_wt * (r_cowhorn / sum_r)
    wt_limestone = reinf_wt * (r_limestone / sum_r)
else:
    wt_cotton = wt_cowhorn = wt_limestone = 0.0

# Mold Volume Selection
st.sidebar.markdown("---")
st.sidebar.subheader("3. Mold Geometry & Volume")
mold_option = st.sidebar.selectbox(
    "Select Specimen / Mold Standard:",
    ["Base Batch Volume (108.0 cm³)", 
     "Compressive Mold (28.8 cm³)", 
     "Density Mold (39.2 cm³)", 
     "Flexural Mold (25.92 cm³)", 
     "Impact Mold (14.0 cm³)", 
     "Custom Mold Dimensions"]
)

if "108.0" in mold_option:
    base_volume = 108.0
elif "Compressive" in mold_option:
    base_volume = 28.8
elif "Density" in mold_option:
    base_volume = 39.2
elif "Flexural" in mold_option:
    base_volume = 25.92
elif "Impact" in mold_option:
    base_volume = 14.0
else:
    l = st.sidebar.number_input("Length (cm)", value=10.0)
    w = st.sidebar.number_input("Width (cm)", value=10.0)
    t = st.sidebar.number_input("Thickness (cm)", value=0.8)
    base_volume = l * w * t

num_replicates = st.sidebar.number_input("Number of Replicates", min_value=1, value=1, step=1)
spill_margin = st.sidebar.slider("Resin Spill / Waste Margin (%)", min_value=0, max_value=20, value=0, step=5)

v_total = base_volume * num_replicates * (1.0 + (spill_margin / 100.0))

# Main Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Active Batch & Void Estimator", 
    "📈 Formulations Comparison (F0–F4)", 
    "🖨️ Printable Methodology Report", 
    "📄 Methodology Equations"
])

# ==========================================
# TAB 1: ACTIVE BATCH & VOID CALCULATOR
# ==========================================
with tab1:
    DEFAULT_CONSTITUENTS = [
        {"name": "Epoxy Resin (LY 556)", "wt": wt_resin, "rho": 1.2086, "comp": 95.0, "flex": 62.5},
        {"name": "Hardener (HY 951)", "wt": wt_hardener, "rho": 1.0731, "comp": 95.0, "flex": 62.5},
        {"name": "Cow-Horn/Cow-Hoof Powder", "wt": wt_cowhorn, "rho": 0.6478, "comp": 1018.96, "flex": 981.40},
        {"name": "Cotton Wool Fiber", "wt": wt_cotton, "rho": 0.0200, "comp": 52.80, "flex": 52.80},
        {"name": "Limestone Powder", "wt": wt_limestone, "rho": 1.4800, "comp": 135.00, "flex": 0.0}
    ]

    st.markdown("### 📝 Constituent Properties & Composition Editor")
    df_input = pd.DataFrame(DEFAULT_CONSTITUENTS)

    edited_df = st.data_editor(
        df_input,
        num_rows="fixed",
        use_container_width=True,
        column_config={
            "wt": st.column_config.NumberColumn("Weight (%)", format="%.3f"),
            "rho": st.column_config.NumberColumn("Density (g/cm³)", format="%.4f"),
            "comp": st.column_config.NumberColumn("Compressive Strength (MPa)", format="%.2f"),
            "flex": st.column_config.NumberColumn("Flexural Strength (MPa)", format="%.2f"),
        }
    )

    # ROM Calculations
    edited_df["Weight / Density"] = edited_df["wt"] / edited_df["rho"]
    total_w_over_rho = edited_df["Weight / Density"].sum()

    rho_theoretical = 100.0 / total_w_over_rho if total_w_over_rho > 0 else 0.0
    edited_df["Volume (%)"] = (edited_df["Weight / Density"] / total_w_over_rho) * 100.0
    edited_df["Batch Volume (cm³)"] = (edited_df["wt"] / 100.0) * v_total
    edited_df["Batch Mass (g)"] = edited_df["rho"] * edited_df["Batch Volume (cm³)"]
    edited_df["Compressive Contrib. (MPa)"] = (edited_df["Volume (%)"] / 100.0) * edited_df["comp"]
    edited_df["Flexural Contrib. (MPa)"] = (edited_df["Volume (%)"] / 100.0) * edited_df["flex"]

    total_mass = edited_df["Batch Mass (g)"].sum()
    pred_comp = edited_df["Compressive Contrib. (MPa)"].sum()
    pred_flex = edited_df["Flexural Contrib. (MPa)"].sum()

    st.markdown("### 📊 Active Batch Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Target Mold Volume", f"{v_total:.2f} cm³")
    c2.metric("Total Batch Mass Required", f"{total_mass:.2f} g")
    c3.metric("Theoretical Density (ρₜ)", f"{rho_theoretical:.4f} g/cm³")
    c4.metric("Pred. Compressive Strength", f"{pred_comp:.2f} MPa")

    st.markdown("---")

    # Void Content Estimator
    st.markdown("### 🧪 Void Content Estimator")
    v_col1, v_col2 = st.columns([1, 1])

    with v_col1:
        calc_mode = st.radio("Density Input Method:", ["Direct Experimental Density (ρₑ)", "Archimedes Method (ASTM D792)"])
        
        if calc_mode == "Direct Experimental Density (ρₑ)":
            rho_exp = st.number_input("Experimental Density, ρₑ (g/cm³):", min_value=0.1, value=1.0500, step=0.005, format="%.4f")
        else:
            w_air = st.number_input("Specimen Weight in Air, Wₐᵢᵣ (g):", min_value=0.001, value=5.000, step=0.1, format="%.3f")
            w_water = st.number_input("Specimen Weight in Water, W_water (g):", min_value=0.000, value=0.250, step=0.1, format="%.3f")
            rho_exp = (w_air / (w_air - w_water)) * 0.9975 if w_air > w_water else 0.0

    with v_col2:
        if rho_exp > 0:
            void_content = ((rho_theoretical - rho_exp) / rho_theoretical) * 100.0
            st.metric("Experimental Density (ρₑ)", f"{rho_exp:.4f} g/cm³")
            st.metric("Calculated Void Content (Vᵥ)", f"{void_content:.2f}%")
            
            if void_content < 5.0:
                st.success("✅ **Good Consolidation (< 5% Voids):** Effective hand lay-up impregnation.")
            elif void_content < 10.0:
                st.warning("⚠️ **Moderate Voids (5 - 10%):** Review compaction procedure.")
            else:
                st.error("❌ **High Void Content (> 10%):** Excess porosity present.")
        else:
            void_content = 0.0

    st.markdown("---")
    st.markdown("### ⚖️ Final Batch Recipe Table")
    final_df = edited_df[["name", "wt", "Volume (%)", "Batch Volume (cm³)", "Batch Mass (g)", "Compressive Contrib. (MPa)", "Flexural Contrib. (MPa)"]].rename(columns={"name": "Constituent", "wt": "Weight (%)"})
    st.dataframe(final_df, use_container_width=True)

    csv = final_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Batch Recipe as CSV", data=csv, file_name=f"batch_recipe_{v_total:.0f}cm3.csv", mime="text/csv")

# ==========================================
# TAB 2: FORMULATIONS COMPARISON (F0–F4)
# ==========================================
with tab2:
    st.markdown("### 📈 Multi-Formulation ROM Comparison (F0–F4)")
    st.caption("Comparative analysis across control (F0) and hybrid formulations (F1–F4) based on 108 cm³ base volume.")

    f_names = ["F0 (Control)", "F1 (15%)", "F2 (20%)", "F3 (25%)", "F4 (30%)"]
    f_matrix_wts = [100.0, 85.0, 80.0, 75.0, 70.0]
    f_reinf_wts = [0.0, 15.0, 20.0, 25.0, 30.0]

    comp_list = []
    
    for i in range(5):
        m_wt = f_matrix_wts[i]
        r_wt = f_reinf_wts[i]
        
        w_res = m_wt * (2/3)
        w_hard = m_wt * (1/3)
        w_cot = r_wt * (2/5) if r_wt > 0 else 0
        w_horn = r_wt * (2/5) if r_wt > 0 else 0
        w_lime = r_wt * (1/5) if r_wt > 0 else 0

        wd_sum = (w_res / 1.2086) + (w_hard / 1.0731) + (w_horn / 0.6478) + (w_cot / 0.0200) + (w_lime / 1.4800)
        rho_t = 100.0 / wd_sum
        
        v_res = (w_res / 1.2086) / wd_sum
        v_hard = (w_hard / 1.0731) / wd_sum
        v_horn = (w_horn / 0.6478) / wd_sum
        v_cot = (w_cot / 0.0200) / wd_sum
        v_lime = (w_lime / 1.4800) / wd_sum

        comp_str = (v_res * 95.0) + (v_hard * 95.0) + (v_horn * 1018.96) + (v_cot * 52.80) + (v_lime * 135.0)
        flex_str = (v_res * 62.5) + (v_hard * 62.5) + (v_horn * 981.40) + (v_cot * 52.80) + (v_lime * 0.0)

        comp_list.append({
            "Formulation": f_names[i],
            "Reinforcement (wt. %)": r_wt,
            "Theoretical Density (g/cm³)": round(rho_t, 4),
            "Compressive Strength (MPa)": round(comp_str, 2),
            "Flexural Strength (MPa)": round(flex_str, 2)
        })

    df_comp = pd.DataFrame(comp_list)
    st.dataframe(df_comp, use_container_width=True)

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown("**Predicted Compressive Strength (MPa)**")
        st.bar_chart(df_comp.set_index("Formulation")["Compressive Strength (MPa)"])

    with chart_col2:
        st.markdown("**Predicted Flexural Strength (MPa)**")
        st.bar_chart(df_comp.set_index("Formulation")["Flexural Strength (MPa)"])

# ==========================================
# TAB 3: PRINTABLE METHODOLOGY REPORT
# ==========================================
with tab3:
    st.markdown("### 🖨️ Methodology Experimental Summary Report")
    st.caption("Click **Print / Save as PDF** below or press `Ctrl+P` (`Cmd+P`) to export this document directly for your methodology chapter.")

    # Generate HTML Table Rows dynamically
    table_rows_html = ""
    for idx, row in edited_df.iterrows():
        table_rows_html += f"""
        <tr>
            <td style="border: 1px solid #ddd; padding: 8px;">{row['name']}</td>
            <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{row['wt']:.2f}%</td>
            <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{row['rho']:.4f}</td>
            <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{row['Volume (%)']:.2f}%</td>
            <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{row['Batch Mass (g)']:.2f}</td>
        </tr>
        """

    # Complete Clean HTML Document Template
    report_html = f"""
    <div id="print-area" style="font-family: Arial, sans-serif; color: #111; line-height: 1.5; padding: 20px; border: 1px solid #ccc; background-color: #fff; border-radius: 8px;">
        <h2 style="text-align: center; color: #1a365d; margin-bottom: 5px;">RESEARCH METHODOLOGY & EXPERIMENTAL BATCHING REPORT</h2>
        <p style="text-align: center; font-size: 14px; color: #555; margin-top: 0;">Green Hybrid Polymer Composite Formulation Methodology</p>
        <hr style="border: 0; border-top: 2px solid #1a365d; margin: 15px 0;">

        <h3>1. Formulation & Batch Parameters</h3>
        <ul>
            <li><b>Selected Formulation Preset:</b> {selected_preset}</li>
            <li><b>Matrix Contribution:</b> {matrix_wt:.1f} wt. % (Resin : Hardener ratio = {r_resin:.1f}:{r_hardener:.1f})</li>
            <li><b>Reinforcement Contribution:</b> {reinf_wt:.1f} wt. % (Cotton : Cowhorn : Limestone ratio = {r_cotton:.1f}:{r_cowhorn:.1f}:{r_limestone:.1f})</li>
            <li><b>Mold Standard / Volume:</b> {mold_option} ({base_volume:.2f} cm³)</li>
            <li><b>Replicates & Spill Margin:</b> {num_replicates} sample(s) with {spill_margin}% waste margin</li>
            <li><b>Total Target Slurry Volume (V_total):</b> {v_total:.2f} cm³</li>
        </ul>

        <h3>2. Constituent Batch Quantities & Volumetric Shares</h3>
        <table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 10px;">
            <thead>
                <tr style="background-color: #f2f2f2; text-align: left;">
                    <th style="border: 1px solid #ddd; padding: 8px;">Constituent Material</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Weight (%)</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Density (g/cm³)</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Volume (%)</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Batch Mass (g)</th>
                </tr>
            </thead>
            <tbody>
                {table_rows_html}
            </tbody>
            <tfoot>
                <tr style="font-weight: bold; background-color: #f9f9f9;">
                    <td style="border: 1px solid #ddd; padding: 8px;">TOTAL</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">100.00%</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">—</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">100.00%</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{total_mass:.2f} g</td>
                </tr>
            </tfoot>
        </table>

        <h3>3. Theoretical & Analytical Performance Predictions</h3>
        <ul>
            <li><b>Theoretical Density (ρₜ):</b> {rho_theoretical:.4f} g/cm³</li>
            <li><b>Predicted Compressive Strength (Voigt ROM):</b> {pred_comp:.2f} MPa</li>
            <li><b>Predicted Flexural Strength (Voigt ROM):</b> {pred_flex:.2f} MPa</li>
        </ul>

        <h3>4. Physical Densification & Void Analysis</h3>
        <ul>
            <li><b>Measured Experimental Density (ρₑ):</b> {rho_exp:.4f} g/cm³</li>
            <li><b>Calculated Void Content (Vᵥ):</b> {void_content:.2f}%</li>
        </ul>

        <div style="margin-top: 30px; font-size: 11px; color: #777; text-align: right; border-top: 1px solid #eee; padding-top: 5px;">
            Generated using Composite Batching Calculator | Chapter 3 Experimental Methodology Format
        </div>
    </div>
    """

    st.components.v1.html(
        f"""
        <button onclick="window.print()" style="background-color: #1a365d; color: white; border: none; padding: 10px 20px; font-size: 14px; border-radius: 5px; cursor: pointer; margin-bottom: 15px;">🖨️ Print / Save as PDF</button>
        {report_html}
        """,
        height=800,
        scrolling=True
    )

# ==========================================
# TAB 4: METHODOLOGY EQUATIONS
# ==========================================
with tab4:
    st.markdown("### 📖 Methodology Equations Summary")
    st.latex(r"\frac{1}{\rho_t} = \left(\frac{W_m}{\rho_m}\right) + \left(\frac{W_f}{\rho_f}\right) + \sum \left(\frac{W_{pi}}{\rho_{pi}}\right)")
    st.latex(r"M_i = \rho_i \times V_i")
    st.latex(r"V_v = \left[\frac{\rho_t - \rho_e}{\rho_t}\right] \times 100")
