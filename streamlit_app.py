import streamlit as st
import requests
import json
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd

# BE_URL = "http://0.0.0.0:80/"
BE_URL = "https://p2x-container-app.wonderfulpebble-6684d847.westeurope.azurecontainerapps.io/"

# Set page title and description
st.set_page_config(page_title="Energy Optimization", layout="wide")
st.title("Energy Optimization Tools")

# Create a selector for the calculator type
calculator_type = st.radio("Select Calculator", ["BEKS", "P2H", "P2G", "DSR"], horizontal=True)

if calculator_type == "BEKS":
    st.header("BEKS Demo")
    st.write("Fill in the form below to submit a request to the BEKS API.")

    # Create form for input parameters
    with st.form("beks_input_form"):
        st.header("Input Parameters")

        # Create columns for a more compact layout
        col1, col2 = st.columns(2)

        with col1:
            # Provider with horizontal radio buttons
            provider = st.radio("Provider", ["ESO", "Litgrid"], index=0, horizontal=True)

            # Sector with horizontal radio buttons
            sector = st.radio("Sector", ["Paslaugų", "Energetikos", "Pramonės", "Telkėjas", "Kita"], index=0,
                              horizontal=True)

            rte = st.number_input("RTE (%)", min_value=0.0, max_value=100.0, value=88.0, step=1.0)
            q_max = st.number_input("Q_max (MWh)", min_value=0.0, value=1.0, step=0.1)
            q_total = st.number_input("Q_total (MWh)", min_value=0.0, value=2.0, step=0.1)
            soc_min = st.number_input("SOC_min (%)", min_value=0.0, max_value=100.0, value=10.0, step=1.0)
            soc_max = st.number_input("SOC_max (%)", min_value=0.0, max_value=100.0, value=95.0, step=1.0)
            n_cycles_da = st.number_input("N_cycles_DA (kartai/d.)", min_value=0, value=1, step=1)
            n_cycles_id = st.number_input("N_cycles_ID (kartai/d.)", min_value=0, value=4, step=1)

            # Reaction time slider with fixed values
            reaction_time_labels = {
                30: "<=30s",
                300: "<=300s",
                750: "<=750s",
                1000: ">750s"
            }

            reaction_time = st.select_slider(
                "reaction_time (s)",
                options=[30, 300, 750, 1000],
                value=300,
                format_func=lambda x: reaction_time_labels[x]
            )

        with col2:
            capex_p = st.number_input("CAPEX_P (tūkst. EUR/MW)", min_value=0.0, value=1000.0, step=10.0)
            capex_c = st.number_input("CAPEX_C (tūkst. Eur/MWh)", min_value=0.0, value=500.0, step=10.0)
            opex_p = st.number_input("OPEX_P (tūkst. Eur/MW/m)", min_value=0.0, value=2.52, step=0.1)
            opex_c = st.number_input("OPEX_C (tūkst. Eur/MWh)", min_value=0.0, value=0.5125, step=0.1)
            discount_rate = st.number_input("discount_rate (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1)
            number_of_years = st.number_input("number_of_years", min_value=1, value=10, step=1)

        # Fix: Corrected the subheader text and layout
        st.subheader("Minimali siūloma kaina už balansavimo pajėgumus:")
        col3, col4, col5, col6, col7 = st.columns(5)

        with col3:
            p_fcr_cap_bsp = st.number_input("FCR", min_value=0.0, value=0.0, step=1.0, key="fcr_cap")
        with col4:
            p_affru_cap_bsp = st.number_input("aFRRu", min_value=0.0, value=0.0, step=1.0, key="afrru_cap")
        with col5:
            p_affrd_cap_bsp = st.number_input("aFRRd", min_value=0.0, value=0.0, step=1.0, key="afrrd_cap")
        with col6:
            p_mffru_cap_bsp = st.number_input("mFRRu", min_value=0.0, value=0.0, step=1.0, key="mfrru_cap")
        with col7:
            p_mffrd_cap_bsp = st.number_input("mFRRd", min_value=0.0, value=0.0, step=1.0, key="mfrrd_cap")

        # Fix: Corrected the subheader text and layout
        st.subheader("Minimali siūloma kaina už balansavimo energiją:")
        col8, col9, col10, col11 = st.columns(4)

        with col8:
            p_affru_bsp = st.number_input("aFRRu", min_value=0.0, value=0.0, step=1.0, key="afrru_energy")
        with col9:
            p_affrd_bsp = st.number_input("aFRRd", min_value=0.0, value=0.0, step=1.0, key="afrrd_energy")
        with col10:
            p_mffru_bsp = st.number_input("mFRRu", min_value=0.0, value=0.0, step=1.0, key="mfrru_energy")
        with col11:
            p_mffrd_bsp = st.number_input("mFRRd", min_value=0.0, value=0.0, step=1.0, key="mfrrd_energy")

        # Submit button
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        # Create the request body
        request_body = {
            "provider": provider,
            "RTE": rte,
            "Q_max": q_max,
            "Q_total": q_total,
            "SOC_min": soc_min,
            "SOC_max": soc_max,
            "N_cycles_DA": n_cycles_da,
            "N_cycles_ID": n_cycles_id,
            "reaction_time": reaction_time,
            "CAPEX_P": capex_p,
            "CAPEX_C": capex_c,
            "OPEX_P": opex_p,
            "OPEX_C": opex_c,
            "discount_rate": discount_rate,
            "number_of_years": number_of_years,
            "P_FCR_CAP_BSP": p_fcr_cap_bsp,
            "P_aFRRu_CAP_BSP": p_affru_cap_bsp,
            "P_aFRRd_CAP_BSP": p_affrd_cap_bsp,
            "P_mFRRu_CAP_BSP": p_mffru_cap_bsp,
            "P_mFRRd_CAP_BSP": p_mffrd_cap_bsp,
            "P_aFRRu_BSP": p_affru_bsp,
            "P_aFRRd_BSP": p_affrd_bsp,
            "P_mFRRu_BSP": p_mffru_bsp,
            "P_mFRRd_BSP": p_mffrd_bsp,
            "Sector": sector
        }

        # Display the request body
        with st.expander("Request Body"):
            st.json(request_body)

        # Make the POST request
        with st.spinner("Processing request..."):
            try:
                response = requests.post(f"{BE_URL}beks", json=request_body)

                # Check if the request was successful
                if response.status_code == 200:
                    # Parse the response
                    data = response.json()

                    # Display success message
                    st.success("Request successful!")

                    # Add download button for the JSON response
                    st.download_button(
                        label="Download JSON",
                        data=json.dumps(data, indent=2),
                        file_name="response.json",
                        mime="application/json"
                    )

                    # VISUALIZATION SECTION
                    st.header("Visualization")

                    # Create tabs for different visualizations
                    tab1, tab2, tab3 = st.tabs(["Summary", "Market Details", "Economic Results"])

                    with tab1:
                        st.subheader("SUMMARY")

                        # YEARLY SUMMARY TABLE
                        st.write("##### YEARLY SUMMARY")
                        yearly_summary_table = data['aggregated']['summary']['yearly_summary_table']
                        st.table(yearly_summary_table)

                        # PROJECT LIFETIME SUMMARY TABLE
                        st.write("##### PROJECT (LIFETIME) SUMMARY")
                        project_summary_table = data['aggregated']['summary']['project_summary_table']
                        st.table(project_summary_table)

                        st.write("##### SUPPLEMENTED WITH GRAPHS")

                        col1, col2 = st.columns(2)

                        with col1:
                            # NET PRESENT VALUE ANALYSIS CHART
                            npv_data = data['aggregated']['summary']['npv_chart_data']

                            # Create a figure with secondary y-axis
                            fig_npv = make_subplots(
                                specs=[[{"secondary_y": True}]]
                            )

                            # Add bar chart for discounted cash flows
                            fig_npv.add_trace(
                                go.Bar(
                                    x=npv_data['years'],
                                    y=npv_data['dcfs'],
                                    name="Discounted Cash Flow",
                                    marker_color="lightblue",
                                    opacity=0.7
                                ),
                                secondary_y=False,
                            )

                            # Add line for cumulative NPV
                            fig_npv.add_trace(
                                go.Scatter(
                                    x=npv_data['years'],
                                    y=npv_data['npv'],
                                    mode="lines+markers",
                                    name="Cumulative NPV",
                                    line=dict(color="red", width=3)
                                ),
                                secondary_y=True,
                            )

                            # Highlight break-even point
                            if npv_data['break_even_point'] is not None:
                                break_even_year = npv_data['years'][npv_data['break_even_point']]
                                break_even_value = npv_data['npv'][npv_data['break_even_point']]

                                fig_npv.add_scatter(
                                    x=[break_even_year],
                                    y=[break_even_value],
                                    mode="markers",
                                    marker=dict(size=10, color="green"),
                                    name="Break-even Point",
                                    secondary_y=True
                                )

                            # Update layout
                            fig_npv.update_xaxes(title_text="Year")
                            fig_npv.update_yaxes(title_text="Discounted Cash Flow (tūkst. EUR)", secondary_y=False)
                            fig_npv.update_yaxes(title_text="Cumulative NPV (tūkst. EUR)", secondary_y=True)
                            fig_npv.update_layout(
                                title="NET PRESENT VALUE ANALYSIS",
                                hovermode='x unified'
                            )

                            st.plotly_chart(fig_npv, use_container_width=True)

                        with col2:
                            # REVENUE vs COST BY PRODUCTS CHART
                            rev_cost_data = data['aggregated']['summary']['revenue_cost_chart_data']
                            fig_rev_cost = px.bar(
                                x=rev_cost_data['products'],
                                y=rev_cost_data['values'],
                                labels={"x": "Product", "y": "Value (tūkst. EUR)"},
                                title="REVENUE vs COST BY PRODUCTS"
                            )

                            fig_rev_cost.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
                            st.plotly_chart(fig_rev_cost, use_container_width=True)

                        col3, col4 = st.columns(2)

                        with col3:
                            # UTILISATION (% TIME) BY PRODUCTS CHART
                            util_data = data['aggregated']['summary']['utilisation_chart_data']
                            fig_util = px.bar(
                                x=util_data['products'],
                                y=util_data['values'],
                                labels={"x": "Product", "y": "Utilisation (%)"},
                                title="UTILISATION (% TIME) BY PRODUCTS"
                            )

                            fig_util.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
                            st.plotly_chart(fig_util, use_container_width=True)

                    with tab2:
                        st.subheader("MARKET DETAILS")

                        # Add CSS for all market table styles - MADE MORE COMPACT
                        st.markdown("""
                        <style>
                        /* Common table styles - COMPACT VERSION */
                        .market-table {
                            width: 100%;
                            border-collapse: collapse;
                            margin-bottom: 0px;
                            font-size: 12px;
                        }
                        .market-table td {
                            padding: 3px;
                            text-align: center;
                        }
                        .market-table th {
                            padding: 3px;
                            text-align: center;
                            font-weight: bold;
                        }

                        /* Power market styles */
                        .power-table td {
                            background-color: #E0F0F5;
                        }
                        .power-header {
                            font-weight: bold;
                            background-color: #C5E0E8 !important;
                        }
                        .power-direction-header {
                            background-color: #D5E8EF !important;
                        }
                        .power-market-title {
                            background-color: #3D7890;
                            color: white;
                            padding: 5px;
                            margin: 0;
                            height: auto;
                            font-size: 14px;
                        }

                        /* Energy market styles */
                        .energy-table td {
                            background-color: #E6F5EC;
                        }
                        .energy-header {
                            font-weight: bold;
                            background-color: #D0EAD9 !important;
                        }
                        .energy-direction-header {
                            background-color: #DCF0E2 !important;
                        }
                        .energy-market-title {
                            background-color: #4D9D6A;
                            color: white;
                            padding: 5px;
                            margin: 0;
                            height: auto;
                            font-size: 14px;
                        }

                        /* Trading market styles */
                        .trading-table td {
                            background-color: #EFF5D8;
                        }
                        .trading-header {
                            font-weight: bold;
                            background-color: #E5ECC5 !important;
                        }
                        .trading-direction-header {
                            background-color: #EAEFCE !important;
                        }
                        .trading-market-title {
                            background-color: #8CB63C;
                            color: white;
                            padding: 5px;
                            margin: 0;
                            height: auto;
                            font-size: 14px;
                        }

                        /* Compact rows */
                        .row-compact {
                            margin-bottom: 0px !important;
                            padding: 0px !important;
                        }

                        /* Remove margin between hr tags */
                        hr {
                            margin: 5px 0 !important;
                        }
                        </style>
                        """, unsafe_allow_html=True)

                        # Create subtabs for each market
                        market_tabs = st.tabs([
                            "BALANSAVIMO PAJĖGUMŲ RINKA",
                            "BALANSAVIMO ENERGIJOS RINKA",
                            "ELEKTROS ENERGIJOS PREKYBA"
                        ])

                        # Tab 1: Power Balancing Market
                        with market_tabs[0]:
                            balansavimo_pajegumu_data = data['aggregated']['markets']['BALANSAVIMO_PAJEGUMU_RINKA']

                            # FCR section
                            fcr_data = balansavimo_pajegumu_data['FCR']
                            col1, col2 = st.columns([1, 5])

                            with col1:
                                st.markdown(
                                    f"""
                                    <div class="power-market-title">
                                    <h4 style="margin:0;">{fcr_data['header']}</h4>
                                    <small>{fcr_data['description']}</small>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                            with col2:
                                # Create the FCR table layout with ACTUAL VALUES
                                st.markdown(
                                    f"""
                                    <table class="market-table power-table">
                                        <tr>
                                            <th class="power-header">{fcr_data['volume_of_procured_reserves']['header']}</th>
                                        </tr>
                                        <tr>
                                            <td>{fcr_data['volume_of_procured_reserves']['value']:.2f} MW</td>
                                        </tr>
                                    </table>

                                    <table class="market-table power-table">
                                        <tr>
                                            <th class="power-header">{fcr_data['utilisation']['header']}</th>
                                        </tr>
                                        <tr>
                                            <td>{fcr_data['utilisation']['value']:.2f} %</td>
                                        </tr>
                                    </table>

                                    <table class="market-table power-table">
                                        <tr>
                                            <th class="power-header">{fcr_data['potential_revenue']['header']}</th>
                                        </tr>
                                        <tr>
                                            <td>{fcr_data['potential_revenue']['value']:.2f} EUR</td>
                                        </tr>
                                    </table>

                                    <table class="market-table power-table">
                                        <tr>
                                            <th class="power-header">{fcr_data['bids_selected']['header']}</th>
                                        </tr>
                                        <tr>
                                            <td>{fcr_data['bids_selected']['value']:.2f} %</td>
                                        </tr>
                                    </table>
                                    """,
                                    unsafe_allow_html=True
                                )

                            st.markdown("<hr>", unsafe_allow_html=True)

                            # aFRR section
                            afrr_data = balansavimo_pajegumu_data['aFRR']
                            col1, col2 = st.columns([1, 5])

                            with col1:
                                st.markdown(
                                    f"""
                                    <div class="power-market-title">
                                    <h4 style="margin:0;">{afrr_data['header']}</h4>
                                    <small>{afrr_data['description']}</small>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                            with col2:
                                st.markdown(
                                    f"""
                                    <table class="market-table power-table">
                                        <tr>
                                            <th class="power-header" colspan="2">{afrr_data['volume_of_procured_reserves']['header']}</th>
                                        </tr>
                                        <tr>
                                            <th class="power-direction-header">UPWARD</th>
                                            <th class="power-direction-header">DOWNWARD</th>
                                        </tr>
                                        <tr>
                                            <td>{afrr_data['volume_of_procured_reserves']['upward']['value']:.2f} MW</td>
                                            <td>{afrr_data['volume_of_procured_reserves']['downward']['value']:.2f} MW</td>
                                        </tr>
                                    </table>

                                    <table class="market-table power-table">
                                        <tr>
                                            <th class="power-header" colspan="2">{afrr_data['utilisation']['header']}</th>
                                        </tr>
                                        <tr>
                                            <th class="power-direction-header">UPWARD</th>
                                            <th class="power-direction-header">DOWNWARD</th>
                                        </tr>
                                        <tr>
                                            <td>{afrr_data['utilisation']['upward']['value']:.2f} %</td>
                                            <td>{afrr_data['utilisation']['downward']['value']:.2f} %</td>
                                        </tr>
                                    </table>

                                    <table class="market-table power-table">
                                        <tr>
                                            <th class="power-header" colspan="2">{afrr_data['potential_revenue']['header']}</th>
                                        </tr>
                                        <tr>
                                            <th class="power-direction-header">UPWARD</th>
                                            <th class="power-direction-header">DOWNWARD</th>
                                        </tr>
                                        <tr>
                                            <td>{afrr_data['potential_revenue']['upward']['value']:.2f} EUR</td>
                                            <td>{afrr_data['potential_revenue']['downward']['value']:.2f} EUR</td>
                                        </tr>
                                    </table>

                                    <table class="market-table power-table">
                                        <tr>
                                            <th class="power-header" colspan="2">{afrr_data['bids_selected']['header']}</th>
                                        </tr>
                                        <tr>
                                            <th class="power-direction-header">UPWARD</th>
                                            <th class="power-direction-header">DOWNWARD</th>
                                        </tr>
                                        <tr>
                                            <td>{afrr_data['bids_selected']['upward']['value']:.2f} %</td>
                                            <td>{afrr_data['bids_selected']['downward']['value']:.2f} %</td>
                                        </tr>
                                    </table>
                                    """,
                                    unsafe_allow_html=True
                                )

                            st.markdown("<hr>", unsafe_allow_html=True)

                            # mFRR section
                            mfrr_data = balansavimo_pajegumu_data['mFRR']
                            col1, col2 = st.columns([1, 5])

                            with col1:
                                st.markdown(
                                    f"""
                                    <div class="power-market-title">
                                    <h4 style="margin:0;">{mfrr_data['header']}</h4>
                                    <small>{mfrr_data['description']}</small>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                            with col2:
                                st.markdown(
                                    f"""
                                    <table class="market-table power-table">
                                        <tr>
                                            <th class="power-header" colspan="2">{mfrr_data['volume_of_procured_reserves']['header']}</th>
                                        </tr>
                                        <tr>
                                            <th class="power-direction-header">UPWARD</th>
                                            <th class="power-direction-header">DOWNWARD</th>
                                        </tr>
                                        <tr>
                                            <td>{mfrr_data['volume_of_procured_reserves']['upward']['value']:.2f} MW</td>
                                            <td>{mfrr_data['volume_of_procured_reserves']['downward']['value']:.2f} MW</td>
                                        </tr>
                                    </table>

                                    <table class="market-table power-table">
                                        <tr>
                                            <th class="power-header" colspan="2">{mfrr_data['utilisation']['header']}</th>
                                        </tr>
                                        <tr>
                                            <th class="power-direction-header">UPWARD</th>
                                            <th class="power-direction-header">DOWNWARD</th>
                                        </tr>
                                        <tr>
                                            <td>{mfrr_data['utilisation']['upward']['value']:.2f} %</td>
                                            <td>{mfrr_data['utilisation']['downward']['value']:.2f} %</td>
                                        </tr>
                                    </table>

                                    <table class="market-table power-table">
                                        <tr>
                                            <th class="power-header" colspan="2">{mfrr_data['potential_revenue']['header']}</th>
                                        </tr>
                                        <tr>
                                            <th class="power-direction-header">UPWARD</th>
                                            <th class="power-direction-header">DOWNWARD</th>
                                        </tr>
                                        <tr>
                                            <td>{mfrr_data['potential_revenue']['upward']['value']:.2f} EUR</td>
                                            <td>{mfrr_data['potential_revenue']['downward']['value']:.2f} EUR</td>
                                        </tr>
                                    </table>

                                    <table class="market-table power-table">
                                        <tr>
                                            <th class="power-header" colspan="2">{mfrr_data['bids_selected']['header']}</th>
                                        </tr>
                                        <tr>
                                            <th class="power-direction-header">UPWARD</th>
                                            <th class="power-direction-header">DOWNWARD</th>
                                        </tr>
                                        <tr>
                                            <td>{mfrr_data['bids_selected']['upward']['value']:.2f} %</td>
                                            <td>{mfrr_data['bids_selected']['downward']['value']:.2f} %</td>
                                        </tr>
                                    </table>
                                    """,
                                    unsafe_allow_html=True
                                )

                        # Tab 2: Energy Balancing Market
                        with market_tabs[1]:
                            balansavimo_energijos_data = data['aggregated']['markets']['BALANSAVIMO_ENERGIJOS_RINKA']

                            # aFRR section
                            afrr_data = balansavimo_energijos_data['aFRR']
                            col1, col2 = st.columns([1, 5])

                            with col1:
                                st.markdown(
                                    f"""
                                    <div class="energy-market-title">
                                    <h4 style="margin:0;">{afrr_data['header']}</h4>
                                    <small>{afrr_data['description']}</small>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                            with col2:
                                st.markdown(
                                    f"""
                                    <table class="market-table energy-table">
                                        <tr>
                                            <th class="energy-header" colspan="2">{afrr_data['volume_of_procured_energy']['header']}</th>
                                        </tr>
                                        <tr>
                                            <th class="energy-direction-header">UPWARD</th>
                                            <th class="energy-direction-header">DOWNWARD</th>
                                        </tr>
                                        <tr>
                                            <td>{afrr_data['volume_of_procured_energy']['upward']['value']:.2f} MWh</td>
                                            <td>{afrr_data['volume_of_procured_energy']['downward']['value']:.2f} MWh</td>
                                        </tr>
                                    </table>

                                    <table class="market-table energy-table">
                                        <tr>
                                            <th class="energy-header" colspan="2">{afrr_data['utilisation']['header']}</th>
                                        </tr>
                                        <tr>
                                            <th class="energy-direction-header">UPWARD</th>
                                            <th class="energy-direction-header">DOWNWARD</th>
                                        </tr>
                                        <tr>
                                            <td>{afrr_data['utilisation']['upward']['value']:.2f} %</td>
                                            <td>{afrr_data['utilisation']['downward']['value']:.2f} %</td>
                                        </tr>
                                    </table>

                                    <table class="market-table energy-table">
                                        <tr>
                                            <th class="energy-header" colspan="2">{afrr_data['potential_revenue']['header']}</th>
                                        </tr>
                                        <tr>
                                            <th class="energy-direction-header">UPWARD</th>
                                            <th class="energy-direction-header">DOWNWARD</th>
                                        </tr>
                                        <tr>
                                            <td>{afrr_data['potential_revenue']['upward']['value']:.2f} EUR</td>
                                            <td>{afrr_data['potential_revenue']['downward']['value']:.2f} EUR</td>
                                        </tr>
                                    </table>

                                    <table class="market-table energy-table">
                                        <tr>
                                            <th class="energy-header" colspan="2">{afrr_data['bids_selected']['header']}</th>
                                        </tr>
                                        <tr>
                                            <th class="energy-direction-header">UPWARD</th>
                                            <th class="energy-direction-header">DOWNWARD</th>
                                        </tr>
                                        <tr>
                                            <td>{afrr_data['bids_selected']['upward']['value']:.2f} %</td>
                                            <td>{afrr_data['bids_selected']['downward']['value']:.2f} %</td>
                                        </tr>
                                    </table>
                                    """,
                                    unsafe_allow_html=True
                                )

                            st.markdown("<hr>", unsafe_allow_html=True)

                            # mFRR section
                            mfrr_data = balansavimo_energijos_data['mFRR']
                            col1, col2 = st.columns([1, 5])

                            with col1:
                                st.markdown(
                                    f"""
                                    <div class="energy-market-title">
                                    <h4 style="margin:0;">{mfrr_data['header']}</h4>
                                    <small>{mfrr_data['description']}</small>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                            with col2:
                                st.markdown(
                                    f"""
                                    <table class="market-table energy-table">
                                        <tr>
                                            <th class="energy-header" colspan="2">{mfrr_data['volume_of_procured_energy']['header']}</th>
                                        </tr>
                                        <tr>
                                            <th class="energy-direction-header">UPWARD</th>
                                            <th class="energy-direction-header">DOWNWARD</th>
                                        </tr>
                                        <tr>
                                            <td>{mfrr_data['volume_of_procured_energy']['upward']['value']:.2f} MWh</td>
                                            <td>{mfrr_data['volume_of_procured_energy']['downward']['value']:.2f} MWh</td>
                                        </tr>
                                    </table>

                                    <table class="market-table energy-table">
                                        <tr>
                                            <th class="energy-header" colspan="2">{mfrr_data['utilisation']['header']}</th>
                                        </tr>
                                        <tr>
                                            <th class="energy-direction-header">UPWARD</th>
                                            <th class="energy-direction-header">DOWNWARD</th>
                                        </tr>
                                        <tr>
                                            <td>{mfrr_data['utilisation']['upward']['value']:.2f} %</td>
                                            <td>{mfrr_data['utilisation']['downward']['value']:.2f} %</td>
                                        </tr>
                                    </table>

                                    <table class="market-table energy-table">
                                        <tr>
                                            <th class="energy-header" colspan="2">{mfrr_data['potential_revenue']['header']}</th>
                                        </tr>
                                        <tr>
                                            <th class="energy-direction-header">UPWARD</th>
                                            <th class="energy-direction-header">DOWNWARD</th>
                                        </tr>
                                        <tr>
                                            <td>{mfrr_data['potential_revenue']['upward']['value']:.2f} EUR</td>
                                            <td>{mfrr_data['potential_revenue']['downward']['value']:.2f} EUR</td>
                                        </tr>
                                    </table>

                                    <table class="market-table energy-table">
                                        <tr>
                                            <th class="energy-header" colspan="2">{mfrr_data['bids_selected']['header']}</th>
                                        </tr>
                                        <tr>
                                            <th class="energy-direction-header">UPWARD</th>
                                            <th class="energy-direction-header">DOWNWARD</th>
                                        </tr>
                                        <tr>
                                            <td>{mfrr_data['bids_selected']['upward']['value']:.2f} %</td>
                                            <td>{mfrr_data['bids_selected']['downward']['value']:.2f} %</td>
                                        </tr>
                                    </table>
                                    """,
                                    unsafe_allow_html=True
                                )

                        # Tab 3: Electricity Trading
                        with market_tabs[2]:
                            elektros_energijos_data = data['aggregated']['markets']['ELEKTROS_ENERGIJOS_PREKYBA']

                            # Day Ahead section
                            if 'Day_Ahead' in elektros_energijos_data:  # Check if Day_Ahead exists
                                day_ahead_data = elektros_energijos_data['Day_Ahead']
                                col1, col2 = st.columns([1, 5])

                                with col1:
                                    st.markdown(
                                        f"""
                                        <div class="trading-market-title">
                                        <h4 style="margin:0;">{day_ahead_data['header']}</h4>
                                        <small>{day_ahead_data['description']}</small>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )

                                with col2:
                                    st.markdown(
                                        f"""
                                        <table class="market-table trading-table">
                                            <tr>
                                                <th class="trading-header" colspan="2">{day_ahead_data['volume_of_energy_exchange']['header']}</th>
                                            </tr>
                                            <tr>
                                                <th class="trading-direction-header">PURCHASE</th>
                                                <th class="trading-direction-header">SALE</th>
                                            </tr>
                                            <tr>
                                                <td>{day_ahead_data['volume_of_energy_exchange']['purchase']['value']:.2f} MWh</td>
                                                <td>{day_ahead_data['volume_of_energy_exchange']['sale']['value']:.2f} MWh</td>
                                            </tr>
                                        </table>

                                        <table class="market-table trading-table">
                                            <tr>
                                                <th class="trading-header" colspan="2">{day_ahead_data['percentage_of_time']['header']}</th>
                                            </tr>
                                            <tr>
                                                <th class="trading-direction-header">PURCHASE</th>
                                                <th class="trading-direction-header">SALE</th>
                                            </tr>
                                            <tr>
                                                <td>{day_ahead_data['percentage_of_time']['purchase']['value']:.2f} %</td>
                                                <td>{day_ahead_data['percentage_of_time']['sale']['value']:.2f} %</td>
                                            </tr>
                                        </table>

                                        <table class="market-table trading-table">
                                            <tr>
                                                <th class="trading-header" colspan="2">{day_ahead_data['potential_cost_revenue']['header']}</th>
                                            </tr>
                                            <tr>
                                                <th class="trading-direction-header">COST</th>
                                                <th class="trading-direction-header">REVENUE</th>
                                            </tr>
                                            <tr>
                                                <td>{day_ahead_data['potential_cost_revenue']['cost']['value']:.2f} EUR</td>
                                                <td>{day_ahead_data['potential_cost_revenue']['revenue']['value']:.2f} EUR</td>
                                            </tr>
                                        </table>
                                        """,
                                        unsafe_allow_html=True
                                    )
                                st.markdown("<hr>", unsafe_allow_html=True)

                            # Intraday section
                            if 'Intraday' in elektros_energijos_data:  # Check if Intraday exists
                                intraday_data = elektros_energijos_data['Intraday']
                                col1, col2 = st.columns([1, 5])

                                with col1:
                                    st.markdown(
                                        f"""
                                        <div class="trading-market-title">
                                        <h4 style="margin:0;">{intraday_data['header']}</h4>
                                        <small>{intraday_data['description']}</small>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )

                                with col2:
                                    st.markdown(
                                        f"""
                                        <table class="market-table trading-table">
                                            <tr>
                                                <th class="trading-header" colspan="2">{intraday_data['volume_of_energy_exchange']['header']}</th>
                                            </tr>
                                            <tr>
                                                <th class="trading-direction-header">PURCHASE</th>
                                                <th class="trading-direction-header">SALE</th>
                                            </tr>
                                            <tr>
                                                <td>{intraday_data['volume_of_energy_exchange']['purchase']['value']:.2f} MWh</td>
                                                <td>{intraday_data['volume_of_energy_exchange']['sale']['value']:.2f} MWh</td>
                                            </tr>
                                        </table>

                                        <table class="market-table trading-table">
                                            <tr>
                                                <th class="trading-header" colspan="2">{intraday_data['percentage_of_time']['header']}</th>
                                            </tr>
                                            <tr>
                                                <th class="trading-direction-header">PURCHASE</th>
                                                <th class="trading-direction-header">SALE</th>
                                            </tr>
                                            <tr>
                                                <td>{intraday_data['percentage_of_time']['purchase']['value']:.2f} %</td>
                                                <td>{intraday_data['percentage_of_time']['sale']['value']:.2f} %</td>
                                            </tr>
                                        </table>

                                        <table class="market-table trading-table">
                                            <tr>
                                                <th class="trading-header" colspan="2">{intraday_data['potential_cost_revenue']['header']}</th>
                                            </tr>
                                            <tr>
                                                <th class="trading-direction-header">COST</th>
                                                <th class="trading-direction-header">REVENUE</th>
                                            </tr>
                                            <tr>
                                                <td>{intraday_data['potential_cost_revenue']['cost']['value']:.2f} EUR</td>
                                                <td>{intraday_data['potential_cost_revenue']['revenue']['value']:.2f} EUR</td>
                                            </tr>
                                        </table>
                                        """,
                                        unsafe_allow_html=True
                                    )

                    with tab3:
                        st.subheader("ECONOMIC RESULTS BY PRODUCT")

                        econ_data = data['aggregated']['economic_results']

                        # Display revenues table and chart
                        st.write("##### REVENUE BY PRODUCT")
                        if econ_data['revenue_table']:  # Check if list is not empty
                            st.table(econ_data['revenue_table'])

                            # Create graph from table data
                            fig_rev = px.bar(
                                econ_data['revenue_table'],
                                x="Product",
                                y="Value (tūkst. EUR)",
                                title="REVENUE BY PRODUCT"
                            )

                            fig_rev.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
                            st.plotly_chart(fig_rev, use_container_width=True)
                        else:
                            st.info("No revenue data available")

                        # Display costs table and chart
                        st.write("##### COST BY PRODUCT")
                        if econ_data['cost_table']:  # Check if list is not empty
                            st.table(econ_data['cost_table'])

                            # Create graph from table data
                            fig_cost = px.bar(
                                econ_data['cost_table'],
                                x="Product",
                                y="Value (tūkst. EUR)",
                                title="COST BY PRODUCT"
                            )

                            fig_cost.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
                            st.plotly_chart(fig_cost, use_container_width=True)
                        else:
                            st.info("No cost data available")

                        # Display total profit
                        st.metric("TOTAL PROFIT", f"{econ_data['total_profit']:.2f} tūkst. EUR")

                        # Display yearly results table
                        st.write("##### YEARLY RESULTS")
                        st.table(econ_data['yearly_table'])

                        # Plot yearly NPV
                        fig_yearly_npv = px.line(
                            econ_data['yearly_table'],
                            x="YEAR",
                            y="NPV (tūkst. EUR)",  # Corrected key if it was NPV (tūkst. EUR)
                            markers=True,
                            title="NET PRESENT VALUE OVER TIME"
                        )

                        fig_yearly_npv.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
                        st.plotly_chart(fig_yearly_npv, use_container_width=True)
                else:
                    # Handle error response - new error handling code
                    try:
                        error_data = response.json()
                        if "detail" in error_data:
                            # Create a popup with the error message
                            st.error(f"Calculation failed: {error_data['detail']}")
                        else:
                            st.error(f"Request failed with status code: {response.status_code}")
                    except json.JSONDecodeError:
                        st.error(f"Request failed with status code: {response.status_code}")

            except requests.exceptions.RequestException as e:
                st.error(f"Error making request: {str(e)}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")

elif calculator_type == "P2H":
    st.header("P2H Demo")
    st.write("Fill in the form below to submit a request to the P2H API.")


    # Function to convert Lithuanian characters for county name
    def convert_lt_chars(text):
        replacements = {
            'ė': 'e',
            'ž': 'z',
            'š': 's'
        }

        for lt_char, ascii_char in replacements.items():
            text = text.replace(lt_char, ascii_char)

        return text.lower()


    # Create form for P2H input parameters
    with st.form("p2h_input_form"):
        st.header("Input Parameters")

        # Add Provider and Sector selection fields like in BEKS
        col_provider, col_sector = st.columns(2)

        with col_provider:
            provider = st.radio("Provider", ["ESO", "Litgrid"], index=0, horizontal=True, key="p2h_provider")

        with col_sector:
            sector = st.radio("Sector", ["Paslaugų", "Energetikos", "Pramonės", "Telkėjas", "Kita"], index=0,
                              horizontal=True, key="p2h_sector")

        # Add regulation direction selector
        regulation_direction = st.radio(
            "Pasirinkite galimą teikti reguliavimo paslaugą:",
            ["Aukštyn", "Žemyn", "Į abi puses"],
            horizontal=True,
            key="p2h_regulation_direction"
        )

        # County dropdown
        county_options = [
            "Alytus", "Kaunas", "Klaipėda", "Marijampolė", "Panevėžys",
            "Šiauliai", "Tauragė", "Telšiai", "Utena", "Vilnius"
        ]
        county = st.selectbox("Apskritis (County)", county_options, index=1, key="p2h_county")  # Default to Kaunas

        # Create columns for a more compact layout
        col1, col2 = st.columns(2)

        with col1:
            # Add yearly heat energy demand
            q_yearly = st.number_input("Metinis šilumos energijos poreikis (MWh)", min_value=0.0, value=13000000.0,
                                       step=100.0, key="p2h_q_yearly")

            q_max_hp = st.number_input("Q_max_HP (MW)", min_value=0.0, value=2.0, step=0.1, key="p2h_q_max_hp")

            # Reaction time sliders with fixed values
            reaction_time_labels = {
                30: "<=30s",
                300: "<=300s",
                750: "<=750s",
                1000: ">750s"
            }

            # Always show both sliders
            reaction_time_u = st.select_slider(
                "reaction_time_u (s) - Upward Regulation Time",
                options=[30, 300, 750, 1000],
                value=300,
                format_func=lambda x: reaction_time_labels[x],
                key="p2h_reaction_time_u"
            )

            reaction_time_d = st.select_slider(
                "reaction_time_d (s) - Downward Regulation Time",
                options=[30, 300, 750, 1000],
                value=300,
                format_func=lambda x: reaction_time_labels[x],
                key="p2h_reaction_time_d"
            )

            t_hp = st.number_input("T_HP (°C)", value=-10.0, step=0.5, key="p2h_t_hp")
            q_max_boiler = st.number_input("Q_max_BOILER (MW)", min_value=0.0, value=3.0, step=0.1,
                                           key="p2h_q_max_boiler")
            p_fuel = st.number_input("P_FUEL (EUR/nm³)", min_value=0.0, value=0.75, step=0.01, key="p2h_p_fuel")
            q_fuel = st.number_input("q_FUEL (kWh/nm³)", min_value=0.0, value=9550.0, step=10.0, key="p2h_q_fuel")
            eta_boiler = st.number_input("eta_BOILER (%)", min_value=0.0, max_value=100.0, value=98.0, step=0.1,
                                         key="p2h_eta_boiler")
            d_hs = st.number_input("d_HS (m)", min_value=0.0, value=5.0, step=0.1, key="p2h_d_hs")

        with col2:
            h_hs = st.number_input("H_HS (m)", min_value=0.0, value=12.0, step=0.1, key="p2h_h_hs")
            t_max_hs = st.number_input("T_max_HS (°C)", min_value=0.0, value=85.0, step=1.0, key="p2h_t_max_hs")
            lambda_hs = st.number_input("lambda_HS (W/m·K)", min_value=0.0, value=0.032, format="%.3f", step=0.001,
                                        key="p2h_lambda_hs")
            dx_hs = st.number_input("dx_HS (m)", min_value=0.0, value=0.25, step=0.01, key="p2h_dx_hs")
            capex_hp = st.number_input("CAPEX_HP (tūkst. EUR/MW)", min_value=0.0, value=6000.0, step=100.0,
                                       key="p2h_capex_hp")
            capex_hs = st.number_input("CAPEX_HS (tūkst. EUR/m³)", min_value=0.0, value=0.1, step=0.01,
                                       key="p2h_capex_hs")
            opex_hp = st.number_input("OPEX_HP (tūkst. EUR/MW/m)", min_value=0.0, value=300.0, step=10.0,
                                      key="p2h_opex_hp")
            opex_hs = st.number_input("OPEX_HS (tūkst. EUR/m³/m)", min_value=0.0, value=0.005, format="%.3f",
                                      step=0.001, key="p2h_opex_hs")

        # Row for discount rate and number of years
        col3, col4 = st.columns(2)
        with col3:
            discount_rate = st.number_input("discount_rate (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1,
                                            key="p2h_discount_rate")
        with col4:
            number_of_years = st.number_input("number_of_years", min_value=1, value=10, step=1,
                                              key="p2h_number_of_years")

        # Add price threshold sections like in BEKS
        st.subheader("Minimali siūloma kaina už balansavimo pajėgumus:")
        col5, col6, col7, col8, col9 = st.columns(5)

        with col5:
            p_fcr_cap_bsp = st.number_input("FCR", min_value=0.0, value=0.0, step=1.0, key="p2h_fcr_cap_thresh")
        with col6:
            p_afrru_cap_bsp = st.number_input("aFRRu", min_value=0.0, value=0.0, step=1.0, key="p2h_afrru_cap_thresh")
        with col7:
            p_afrrd_cap_bsp = st.number_input("aFRRd", min_value=0.0, value=0.0, step=1.0, key="p2h_afrrd_cap_thresh")
        with col8:
            p_mfrru_cap_bsp = st.number_input("mFRRu", min_value=0.0, value=0.0, step=1.0, key="p2h_mfrru_cap_thresh")
        with col9:
            p_mfrrd_cap_bsp = st.number_input("mFRRd", min_value=0.0, value=0.0, step=1.0, key="p2h_mfrrd_cap_thresh")

        st.subheader("Minimali siūloma kaina už balansavimo energiją:")
        col10, col11, col12, col13 = st.columns(4)

        with col10:
            p_afrru_bsp = st.number_input("aFRRu", min_value=0.0, value=0.0, step=1.0, key="p2h_afrru_energy_thresh")
        with col11:
            p_afrrd_bsp = st.number_input("aFRRd", min_value=0.0, value=0.0, step=1.0, key="p2h_afrrd_energy_thresh")
        with col12:
            p_mfrru_bsp = st.number_input("mFRRu", min_value=0.0, value=0.0, step=1.0, key="p2h_mfrru_energy_thresh")
        with col13:
            p_mfrrd_bsp = st.number_input("mFRRd", min_value=0.0, value=0.0, step=1.0, key="p2h_mfrrd_energy_thresh")

        # Submit button
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        # Adjust reaction time based on regulation direction
        if regulation_direction == "Aukštyn":
            adjusted_reaction_time_u = reaction_time_u
            adjusted_reaction_time_d = 0
            produktai = {"FCR": False, "aFRRd": False, "aFRRu": True, "mFRRd": False, "mFRRu": True}
        elif regulation_direction == "Žemyn":
            adjusted_reaction_time_u = 0
            adjusted_reaction_time_d = reaction_time_d
            produktai = {"FCR": False, "aFRRd": True, "aFRRu": False, "mFRRd": True, "mFRRu": False}
        else:  # "Į abi puses"
            adjusted_reaction_time_u = reaction_time_u
            adjusted_reaction_time_d = reaction_time_d
            produktai = {"FCR": True, "aFRRd": True, "aFRRu": True, "mFRRd": True, "mFRRu": True}

        # Create the request body
        request_body = {
            "provider": provider, "Q_max_HP": q_max_hp, "reaction_time_u": adjusted_reaction_time_u,
            "reaction_time_d": adjusted_reaction_time_d, "T_HP": t_hp, "Q_max_BOILER": q_max_boiler,
            "P_FUEL": p_fuel, "q_FUEL": q_fuel, "eta_BOILER": eta_boiler, "d_HS": d_hs, "H_HS": h_hs,
            "T_max_HS": t_max_hs, "lambda_HS": lambda_hs, "dx_HS": dx_hs, "CAPEX_HP": capex_hp,
            "CAPEX_HS": capex_hs, "OPEX_HP": opex_hp, "OPEX_HS": opex_hs, "discount_rate": discount_rate,
            "number_of_years": number_of_years, "P_FCR_CAP_BSP": p_fcr_cap_bsp,
            "P_aFRRu_CAP_BSP": p_afrru_cap_bsp, "P_aFRRd_CAP_BSP": p_afrrd_cap_bsp,
            "P_mFRRu_CAP_BSP": p_mfrru_cap_bsp, "P_mFRRd_CAP_BSP": p_mfrrd_cap_bsp,
            "P_aFRRu_BSP": p_afrru_bsp, "P_aFRRd_BSP": p_afrrd_bsp, "P_mFRRu_BSP": p_mfrru_bsp,
            "P_mFRRd_BSP": p_mfrrd_bsp, "Sector": sector, "County": convert_lt_chars(county),
            "Q_yearly": q_yearly, "produktai": produktai
        }

        with st.expander("Request Body"):
            st.json(request_body)

        with st.spinner("Processing request..."):
            try:
                response = requests.post(f"{BE_URL}p2h", json=request_body)

                if response.status_code == 200:
                    data = response.json()
                    st.success("Request successful!")
                    st.download_button(
                        label="Download JSON",
                        data=json.dumps(data, indent=2),
                        file_name="p2h_response.json",
                        mime="application/json"
                    )

                    st.header("Visualization")
                    tab1, tab2, tab3 = st.tabs(["Summary", "Market Details", "Economic Results"])

                    with tab1:
                        st.subheader("SUMMARY")
                        if "aggregated" in data and "summary" in data["aggregated"]:
                            summary = data["aggregated"]["summary"]
                            st.write("##### YEARLY SUMMARY")
                            st.table(summary.get('yearly_summary_table', []))
                            st.write("##### PROJECT (LIFETIME) SUMMARY")
                            st.table(summary.get('project_summary_table', []))
                            st.write("##### SUPPLEMENTED WITH GRAPHS")
                            col1, col2 = st.columns(2)
                            with col1:
                                npv_data = summary.get('npv_chart_data', {})
                                if npv_data and 'years' in npv_data and 'dcfs' in npv_data and 'npv' in npv_data:
                                    fig_npv = make_subplots(specs=[[{"secondary_y": True}]])
                                    fig_npv.add_trace(go.Bar(x=npv_data['years'], y=npv_data['dcfs'],
                                                             name="Discounted Cash Flow", marker_color="lightblue",
                                                             opacity=0.7),
                                                      secondary_y=False)
                                    fig_npv.add_trace(go.Scatter(x=npv_data['years'], y=npv_data['npv'],
                                                                 mode="lines+markers", name="Cumulative NPV",
                                                                 line=dict(color="red", width=3)), secondary_y=True)
                                    if npv_data.get('break_even_point') is not None and \
                                            isinstance(npv_data['break_even_point'], int) and \
                                            0 <= npv_data['break_even_point'] < len(npv_data['years']):
                                        break_even_year = npv_data['years'][npv_data['break_even_point']]
                                        break_even_value = npv_data['npv'][npv_data['break_even_point']]
                                        fig_npv.add_scatter(x=[break_even_year], y=[break_even_value], mode="markers",
                                                            marker=dict(size=10, color="green"),
                                                            name="Break-even Point",
                                                            secondary_y=True)
                                    fig_npv.update_xaxes(title_text="Year")
                                    fig_npv.update_yaxes(title_text="Discounted Cash Flow (tūkst. EUR)",
                                                         secondary_y=False)
                                    fig_npv.update_yaxes(title_text="Cumulative NPV (tūkst. EUR)", secondary_y=True)
                                    fig_npv.update_layout(title="NET PRESENT VALUE ANALYSIS", hovermode='x unified')
                                    st.plotly_chart(fig_npv, use_container_width=True)
                                else:
                                    st.info("NPV chart data is incomplete or missing key fields.")
                            with col2:
                                rev_cost_data = summary.get('revenue_cost_chart_data', {})
                                if rev_cost_data and 'products' in rev_cost_data and 'values' in rev_cost_data:
                                    fig_rev_cost = px.bar(x=rev_cost_data['products'], y=rev_cost_data['values'],
                                                          labels={"x": "Category", "y": "Value (tūkst. EUR)"},
                                                          title="COST COMPARISON")
                                    colors = ['red' if v < 0 else 'green' for v in rev_cost_data['values']]
                                    fig_rev_cost.update_traces(marker_color=colors,
                                                               hovertemplate='%{y:,.2f}<extra></extra>')
                                    st.plotly_chart(fig_rev_cost, use_container_width=True)
                                else:
                                    st.info("Revenue/Cost chart data is incomplete or missing key fields.")

                            col3, col4 = st.columns(2)
                            with col3:
                                util_data = summary.get('utilisation_chart_data', {})
                                if util_data and util_data.get('products') and util_data.get('values'):
                                    fig_util = px.bar(
                                        x=util_data['products'],
                                        y=util_data['values'],
                                        labels={"x": "Product", "y": "Utilisation (%)"},
                                        title="UTILISATION (% TIME) BY PRODUCTS"
                                    )
                                    fig_util.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
                                    st.plotly_chart(fig_util, use_container_width=True)
                                else:
                                    st.info("Utilisation chart data is incomplete or missing key fields.")

                            with col4:
                                if "bid_percentages" in data.get("aggregated", {}):
                                    bid_data = data["aggregated"]["bid_percentages"]
                                    bid_products = [str(k) for k, v in bid_data.items() if
                                                    isinstance(v, (int, float)) and v > 0]
                                    bid_values = [v for k, v in bid_data.items() if
                                                  isinstance(v, (int, float)) and v > 0]

                                    if bid_products:
                                        fig_bids = px.bar(
                                            x=bid_products,
                                            y=bid_values,
                                            labels={"x": "Product", "y": "Selection Rate (%)"},
                                            title="BID SELECTION RATE BY PRODUCT"
                                        )
                                        fig_bids.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
                                        st.plotly_chart(fig_bids, use_container_width=True)
                                    # else: # Optional info if no valid bid data
                                    #     st.info("No valid bid selection data to display (>0).")
                                # else: # Optional info if key is missing
                                #     st.info("Bid percentages data not found in response.")

                    with tab2:
                        st.subheader("MARKET DETAILS")
                        st.markdown("""
                        <style>
                        .market-table { width: 100%; border-collapse: collapse; margin-bottom: 0px; font-size: 12px; }
                        .market-table td { padding: 3px; text-align: center; }
                        .market-table th { padding: 3px; text-align: center; font-weight: bold; }
                        .power-table td { background-color: #E0F0F5; }
                        .power-header { font-weight: bold; background-color: #C5E0E8 !important; }
                        .power-direction-header { background-color: #D5E8EF !important; }
                        .power-market-title { background-color: #3D7890; color: white; padding: 5px; margin: 0; height: auto; font-size: 14px; }
                        .energy-table td { background-color: #E6F5EC; }
                        .energy-header { font-weight: bold; background-color: #D0EAD9 !important; }
                        .energy-direction-header { background-color: #DCF0E2 !important; }
                        .energy-market-title { background-color: #4D9D6A; color: white; padding: 5px; margin: 0; height: auto; font-size: 14px; }
                        .trading-table td { background-color: #EFF5D8; }
                        .trading-header { font-weight: bold; background-color: #E5ECC5 !important; }
                        .trading-direction-header { background-color: #EAEFCE !important; }
                        .trading-market-title { background-color: #8CB63C; color: white; padding: 5px; margin: 0; height: auto; font-size: 14px; }
                        .row-compact { margin-bottom: 0px !important; padding: 0px !important; }
                        hr { margin: 5px 0 !important; }
                        </style>
                        """, unsafe_allow_html=True)

                        if "aggregated" in data and "markets" in data["aggregated"]:
                            markets_data = data["aggregated"]["markets"]

                            market_tabs_p2h = st.tabs([
                                "BALANSAVIMO PAJĖGUMŲ RINKA",
                                "BALANSAVIMO ENERGIJOS RINKA",
                                "ELEKTROS ENERGIJOS PREKYBA"
                            ])

                            # Tab 1: Power Balancing Market (P2H)
                            with market_tabs_p2h[0]:
                                if 'BALANSAVIMO_PAJEGUMU_RINKA' in markets_data:
                                    balansavimo_pajegumu_data = markets_data['BALANSAVIMO_PAJEGUMU_RINKA']
                                    processed_something_in_power = False
                                    # FCR section
                                    if 'FCR' in balansavimo_pajegumu_data:
                                        fcr_data = balansavimo_pajegumu_data['FCR']
                                        col1, col2 = st.columns([1, 5])
                                        with col1:
                                            st.markdown(
                                                f"""<div class="power-market-title"><h4 style="margin:0;">{fcr_data.get('header', 'FCR')}</h4><small>{fcr_data.get('description', 'FREQUENCY CONTAINMENT RESERVE')}</small></div>""",
                                                unsafe_allow_html=True)
                                        with col2:
                                            st.markdown(
                                                f"""<table class="market-table power-table"><tr><th class="power-header">{fcr_data.get('volume_of_procured_reserves', {}).get('header', 'VOLUME OF PROCURED RESERVES')}</th></tr><tr><td>{fcr_data.get('volume_of_procured_reserves', {}).get('value', 0):.2f} MW</td></tr></table>""" +
                                                f"""<table class="market-table power-table"><tr><th class="power-header">{fcr_data.get('utilisation', {}).get('header', 'UTILISATION (% OF TIME)')}</th></tr><tr><td>{fcr_data.get('utilisation', {}).get('value', 0.0):.2f} %</td></tr></table>""" +
                                                f"""<table class="market-table power-table"><tr><th class="power-header">{fcr_data.get('potential_revenue', {}).get('header', 'POTENTIAL REVENUE')}</th></tr><tr><td>{fcr_data.get('potential_revenue', {}).get('value', 0.0):.2f} tūkst. EUR</td></tr></table>""" +
                                                f"""<table class="market-table power-table"><tr><th class="power-header">{fcr_data.get('bids_selected', {}).get('header', '% OF BIDS SELECTED')}</th></tr><tr><td>{fcr_data.get('bids_selected', {}).get('value', 0.0):.2f} %</td></tr></table>""",
                                                unsafe_allow_html=True)
                                        st.markdown("<hr>", unsafe_allow_html=True)
                                        processed_something_in_power = True
                                    # aFRR section
                                    if 'aFRR' in balansavimo_pajegumu_data:
                                        afrr_data = balansavimo_pajegumu_data['aFRR']
                                        col1, col2 = st.columns([1, 5])
                                        with col1:
                                            st.markdown(
                                                f"""<div class="power-market-title"><h4 style="margin:0;">{afrr_data.get('header', 'aFRR')}</h4><small>{afrr_data.get('description', 'AUTOMATIC FREQUENCY RESTORATION RESERVE')}</small></div>""",
                                                unsafe_allow_html=True)
                                        with col2:
                                            st.markdown(
                                                f"""<table class="market-table power-table"><tr><th class="power-header" colspan="2">{afrr_data.get('volume_of_procured_reserves', {}).get('header', 'VOLUME OF PROCURED RESERVES')}</th></tr><tr><th class="power-direction-header">UPWARD</th><th class="power-direction-header">DOWNWARD</th></tr><tr><td>{afrr_data.get('volume_of_procured_reserves', {}).get('upward', {}).get('value', 0):.2f} MW</td><td>{afrr_data.get('volume_of_procured_reserves', {}).get('downward', {}).get('value', 0):.2f} MW</td></tr></table>""" +
                                                f"""<table class="market-table power-table"><tr><th class="power-header" colspan="2">{afrr_data.get('utilisation', {}).get('header', 'UTILISATION (% OF TIME)')}</th></tr><tr><th class="power-direction-header">UPWARD</th><th class="power-direction-header">DOWNWARD</th></tr><tr><td>{afrr_data.get('utilisation', {}).get('upward', {}).get('value', 0.0):.2f} %</td><td>{afrr_data.get('utilisation', {}).get('downward', {}).get('value', 0.0):.2f} %</td></tr></table>""" +
                                                f"""<table class="market-table power-table"><tr><th class="power-header" colspan="2">{afrr_data.get('potential_revenue', {}).get('header', 'POTENTIAL REVENUE')}</th></tr><tr><th class="power-direction-header">UPWARD</th><th class="power-direction-header">DOWNWARD</th></tr><tr><td>{afrr_data.get('potential_revenue', {}).get('upward', {}).get('value', 0.0):.2f} tūkst. EUR</td><td>{afrr_data.get('potential_revenue', {}).get('downward', {}).get('value', 0.0):.2f} tūkst. EUR</td></tr></table>""" +
                                                f"""<table class="market-table power-table"><tr><th class="power-header" colspan="2">{afrr_data.get('bids_selected', {}).get('header', '% OF BIDS SELECTED')}</th></tr><tr><th class="power-direction-header">UPWARD</th><th class="power-direction-header">DOWNWARD</th></tr><tr><td>{afrr_data.get('bids_selected', {}).get('upward', {}).get('value', 0.0):.2f} %</td><td>{afrr_data.get('bids_selected', {}).get('downward', {}).get('value', 0.0):.2f} %</td></tr></table>""",
                                                unsafe_allow_html=True)
                                        st.markdown("<hr>", unsafe_allow_html=True)
                                        processed_something_in_power = True
                                    # mFRR section
                                    if 'mFRR' in balansavimo_pajegumu_data:
                                        mfrr_data = balansavimo_pajegumu_data['mFRR']
                                        col1, col2 = st.columns([1, 5])
                                        with col1:
                                            st.markdown(
                                                f"""<div class="power-market-title"><h4 style="margin:0;">{mfrr_data.get('header', 'mFRR')}</h4><small>{mfrr_data.get('description', 'MANUAL FREQUENCY RESTORATION RESERVE')}</small></div>""",
                                                unsafe_allow_html=True)
                                        with col2:
                                            st.markdown(
                                                f"""<table class="market-table power-table"><tr><th class="power-header" colspan="2">{mfrr_data.get('volume_of_procured_reserves', {}).get('header', 'VOLUME OF PROCURED RESERVES')}</th></tr><tr><th class="power-direction-header">UPWARD</th><th class="power-direction-header">DOWNWARD</th></tr><tr><td>{mfrr_data.get('volume_of_procured_reserves', {}).get('upward', {}).get('value', 0):.2f} MW</td><td>{mfrr_data.get('volume_of_procured_reserves', {}).get('downward', {}).get('value', 0):.2f} MW</td></tr></table>""" +
                                                f"""<table class="market-table power-table"><tr><th class="power-header" colspan="2">{mfrr_data.get('utilisation', {}).get('header', 'UTILISATION (% OF TIME)')}</th></tr><tr><th class="power-direction-header">UPWARD</th><th class="power-direction-header">DOWNWARD</th></tr><tr><td>{mfrr_data.get('utilisation', {}).get('upward', {}).get('value', 0.0):.2f} %</td><td>{mfrr_data.get('utilisation', {}).get('downward', {}).get('value', 0.0):.2f} %</td></tr></table>""" +
                                                f"""<table class="market-table power-table"><tr><th class="power-header" colspan="2">{mfrr_data.get('potential_revenue', {}).get('header', 'POTENTIAL REVENUE')}</th></tr><tr><th class="power-direction-header">UPWARD</th><th class="power-direction-header">DOWNWARD</th></tr><tr><td>{mfrr_data.get('potential_revenue', {}).get('upward', {}).get('value', 0.0):.2f} tūkst. EUR</td><td>{mfrr_data.get('potential_revenue', {}).get('downward', {}).get('value', 0.0):.2f} tūkst. EUR</td></tr></table>""" +
                                                f"""<table class="market-table power-table"><tr><th class="power-header" colspan="2">{mfrr_data.get('bids_selected', {}).get('header', '% OF BIDS SELECTED')}</th></tr><tr><th class="power-direction-header">UPWARD</th><th class="power-direction-header">DOWNWARD</th></tr><tr><td>{mfrr_data.get('bids_selected', {}).get('upward', {}).get('value', 0.0):.2f} %</td><td>{mfrr_data.get('bids_selected', {}).get('downward', {}).get('value', 0.0):.2f} %</td></tr></table>""",
                                                unsafe_allow_html=True)
                                        # No <hr> after the last item if it's mFRR
                                        processed_something_in_power = True
                                    if not processed_something_in_power:
                                        st.info("Nėra duomenų apie balansavimo pajėgumų rinką.")
                                else:
                                    st.info("Balansavimo pajėgumų rinkos duomenų nėra.")

                            # Tab 2: Energy Balancing Market (P2H)
                            with market_tabs_p2h[1]:
                                if 'BALANSAVIMO_ENERGIJOS_RINKA' in markets_data:
                                    balansavimo_energijos_data = markets_data['BALANSAVIMO_ENERGIJOS_RINKA']
                                    processed_something_in_energy = False
                                    # aFRR section
                                    if 'aFRR' in balansavimo_energijos_data:
                                        afrr_data = balansavimo_energijos_data['aFRR']
                                        col1, col2 = st.columns([1, 5])
                                        with col1:
                                            st.markdown(
                                                f"""<div class="energy-market-title"><h4 style="margin:0;">{afrr_data.get('header', 'aFRR')}</h4><small>{afrr_data.get('description', 'AUTOMATIC FREQUENCY RESTORATION RESERVE')}</small></div>""",
                                                unsafe_allow_html=True)
                                        with col2:
                                            st.markdown(
                                                f"""<table class="market-table energy-table"><tr><th class="energy-header" colspan="2">{afrr_data.get('volume_of_procured_energy', {}).get('header', 'VOLUME OF PROCURED ENERGY')}</th></tr><tr><th class="energy-direction-header">UPWARD</th><th class="energy-direction-header">DOWNWARD</th></tr><tr><td>{afrr_data.get('volume_of_procured_energy', {}).get('upward', {}).get('value', 0.0):.2f} MWh</td><td>{afrr_data.get('volume_of_procured_energy', {}).get('downward', {}).get('value', 0.0):.2f} MWh</td></tr></table>""" +
                                                f"""<table class="market-table energy-table"><tr><th class="energy-header" colspan="2">{afrr_data.get('utilisation', {}).get('header', 'UTILISATION (% OF TIME)')}</th></tr><tr><th class="energy-direction-header">UPWARD</th><th class="energy-direction-header">DOWNWARD</th></tr><tr><td>{afrr_data.get('utilisation', {}).get('upward', {}).get('value', 0.0):.2f} %</td><td>{afrr_data.get('utilisation', {}).get('downward', {}).get('value', 0.0):.2f} %</td></tr></table>""" +
                                                f"""<table class="market-table energy-table"><tr><th class="energy-header" colspan="2">{afrr_data.get('potential_revenue', {}).get('header', 'POTENTIAL REVENUE')}</th></tr><tr><th class="energy-direction-header">UPWARD</th><th class="energy-direction-header">DOWNWARD</th></tr><tr><td>{afrr_data.get('potential_revenue', {}).get('upward', {}).get('value', 0.0):.2f} tūkst. EUR</td><td>{afrr_data.get('potential_revenue', {}).get('downward', {}).get('value', 0.0):.2f} tūkst. EUR</td></tr></table>""" +
                                                f"""<table class="market-table energy-table"><tr><th class="energy-header" colspan="2">{afrr_data.get('bids_selected', {}).get('header', '% OF BIDS SELECTED')}</th></tr><tr><th class="energy-direction-header">UPWARD</th><th class="energy-direction-header">DOWNWARD</th></tr><tr><td>{afrr_data.get('bids_selected', {}).get('upward', {}).get('value', 0.0):.2f} %</td><td>{afrr_data.get('bids_selected', {}).get('downward', {}).get('value', 0.0):.2f} %</td></tr></table>""",
                                                unsafe_allow_html=True)
                                        st.markdown("<hr>", unsafe_allow_html=True)
                                        processed_something_in_energy = True
                                    # mFRR section
                                    if 'mFRR' in balansavimo_energijos_data:
                                        mfrr_data = balansavimo_energijos_data['mFRR']
                                        col1, col2 = st.columns([1, 5])
                                        with col1:
                                            st.markdown(
                                                f"""<div class="energy-market-title"><h4 style="margin:0;">{mfrr_data.get('header', 'mFRR')}</h4><small>{mfrr_data.get('description', 'MANUAL FREQUENCY RESTORATION RESERVE')}</small></div>""",
                                                unsafe_allow_html=True)
                                        with col2:
                                            st.markdown(
                                                f"""<table class="market-table energy-table"><tr><th class="energy-header" colspan="2">{mfrr_data.get('volume_of_procured_energy', {}).get('header', 'VOLUME OF PROCURED ENERGY')}</th></tr><tr><th class="energy-direction-header">UPWARD</th><th class="energy-direction-header">DOWNWARD</th></tr><tr><td>{mfrr_data.get('volume_of_procured_energy', {}).get('upward', {}).get('value', 0.0):.2f} MWh</td><td>{mfrr_data.get('volume_of_procured_energy', {}).get('downward', {}).get('value', 0.0):.2f} MWh</td></tr></table>""" +
                                                f"""<table class="market-table energy-table"><tr><th class="energy-header" colspan="2">{mfrr_data.get('utilisation', {}).get('header', 'UTILISATION (% OF TIME)')}</th></tr><tr><th class="energy-direction-header">UPWARD</th><th class="energy-direction-header">DOWNWARD</th></tr><tr><td>{mfrr_data.get('utilisation', {}).get('upward', {}).get('value', 0.0):.2f} %</td><td>{mfrr_data.get('utilisation', {}).get('downward', {}).get('value', 0.0):.2f} %</td></tr></table>""" +
                                                f"""<table class="market-table energy-table"><tr><th class="energy-header" colspan="2">{mfrr_data.get('potential_revenue', {}).get('header', 'POTENTIAL REVENUE')}</th></tr><tr><th class="energy-direction-header">UPWARD</th><th class="energy-direction-header">DOWNWARD</th></tr><tr><td>{mfrr_data.get('potential_revenue', {}).get('upward', {}).get('value', 0.0):.2f} tūkst. EUR</td><td>{mfrr_data.get('potential_revenue', {}).get('downward', {}).get('value', 0.0):.2f} tūkst. EUR</td></tr></table>""" +
                                                f"""<table class="market-table energy-table"><tr><th class="energy-header" colspan="2">{mfrr_data.get('bids_selected', {}).get('header', '% OF BIDS SELECTED')}</th></tr><tr><th class="energy-direction-header">UPWARD</th><th class="energy-direction-header">DOWNWARD</th></tr><tr><td>{mfrr_data.get('bids_selected', {}).get('upward', {}).get('value', 0.0):.2f} %</td><td>{mfrr_data.get('bids_selected', {}).get('downward', {}).get('value', 0.0):.2f} %</td></tr></table>""",
                                                unsafe_allow_html=True)
                                        processed_something_in_energy = True
                                    if not processed_something_in_energy:
                                        st.info("Nėra duomenų apie balansavimo energijos rinką.")
                                else:
                                    st.info("Balansavimo energijos rinkos duomenų nėra.")

                            # Tab 3: Electricity Trading (P2H)
                            with market_tabs_p2h[2]:
                                if 'ELEKTROS_ENERGIJOS_PREKYBA' in markets_data:
                                    elektros_energijos_data = markets_data['ELEKTROS_ENERGIJOS_PREKYBA']
                                    section_keys = list(elektros_energijos_data.keys())
                                    if not section_keys:
                                        st.info("Nėra elektros energijos prekybos duomenų.")

                                    for i, section_name in enumerate(section_keys):
                                        section_data = elektros_energijos_data[section_name]

                                        col1, col2 = st.columns([1, 5])
                                        with col1:
                                            st.markdown(
                                                f"""<div class="trading-market-title"><h4 style="margin:0;">{section_data.get('header', section_name.replace('_', ' '))}</h4><small>{section_data.get('description', '')}</small></div>""",
                                                unsafe_allow_html=True)

                                        html_tables_trading = ""
                                        # Volume of Energy Exchange
                                        voee = section_data.get('volume_of_energy_exchange', {})
                                        voee_header_text = voee.get('header', 'VOLUME OF ENERGY EXCHANGE')
                                        if 'sale' in voee:  # Standard purchase/sale structure
                                            html_tables_trading += f"""<table class="market-table trading-table"><tr><th class="trading-header" colspan="2">{voee_header_text}</th></tr>
                                                                    <tr><th class="trading-direction-header">PURCHASE</th><th class="trading-direction-header">SALE</th></tr>
                                                                    <tr><td>{voee.get('purchase', {}).get('value', 0.0):.2f} MWh</td><td>{voee.get('sale', {}).get('value', 0.0):.2f} MWh</td></tr></table>"""
                                        elif 'purchase' in voee:  # Purchase only (e.g., Electricity Consumption, Heat Generation)
                                            if section_name == "Heat_Generation" and 'header' not in voee:  # Specific header for Heat Gen if not provided
                                                voee_header_text = "VOLUME OF HEAT GENERATED"
                                            elif section_name == "Electricity_Consumption" and 'header' not in voee:
                                                voee_header_text = "VOLUME OF ENERGY PURCHASED"

                                            html_tables_trading += f"""<table class="market-table trading-table"><tr><th class="trading-header">{voee_header_text}</th></tr>
                                                                    <tr><td>{voee.get('purchase', {}).get('value', 0.0):.2f} MWh</td></tr></table>"""
                                        else:  # Fallback
                                            html_tables_trading += f"""<table class="market-table trading-table"><tr><th class="trading-header" colspan="2">{voee_header_text}</th></tr><tr><td colspan="2">Nėra duomenų</td></tr></table>"""

                                        # Percentage of Time
                                        pot = section_data.get('percentage_of_time', {})
                                        pot_header_text = pot.get('header', '% OF TIME')
                                        if 'sale' in pot:
                                            html_tables_trading += f"""<table class="market-table trading-table"><tr><th class="trading-header" colspan="2">{pot_header_text}</th></tr>
                                                                    <tr><th class="trading-direction-header">PURCHASE</th><th class="trading-direction-header">SALE</th></tr>
                                                                    <tr><td>{pot.get('purchase', {}).get('value', 0.0):.2f} %</td><td>{pot.get('sale', {}).get('value', 0.0):.2f} %</td></tr></table>"""
                                        elif 'purchase' in pot:
                                            html_tables_trading += f"""<table class="market-table trading-table"><tr><th class="trading-header">{pot_header_text}</th></tr>
                                                                    <tr><td>{pot.get('purchase', {}).get('value', 0.0):.2f} %</td></tr></table>"""
                                        else:
                                            html_tables_trading += f"""<table class="market-table trading-table"><tr><th class="trading-header" colspan="2">{pot_header_text}</th></tr><tr><td colspan="2">Nėra duomenų</td></tr></table>"""

                                        # Potential Cost/Revenue
                                        pcr = section_data.get('potential_cost_revenue', {})
                                        pcr_header_text = pcr.get('header', 'COST & REVENUE')
                                        if 'revenue' in pcr and 'cost' in pcr:  # Standard cost/revenue structure
                                            html_tables_trading += f"""<table class="market-table trading-table"><tr><th class="trading-header" colspan="2">{pcr_header_text}</th></tr>
                                                                    <tr><th class="trading-direction-header">COST</th><th class="trading-direction-header">REVENUE</th></tr>
                                                                    <tr><td>{pcr.get('cost', {}).get('value', 0.0):.2f} tūkst. EUR</td><td>{pcr.get('revenue', {}).get('value', 0.0):.2f} tūkst. EUR</td></tr></table>"""
                                        elif 'cost' in pcr:  # Cost only
                                            if 'header' not in pcr: pcr_header_text = "COST"  # Override if only cost and no specific header
                                            html_tables_trading += f"""<table class="market-table trading-table"><tr><th class="trading-header">{pcr_header_text}</th></tr>
                                                                    <tr><td>{pcr.get('cost', {}).get('value', 0.0):.2f} tūkst. EUR</td></tr></table>"""
                                        else:  # Fallback
                                            html_tables_trading += f"""<table class="market-table trading-table"><tr><th class="trading-header" colspan="2">{pcr_header_text}</th></tr><tr><td colspan="2">Nėra duomenų</td></tr></table>"""

                                        with col2:
                                            st.markdown(html_tables_trading, unsafe_allow_html=True)

                                        if i < len(section_keys) - 1:  # Add <hr> if not the last section
                                            st.markdown("<hr>", unsafe_allow_html=True)
                                else:
                                    st.info("Elektros energijos prekybos duomenų nėra.")

                    with tab3:
                        st.subheader("ECONOMIC RESULTS BY PRODUCT")

                        if "aggregated" in data and "economic_results" in data["aggregated"]:
                            econ_data = data["aggregated"]["economic_results"]

                            st.write("##### REVENUE BY PRODUCT")
                            if "revenue_table" in econ_data and econ_data["revenue_table"]:
                                st.table(econ_data["revenue_table"])
                                fig_rev = px.bar(
                                    econ_data["revenue_table"], x="Product", y="Value (tūkst. EUR)",
                                    title="REVENUE BY PRODUCT"
                                )
                                fig_rev.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
                                st.plotly_chart(fig_rev, use_container_width=True)
                            else:
                                st.info("No revenue data available")

                            st.write("##### COST BY PRODUCT")
                            if "cost_table" in econ_data and econ_data["cost_table"]:
                                st.table(econ_data["cost_table"])
                                fig_cost = px.bar(
                                    econ_data["cost_table"], x="Product", y="Value (tūkst. EUR)",
                                    title="COST BY PRODUCT"
                                )
                                fig_cost.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
                                st.plotly_chart(fig_cost, use_container_width=True)
                            else:
                                st.info("No cost data available")

                            st.metric("TOTAL SAVINGS", f"{econ_data.get('total_profit', 0):.2f} tūkst. EUR")

                            st.write("##### YEARLY RESULTS")
                            if "yearly_table" in econ_data and econ_data["yearly_table"]:
                                yearly_df = pd.DataFrame(econ_data["yearly_table"])
                                st.table(yearly_df)

                                if "YEAR" in yearly_df.columns and "NPV" in yearly_df.columns:
                                    fig_yearly_npv = px.line(
                                        yearly_df, x="YEAR", y="NPV", markers=True,
                                        title="NET PRESENT VALUE OVER TIME"
                                    )
                                    fig_yearly_npv.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
                                    st.plotly_chart(fig_yearly_npv, use_container_width=True)

                                y_metrics = [col for col in ["CAPEX", "OPEX", "CF"] if col in yearly_df.columns]
                                if "YEAR" in yearly_df.columns and y_metrics:
                                    fig_yearly_metrics = px.bar(
                                        yearly_df, x="YEAR", y=y_metrics,
                                        title="YEARLY FINANCIAL METRICS", barmode="group"
                                    )
                                    st.plotly_chart(fig_yearly_metrics, use_container_width=True)
                            else:
                                st.info("No yearly results data available.")
                        else:
                            st.info("Economic results data not found.")
                else:
                    try:
                        error_data = response.json()
                        if "detail" in error_data:
                            st.error(f"Calculation failed: {error_data['detail']}")
                        else:
                            st.error(f"Request failed with status code: {response.status_code}")
                    except json.JSONDecodeError:
                        st.error(f"Request failed with status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"Error making request: {str(e)}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")

elif calculator_type == "P2G":
    st.header("P2G Demo")
    st.write("Fill in the form below to submit a request to the P2G API.")

    # Create form for P2G input parameters
    with st.form("p2g_input_form"):
        st.header("Input Parameters")

        # Add Provider and Sector selection fields
        col_provider, col_sector = st.columns(2)

        with col_provider:
            provider = st.radio("Provider", ["ESO", "Litgrid"], index=1, horizontal=True, key="p2g_provider")

        with col_sector:
            sector = st.radio("Sector", ["Paslaugų", "Energetikos", "Pramonės", "Telkėjas", "Kita"], index=0,
                              horizontal=True, key="p2g_sector")

        # Add regulation direction selector (same as P2H)
        regulation_direction = st.radio(
            "Pasirinkite galimą teikti reguliavimo paslaugą:",
            ["Aukštyn", "Žemyn", "Į abi puses"],
            horizontal=True,
            key="p2g_regulation_direction"
        )

        # Electrolyzer technology selection
        electrolyzer_tech = st.radio(
            "Kokia elektrolizerio technologija:",
            ["SOEC", "AEL", "PEM"],
            horizontal=True,
            key="p2g_electrolyzer_tech"
        )

        # Create columns for a more compact layout
        col1, col2 = st.columns(2)

        with col1:
            q_max = st.number_input("Elektrolizerio elektrinė galia (MW)", min_value=0.0, value=1.0, step=0.1,
                                    key="p2g_q_max")

            # Reaction time sliders with fixed values (same as P2H)
            reaction_time_labels = {
                30: "<=30s",
                300: "<=300s",
                750: "<=750s",
                1000: ">750s"
            }

            reaction_time_u = st.select_slider(
                "reaction_time_u (s) - Upward Regulation Time",
                options=[30, 300, 750, 1000],
                value=30,
                format_func=lambda x: reaction_time_labels[x],
                key="p2g_reaction_time_u"
            )

            reaction_time_d = st.select_slider(
                "reaction_time_d (s) - Downward Regulation Time",
                options=[30, 300, 750, 1000],
                value=30,
                format_func=lambda x: reaction_time_labels[x],
                key="p2g_reaction_time_d"
            )

            eta_h2 = st.number_input("Elektrolizerio (elektra -> vandenilis) naudingumo koeficientas (%)",
                                     min_value=0.0, max_value=100.0, value=50.0, step=1.0, key="p2g_eta_h2")


            t0 = st.number_input("Pagamintų vandenilio dujų temperatūra (°C)", value=80.0, step=1.0, key="p2g_t0")
            p0 = st.number_input("Pagamintų vandenilio dujų slėgis (bar)", min_value=0.0, value=30.0, step=1.0,
                                 key="p2g_p0")

        with col2:
            eta_c = st.number_input("Kompresoriaus naudingumo koeficientas (%)", min_value=0.0, max_value=100.0,
                                    value=80.0, step=1.0, key="p2g_eta_c")
            p_h2 = st.number_input("P_H2 (EUR/kg)", min_value=0.0, value=3.5, step=0.1, key="p2g_p_h2")
            capex = st.number_input("CAPEX (tūkst. EUR/MW)", min_value=0.0, value=2000.0, step=100.0, key="p2g_capex")
            opex = st.number_input("OPEX (tūkst. EUR/MW/m)", min_value=0.0, value=16.0, step=1.0, key="p2g_opex")
            discount_rate = st.number_input("discount_rate (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1,
                                            key="p2g_discount_rate")
            number_of_years = st.number_input("number_of_years", min_value=1, value=10, step=1,
                                              key="p2g_number_of_years")

        # Add price threshold sections (same as other calculators)
        st.subheader("Minimali siūloma kaina už balansavimo pajėgumus:")
        col3, col4, col5, col6, col7 = st.columns(5)

        with col3:
            p_fcr_cap_bsp = st.number_input("FCR", min_value=0.0, value=0.0, step=1.0, key="p2g_fcr_cap")
        with col4:
            p_afrru_cap_bsp = st.number_input("aFRRu", min_value=0.0, value=0.0, step=1.0, key="p2g_afrru_cap")
        with col5:
            p_afrrd_cap_bsp = st.number_input("aFRRd", min_value=0.0, value=0.0, step=1.0, key="p2g_afrrd_cap")
        with col6:
            p_mfrru_cap_bsp = st.number_input("mFRRu", min_value=0.0, value=0.0, step=1.0, key="p2g_mfrru_cap")
        with col7:
            p_mfrrd_cap_bsp = st.number_input("mFRRd", min_value=0.0, value=0.0, step=1.0, key="p2g_mfrrd_cap")

        st.subheader("Minimali siūloma kaina už balansavimo energiją:")
        col8, col9, col10, col11 = st.columns(4)

        with col8:
            p_afrru_bsp = st.number_input("aFRRu", min_value=0.0, value=0.0, step=1.0, key="p2g_afrru_energy")
        with col9:
            p_afrrd_bsp = st.number_input("aFRRd", min_value=0.0, value=0.0, step=1.0, key="p2g_afrrd_energy")
        with col10:
            p_mfrru_bsp = st.number_input("mFRRu", min_value=0.0, value=0.0, step=1.0, key="p2g_mfrru_energy")
        with col11:
            p_mfrrd_bsp = st.number_input("mFRRd", min_value=0.0, value=0.0, step=1.0, key="p2g_mfrrd_energy")

        # Submit button
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        # Adjust reaction time and produktai based on regulation direction (same logic as P2H)
        if regulation_direction == "Aukštyn":
            adjusted_reaction_time_u = reaction_time_u
            adjusted_reaction_time_d = 0
            produktai = {"FCR": False, "aFRRd": False, "aFRRu": True, "mFRRd": False, "mFRRu": True}
        elif regulation_direction == "Žemyn":
            adjusted_reaction_time_u = 0
            adjusted_reaction_time_d = reaction_time_d
            produktai = {"FCR": False, "aFRRd": True, "aFRRu": False, "mFRRd": True, "mFRRu": False}
        else:  # "Į abi puses"
            adjusted_reaction_time_u = reaction_time_u
            adjusted_reaction_time_d = reaction_time_d
            produktai = {"FCR": True, "aFRRd": True, "aFRRu": True, "mFRRd": True, "mFRRu": True}

        # Create the request body
        request_body = {
            "Q_max": q_max,
            "P_H2": p_h2,
            "electrolyzer_tech": electrolyzer_tech,
            "eta_H2": eta_h2,
            "reaction_time_d": adjusted_reaction_time_d,
            "reaction_time_u": adjusted_reaction_time_u,
            "T0": t0,
            "p0": p0,
            "eta_C": eta_c,
            "CAPEX": capex,
            "OPEX": opex,
            "discount_rate": discount_rate,
            "number_of_years": number_of_years,
            "P_FCR_CAP_BSP": p_fcr_cap_bsp,
            "P_aFRRu_CAP_BSP": p_afrru_cap_bsp,
            "P_aFRRd_CAP_BSP": p_afrrd_cap_bsp,
            "P_mFRRu_CAP_BSP": p_mfrru_cap_bsp,
            "P_mFRRd_CAP_BSP": p_mfrrd_cap_bsp,
            "P_aFRRu_BSP": p_afrru_bsp,
            "P_aFRRd_BSP": p_afrrd_bsp,
            "P_mFRRu_BSP": p_mfrru_bsp,
            "P_mFRRd_BSP": p_mfrrd_bsp,
            "provider": provider,
            "Sector": sector,
            "produktai": produktai
        }

        with st.expander("Request Body"):
            st.json(request_body)

        with st.spinner("Processing request..."):
            try:
                response = requests.post(f"{BE_URL}p2g", json=request_body)

                if response.status_code == 200:
                    data = response.json()
                    st.success("Request successful!")
                    st.download_button(
                        label="Download JSON",
                        data=json.dumps(data, indent=2),
                        file_name="p2g_response.json",
                        mime="application/json"
                    )

                    st.header("Visualization")
                    tab1, tab2, tab3 = st.tabs(["Summary", "Market Details", "Economic Results"])

                    with tab1:
                        st.subheader("SUMMARY")
                        if "aggregated" in data and "summary" in data["aggregated"]:
                            summary = data["aggregated"]["summary"]
                            st.write("##### YEARLY SUMMARY")
                            st.table(summary.get('yearly_summary_table', []))
                            st.write("##### PROJECT (LIFETIME) SUMMARY")
                            st.table(summary.get('project_summary_table', []))
                            st.write("##### SUPPLEMENTED WITH GRAPHS")

                            col1, col2 = st.columns(2)
                            with col1:
                                npv_data = summary.get('npv_chart_data', {})
                                if npv_data and 'years' in npv_data and 'dcfs' in npv_data and 'npv' in npv_data:
                                    fig_npv = make_subplots(specs=[[{"secondary_y": True}]])
                                    fig_npv.add_trace(go.Bar(x=npv_data['years'], y=npv_data['dcfs'],
                                                             name="Discounted Cash Flow", marker_color="lightblue",
                                                             opacity=0.7),
                                                      secondary_y=False)
                                    fig_npv.add_trace(go.Scatter(x=npv_data['years'], y=npv_data['npv'],
                                                                 mode="lines+markers", name="Cumulative NPV",
                                                                 line=dict(color="red", width=3)), secondary_y=True)
                                    if npv_data.get('break_even_point') is not None and \
                                            isinstance(npv_data['break_even_point'], int) and \
                                            0 <= npv_data['break_even_point'] < len(npv_data['years']):
                                        break_even_year = npv_data['years'][npv_data['break_even_point']]
                                        break_even_value = npv_data['npv'][npv_data['break_even_point']]
                                        fig_npv.add_scatter(x=[break_even_year], y=[break_even_value], mode="markers",
                                                            marker=dict(size=10, color="green"),
                                                            name="Break-even Point",
                                                            secondary_y=True)
                                    fig_npv.update_xaxes(title_text="Year")
                                    fig_npv.update_yaxes(title_text="Discounted Cash Flow (tūkst. EUR)",
                                                         secondary_y=False)
                                    fig_npv.update_yaxes(title_text="Cumulative NPV (tūkst. EUR)", secondary_y=True)
                                    fig_npv.update_layout(title="NET PRESENT VALUE ANALYSIS", hovermode='x unified')
                                    st.plotly_chart(fig_npv, use_container_width=True)
                                else:
                                    st.info("NPV chart data is incomplete or missing key fields.")

                            with col2:
                                rev_cost_data = summary.get('revenue_cost_chart_data', {})
                                if rev_cost_data and 'products' in rev_cost_data and 'values' in rev_cost_data:
                                    fig_rev_cost = px.bar(x=rev_cost_data['products'], y=rev_cost_data['values'],
                                                          labels={"x": "Product", "y": "Value (tūkst. EUR)"},
                                                          title="REVENUE vs COST BY PRODUCTS")
                                    colors = ['red' if v < 0 else 'green' for v in rev_cost_data['values']]
                                    fig_rev_cost.update_traces(marker_color=colors,
                                                               hovertemplate='%{y:,.2f}<extra></extra>')
                                    st.plotly_chart(fig_rev_cost, use_container_width=True)
                                else:
                                    st.info("Revenue/Cost chart data is incomplete or missing key fields.")

                            col3, col4 = st.columns(2)
                            with col3:
                                util_data = summary.get('utilisation_chart_data', {})
                                if util_data and util_data.get('products') and util_data.get('values'):
                                    fig_util = px.bar(
                                        x=util_data['products'],
                                        y=util_data['values'],
                                        labels={"x": "Product", "y": "Utilisation (%)"},
                                        title="UTILISATION (% TIME) BY PRODUCTS"
                                    )
                                    fig_util.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
                                    st.plotly_chart(fig_util, use_container_width=True)
                                else:
                                    st.info("Utilisation chart data is incomplete or missing key fields.")

                    with tab2:
                        st.subheader("MARKET DETAILS")
                        st.markdown("""
                        <style>
                        .market-table { width: 100%; border-collapse: collapse; margin-bottom: 0px; font-size: 12px; }
                        .market-table td { padding: 3px; text-align: center; }
                        .market-table th { padding: 3px; text-align: center; font-weight: bold; }
                        .power-table td { background-color: #E0F0F5; }
                        .power-header { font-weight: bold; background-color: #C5E0E8 !important; }
                        .power-direction-header { background-color: #D5E8EF !important; }
                        .power-market-title { background-color: #3D7890; color: white; padding: 5px; margin: 0; height: auto; font-size: 14px; }
                        .energy-table td { background-color: #E6F5EC; }
                        .energy-header { font-weight: bold; background-color: #D0EAD9 !important; }
                        .energy-direction-header { background-color: #DCF0E2 !important; }
                        .energy-market-title { background-color: #4D9D6A; color: white; padding: 5px; margin: 0; height: auto; font-size: 14px; }
                        .trading-table td { background-color: #EFF5D8; }
                        .trading-header { font-weight: bold; background-color: #E5ECC5 !important; }
                        .trading-direction-header { background-color: #EAEFCE !important; }
                        .trading-market-title { background-color: #8CB63C; color: white; padding: 5px; margin: 0; height: auto; font-size: 14px; }
                        .hydrogen-table td { background-color: #F0E6FF; }
                        .hydrogen-header { font-weight: bold; background-color: #E6D9FF !important; }
                        .hydrogen-market-title { background-color: #8A63D2; color: white; padding: 5px; margin: 0; height: auto; font-size: 14px; }
                        .row-compact { margin-bottom: 0px !important; padding: 0px !important; }
                        hr { margin: 5px 0 !important; }
                        </style>
                        """, unsafe_allow_html=True)

                        if "aggregated" in data and "markets" in data["aggregated"]:
                            markets_data = data["aggregated"]["markets"]

                            market_tabs_p2g = st.tabs([
                                "BALANSAVIMO PAJĖGUMŲ RINKA",
                                "BALANSAVIMO ENERGIJOS RINKA",
                                "ELEKTROS ENERGIJOS PREKYBA",
                                "VANDENILIO PREKYBA"
                            ])

                            # Tab 1: Power Balancing Market (P2G) - Same as other calculators
                            with market_tabs_p2g[0]:
                                if 'BALANSAVIMO_PAJEGUMU_RINKA' in markets_data:
                                    balansavimo_pajegumu_data = markets_data['BALANSAVIMO_PAJEGUMU_RINKA']

                                    # FCR section
                                    if 'FCR' in balansavimo_pajegumu_data:
                                        fcr_data = balansavimo_pajegumu_data['FCR']
                                        col1, col2 = st.columns([1, 5])
                                        with col1:
                                            st.markdown(
                                                f"""<div class="power-market-title"><h4 style="margin:0;">{fcr_data.get('header', 'FCR')}</h4><small>{fcr_data.get('description', 'FREQUENCY CONTAINMENT RESERVE')}</small></div>""",
                                                unsafe_allow_html=True)
                                        with col2:
                                            st.markdown(
                                                f"""<table class="market-table power-table"><tr><th class="power-header">{fcr_data.get('volume_of_procured_reserves', {}).get('header', 'VOLUME OF PROCURED RESERVES')}</th></tr><tr><td>{fcr_data.get('volume_of_procured_reserves', {}).get('value', 0):.2f} MW</td></tr></table>""" +
                                                f"""<table class="market-table power-table"><tr><th class="power-header">{fcr_data.get('utilisation', {}).get('header', 'UTILISATION (% OF TIME)')}</th></tr><tr><td>{fcr_data.get('utilisation', {}).get('value', 0.0):.2f} %</td></tr></table>""" +
                                                f"""<table class="market-table power-table"><tr><th class="power-header">{fcr_data.get('potential_revenue', {}).get('header', 'POTENTIAL REVENUE')}</th></tr><tr><td>{fcr_data.get('potential_revenue', {}).get('value', 0.0):.2f} tūkst. EUR</td></tr></table>""" +
                                                f"""<table class="market-table power-table"><tr><th class="power-header">{fcr_data.get('bids_selected', {}).get('header', '% OF BIDS SELECTED')}</th></tr><tr><td>{fcr_data.get('bids_selected', {}).get('value', 0.0):.2f} %</td></tr></table>""",
                                                unsafe_allow_html=True)
                                        st.markdown("<hr>", unsafe_allow_html=True)

                                    # aFRR section
                                    if 'aFRR' in balansavimo_pajegumu_data:
                                        afrr_data = balansavimo_pajegumu_data['aFRR']
                                        col1, col2 = st.columns([1, 5])
                                        with col1:
                                            st.markdown(
                                                f"""<div class="power-market-title"><h4 style="margin:0;">{afrr_data.get('header', 'aFRR')}</h4><small>{afrr_data.get('description', 'AUTOMATIC FREQUENCY RESTORATION RESERVE')}</small></div>""",
                                                unsafe_allow_html=True)
                                        with col2:
                                            st.markdown(
                                                f"""<table class="market-table power-table"><tr><th class="power-header" colspan="2">{afrr_data.get('volume_of_procured_reserves', {}).get('header', 'VOLUME OF PROCURED RESERVES')}</th></tr><tr><th class="power-direction-header">UPWARD</th><th class="power-direction-header">DOWNWARD</th></tr><tr><td>{afrr_data.get('volume_of_procured_reserves', {}).get('upward', {}).get('value', 0):.2f} MW</td><td>{afrr_data.get('volume_of_procured_reserves', {}).get('downward', {}).get('value', 0):.2f} MW</td></tr></table>""" +
                                                f"""<table class="market-table power-table"><tr><th class="power-header" colspan="2">{afrr_data.get('utilisation', {}).get('header', 'UTILISATION (% OF TIME)')}</th></tr><tr><th class="power-direction-header">UPWARD</th><th class="power-direction-header">DOWNWARD</th></tr><tr><td>{afrr_data.get('utilisation', {}).get('upward', {}).get('value', 0.0):.2f} %</td><td>{afrr_data.get('utilisation', {}).get('downward', {}).get('value', 0.0):.2f} %</td></tr></table>""" +
                                                f"""<table class="market-table power-table"><tr><th class="power-header" colspan="2">{afrr_data.get('potential_revenue', {}).get('header', 'POTENTIAL REVENUE')}</th></tr><tr><th class="power-direction-header">UPWARD</th><th class="power-direction-header">DOWNWARD</th></tr><tr><td>{afrr_data.get('potential_revenue', {}).get('upward', {}).get('value', 0.0):.2f} tūkst. EUR</td><td>{afrr_data.get('potential_revenue', {}).get('downward', {}).get('value', 0.0):.2f} tūkst. EUR</td></tr></table>""" +
                                                f"""<table class="market-table power-table"><tr><th class="power-header" colspan="2">{afrr_data.get('bids_selected', {}).get('header', '% OF BIDS SELECTED')}</th></tr><tr><th class="power-direction-header">UPWARD</th><th class="power-direction-header">DOWNWARD</th></tr><tr><td>{afrr_data.get('bids_selected', {}).get('upward', {}).get('value', 0.0):.2f} %</td><td>{afrr_data.get('bids_selected', {}).get('downward', {}).get('value', 0.0):.2f} %</td></tr></table>""",
                                                unsafe_allow_html=True)
                                        st.markdown("<hr>", unsafe_allow_html=True)

                                    # mFRR section
                                    if 'mFRR' in balansavimo_pajegumu_data:
                                        mfrr_data = balansavimo_pajegumu_data['mFRR']
                                        col1, col2 = st.columns([1, 5])
                                        with col1:
                                            st.markdown(
                                                f"""<div class="power-market-title"><h4 style="margin:0;">{mfrr_data.get('header', 'mFRR')}</h4><small>{mfrr_data.get('description', 'MANUAL FREQUENCY RESTORATION RESERVE')}</small></div>""",
                                                unsafe_allow_html=True)
                                        with col2:
                                            st.markdown(
                                                f"""<table class="market-table power-table"><tr><th class="power-header" colspan="2">{mfrr_data.get('volume_of_procured_reserves', {}).get('header', 'VOLUME OF PROCURED RESERVES')}</th></tr><tr><th class="power-direction-header">UPWARD</th><th class="power-direction-header">DOWNWARD</th></tr><tr><td>{mfrr_data.get('volume_of_procured_reserves', {}).get('upward', {}).get('value', 0):.2f} MW</td><td>{mfrr_data.get('volume_of_procured_reserves', {}).get('downward', {}).get('value', 0):.2f} MW</td></tr></table>""" +
                                                f"""<table class="market-table power-table"><tr><th class="power-header" colspan="2">{mfrr_data.get('utilisation', {}).get('header', 'UTILISATION (% OF TIME)')}</th></tr><tr><th class="power-direction-header">UPWARD</th><th class="power-direction-header">DOWNWARD</th></tr><tr><td>{mfrr_data.get('utilisation', {}).get('upward', {}).get('value', 0.0):.2f} %</td><td>{mfrr_data.get('utilisation', {}).get('downward', {}).get('value', 0.0):.2f} %</td></tr></table>""" +
                                                f"""<table class="market-table power-table"><tr><th class="power-header" colspan="2">{mfrr_data.get('potential_revenue', {}).get('header', 'POTENTIAL REVENUE')}</th></tr><tr><th class="power-direction-header">UPWARD</th><th class="power-direction-header">DOWNWARD</th></tr><tr><td>{mfrr_data.get('potential_revenue', {}).get('upward', {}).get('value', 0.0):.2f} tūkst. EUR</td><td>{mfrr_data.get('potential_revenue', {}).get('downward', {}).get('value', 0.0):.2f} tūkst. EUR</td></tr></table>""" +
                                                f"""<table class="market-table power-table"><tr><th class="power-header" colspan="2">{mfrr_data.get('bids_selected', {}).get('header', '% OF BIDS SELECTED')}</th></tr><tr><th class="power-direction-header">UPWARD</th><th class="power-direction-header">DOWNWARD</th></tr><tr><td>{mfrr_data.get('bids_selected', {}).get('upward', {}).get('value', 0.0):.2f} %</td><td>{mfrr_data.get('bids_selected', {}).get('downward', {}).get('value', 0.0):.2f} %</td></tr></table>""",
                                                unsafe_allow_html=True)
                                else:
                                    st.info("Balansavimo pajėgumų rinkos duomenų nėra.")

                            # Tab 2: Energy Balancing Market (P2G) - Same as other calculators
                            with market_tabs_p2g[1]:
                                if 'BALANSAVIMO_ENERGIJOS_RINKA' in markets_data:
                                    balansavimo_energijos_data = markets_data['BALANSAVIMO_ENERGIJOS_RINKA']

                                    # aFRR section
                                    if 'aFRR' in balansavimo_energijos_data:
                                        afrr_data = balansavimo_energijos_data['aFRR']
                                        col1, col2 = st.columns([1, 5])
                                        with col1:
                                            st.markdown(
                                                f"""<div class="energy-market-title"><h4 style="margin:0;">{afrr_data.get('header', 'aFRR')}</h4><small>{afrr_data.get('description', 'AUTOMATIC FREQUENCY RESTORATION RESERVE')}</small></div>""",
                                                unsafe_allow_html=True)
                                        with col2:
                                            st.markdown(
                                                f"""<table class="market-table energy-table"><tr><th class="energy-header" colspan="2">{afrr_data.get('volume_of_procured_energy', {}).get('header', 'VOLUME OF PROCURED ENERGY')}</th></tr><tr><th class="energy-direction-header">UPWARD</th><th class="energy-direction-header">DOWNWARD</th></tr><tr><td>{afrr_data.get('volume_of_procured_energy', {}).get('upward', {}).get('value', 0.0):.2f} GWh</td><td>{afrr_data.get('volume_of_procured_energy', {}).get('downward', {}).get('value', 0.0):.2f} GWh</td></tr></table>""" +
                                                f"""<table class="market-table energy-table"><tr><th class="energy-header" colspan="2">{afrr_data.get('utilisation', {}).get('header', 'UTILISATION (% OF TIME)')}</th></tr><tr><th class="energy-direction-header">UPWARD</th><th class="energy-direction-header">DOWNWARD</th></tr><tr><td>{afrr_data.get('utilisation', {}).get('upward', {}).get('value', 0.0):.2f} %</td><td>{afrr_data.get('utilisation', {}).get('downward', {}).get('value', 0.0):.2f} %</td></tr></table>""" +
                                                f"""<table class="market-table energy-table"><tr><th class="energy-header" colspan="2">{afrr_data.get('potential_revenue', {}).get('header', 'POTENTIAL REVENUE')}</th></tr><tr><th class="energy-direction-header">UPWARD</th><th class="energy-direction-header">DOWNWARD</th></tr><tr><td>{afrr_data.get('potential_revenue', {}).get('upward', {}).get('value', 0.0):.2f} tūkst. EUR</td><td>{afrr_data.get('potential_revenue', {}).get('downward', {}).get('value', 0.0):.2f} tūkst. EUR</td></tr></table>""" +
                                                f"""<table class="market-table energy-table"><tr><th class="energy-header" colspan="2">{afrr_data.get('bids_selected', {}).get('header', '% OF BIDS SELECTED')}</th></tr><tr><th class="energy-direction-header">UPWARD</th><th class="energy-direction-header">DOWNWARD</th></tr><tr><td>{afrr_data.get('bids_selected', {}).get('upward', {}).get('value', 0.0):.2f} %</td><td>{afrr_data.get('bids_selected', {}).get('downward', {}).get('value', 0.0):.2f} %</td></tr></table>""",
                                                unsafe_allow_html=True)
                                        st.markdown("<hr>", unsafe_allow_html=True)

                                    # mFRR section
                                    if 'mFRR' in balansavimo_energijos_data:
                                        mfrr_data = balansavimo_energijos_data['mFRR']
                                        col1, col2 = st.columns([1, 5])
                                        with col1:
                                            st.markdown(
                                                f"""<div class="energy-market-title"><h4 style="margin:0;">{mfrr_data.get('header', 'mFRR')}</h4><small>{mfrr_data.get('description', 'MANUAL FREQUENCY RESTORATION RESERVE')}</small></div>""",
                                                unsafe_allow_html=True)
                                        with col2:
                                            st.markdown(
                                                f"""<table class="market-table energy-table"><tr><th class="energy-header" colspan="2">{mfrr_data.get('volume_of_procured_energy', {}).get('header', 'VOLUME OF PROCURED ENERGY')}</th></tr><tr><th class="energy-direction-header">UPWARD</th><th class="energy-direction-header">DOWNWARD</th></tr><tr><td>{mfrr_data.get('volume_of_procured_energy', {}).get('upward', {}).get('value', 0.0):.2f} GWh</td><td>{mfrr_data.get('volume_of_procured_energy', {}).get('downward', {}).get('value', 0.0):.2f} GWh</td></tr></table>""" +
                                                f"""<table class="market-table energy-table"><tr><th class="energy-header" colspan="2">{mfrr_data.get('utilisation', {}).get('header', 'UTILISATION (% OF TIME)')}</th></tr><tr><th class="energy-direction-header">UPWARD</th><th class="energy-direction-header">DOWNWARD</th></tr><tr><td>{mfrr_data.get('utilisation', {}).get('upward', {}).get('value', 0.0):.2f} %</td><td>{mfrr_data.get('utilisation', {}).get('downward', {}).get('value', 0.0):.2f} %</td></tr></table>""" +
                                                f"""<table class="market-table energy-table"><tr><th class="energy-header" colspan="2">{mfrr_data.get('potential_revenue', {}).get('header', 'POTENTIAL REVENUE')}</th></tr><tr><th class="energy-direction-header">UPWARD</th><th class="energy-direction-header">DOWNWARD</th></tr><tr><td>{mfrr_data.get('potential_revenue', {}).get('upward', {}).get('value', 0.0):.2f} tūkst. EUR</td><td>{mfrr_data.get('potential_revenue', {}).get('downward', {}).get('value', 0.0):.2f} tūkst. EUR</td></tr></table>""" +
                                                f"""<table class="market-table energy-table"><tr><th class="energy-header" colspan="2">{mfrr_data.get('bids_selected', {}).get('header', '% OF BIDS SELECTED')}</th></tr><tr><th class="energy-direction-header">UPWARD</th><th class="energy-direction-header">DOWNWARD</th></tr><tr><td>{mfrr_data.get('bids_selected', {}).get('upward', {}).get('value', 0.0):.2f} %</td><td>{mfrr_data.get('bids_selected', {}).get('downward', {}).get('value', 0.0):.2f} %</td></tr></table>""",
                                                unsafe_allow_html=True)
                                else:
                                    st.info("Balansavimo energijos rinkos duomenų nėra.")

                            # Tab 3: Electricity Trading (P2G)
                            with market_tabs_p2g[2]:
                                if 'ELEKTROS_ENERGIJOS_PREKYBA' in markets_data:
                                    elektros_energijos_data = markets_data['ELEKTROS_ENERGIJOS_PREKYBA']

                                    # Day Ahead section
                                    if 'Day_Ahead' in elektros_energijos_data:
                                        day_ahead_data = elektros_energijos_data['Day_Ahead']
                                        col1, col2 = st.columns([1, 5])
                                        with col1:
                                            st.markdown(
                                                f"""<div class="trading-market-title"><h4 style="margin:0;">{day_ahead_data.get('header', 'Day Ahead')}</h4><small>{day_ahead_data.get('description', 'Electricity procurement for hydrogen production')}</small></div>""",
                                                unsafe_allow_html=True)
                                        with col2:
                                            voee = day_ahead_data.get('volume_of_energy_exchange', {})
                                            pot = day_ahead_data.get('percentage_of_time', {})
                                            pcr = day_ahead_data.get('potential_cost_revenue', {})

                                            st.markdown(
                                                f"""<table class="market-table trading-table"><tr><th class="trading-header">{voee.get('header', 'VOLUME')}</th></tr><tr><td>{voee.get('purchase', {}).get('value', 0.0):.2f} GWh</td></tr></table>""" +
                                                f"""<table class="market-table trading-table"><tr><th class="trading-header">{pot.get('header', '% OF TIME')}</th></tr><tr><td>{pot.get('purchase', {}).get('value', 0.0):.2f} %</td></tr></table>""" +
                                                f"""<table class="market-table trading-table"><tr><th class="trading-header">{pcr.get('header', 'COST')}</th></tr><tr><td>{pcr.get('cost', {}).get('value', 0.0):.2f} tūkst. EUR</td></tr></table>""",
                                                unsafe_allow_html=True)
                                else:
                                    st.info("Elektros energijos prekybos duomenų nėra.")

                            # Tab 4: Hydrogen Trading (P2G specific)
                            with market_tabs_p2g[3]:
                                if 'VANDENILIO_PREKYBA' in markets_data:
                                    vandenilio_data = markets_data['VANDENILIO_PREKYBA']

                                    if 'Hydrogen_Sales' in vandenilio_data:
                                        hydrogen_data = vandenilio_data['Hydrogen_Sales']
                                        col1, col2 = st.columns([1, 5])
                                        with col1:
                                            st.markdown(
                                                f"""<div class="hydrogen-market-title"><h4 style="margin:0;">{hydrogen_data.get('header', 'Hydrogen Sales')}</h4><small>{hydrogen_data.get('description', 'Revenue from selling produced hydrogen')}</small></div>""",
                                                unsafe_allow_html=True)
                                        with col2:
                                            vhs = hydrogen_data.get('volume_of_h2_sold', {})
                                            pcr = hydrogen_data.get('potential_cost_revenue', {})

                                            st.markdown(
                                                f"""<table class="market-table hydrogen-table"><tr><th class="hydrogen-header">{vhs.get('header', 'VOLUME SOLD')}</th></tr><tr><td>{vhs.get('value', 0.0):.2f} kg</td></tr></table>""" +
                                                f"""<table class="market-table hydrogen-table"><tr><th class="hydrogen-header">{pcr.get('header', 'REVENUE')}</th></tr><tr><td>{pcr.get('revenue', {}).get('value', 0.0):.2f} tūkst. EUR</td></tr></table>""",
                                                unsafe_allow_html=True)
                                else:
                                    st.info("Vandenilio prekybos duomenų nėra.")

                    with tab3:
                        st.subheader("ECONOMIC RESULTS BY PRODUCT")

                        if "aggregated" in data and "economic_results" in data["aggregated"]:
                            econ_data = data["aggregated"]["economic_results"]

                            st.write("##### REVENUE BY PRODUCT")
                            if "revenue_table" in econ_data and econ_data["revenue_table"]:
                                st.table(econ_data["revenue_table"])
                                fig_rev = px.bar(
                                    econ_data["revenue_table"], x="Product", y="Value (tūkst. EUR)",
                                    title="REVENUE BY PRODUCT"
                                )
                                fig_rev.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
                                st.plotly_chart(fig_rev, use_container_width=True)
                            else:
                                st.info("No revenue data available")

                            st.write("##### COST BY PRODUCT")
                            if "cost_table" in econ_data and econ_data["cost_table"]:
                                st.table(econ_data["cost_table"])
                                fig_cost = px.bar(
                                    econ_data["cost_table"], x="Product", y="Value (tūkst. EUR)",
                                    title="COST BY PRODUCT"
                                )
                                fig_cost.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
                                st.plotly_chart(fig_cost, use_container_width=True)
                            else:
                                st.info("No cost data available")

                            st.metric("TOTAL PROFIT", f"{econ_data.get('total_profit', 0):.2f} tūkst. EUR")

                            st.write("##### YEARLY RESULTS")
                            if "yearly_table" in econ_data and econ_data["yearly_table"]:
                                yearly_df = pd.DataFrame(econ_data["yearly_table"])
                                st.table(yearly_df)

                                if "YEAR" in yearly_df.columns and "NPV (tūkst. EUR)" in yearly_df.columns:
                                    fig_yearly_npv = px.line(
                                        yearly_df, x="YEAR", y="NPV (tūkst. EUR)", markers=True,
                                        title="NET PRESENT VALUE OVER TIME"
                                    )
                                    fig_yearly_npv.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
                                    st.plotly_chart(fig_yearly_npv, use_container_width=True)

                                # Check for SOH (State of Health) visualization specific to P2G
                                if "SOH (%)" in yearly_df.columns:
                                    fig_soh = px.line(
                                        yearly_df, x="YEAR", y="SOH (%)", markers=True,
                                        title="ELECTROLYZER STATE OF HEALTH OVER TIME"
                                    )
                                    fig_soh.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
                                    st.plotly_chart(fig_soh, use_container_width=True)

                                y_metrics = [col for col in
                                             ["CAPEX (tūkst. EUR)", "OPEX (tūkst. EUR)", "CF (tūkst. EUR)"] if
                                             col in yearly_df.columns]
                                if "YEAR" in yearly_df.columns and y_metrics:
                                    fig_yearly_metrics = px.bar(
                                        yearly_df, x="YEAR", y=y_metrics,
                                        title="YEARLY FINANCIAL METRICS", barmode="group"
                                    )
                                    st.plotly_chart(fig_yearly_metrics, use_container_width=True)
                            else:
                                st.info("No yearly results data available.")
                        else:
                            st.info("Economic results data not found.")
                else:
                    try:
                        error_data = response.json()
                        if "detail" in error_data:
                            st.error(f"Calculation failed: {error_data['detail']}")
                        else:
                            st.error(f"Request failed with status code: {response.status_code}")
                    except json.JSONDecodeError:
                        st.error(f"Request failed with status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"Error making request: {str(e)}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")

elif calculator_type == "DSR":
    st.header("DSR Demo")
    st.write("Fill in the form below to submit a request to the DSR API.")

    # Create form for DSR input parameters
    with st.form("dsr_input_form"):
        st.header("Input Parameters")

        # Provider and Sector selection
        col_provider, col_sector = st.columns(2)

        with col_provider:
            provider = st.radio("Provider", ["ESO", "Litgrid"], index=1, horizontal=True, key="dsr_provider")

        with col_sector:
            sector = st.radio("Sector", ["Paslaugų", "Energetikos", "Pramonės", "Telkėjas", "Kita"], index=2,
                              horizontal=True, key="dsr_sector")

        # Add regulation direction selector (same as P2H but without FCR)
        regulation_direction = st.radio(
            "Pasirinkite galimą teikti reguliavimo paslaugą:",
            ["Aukštyn", "Žemyn", "Į abi puses"],
            horizontal=True,
            key="dsr_regulation_direction"
        )

        # Create columns for a more compact layout
        col1, col2 = st.columns(2)

        with col1:
            # Device characteristics
            q_avg = st.number_input("Q_avg - Average power (MW)", min_value=0.0, value=10.0, step=0.1,
                                    key="dsr_q_avg")
            q_min = st.number_input("Q_min - Minimum power (MW)", min_value=0.0, value=5.0, step=0.1,
                                    key="dsr_q_min")
            q_max = st.number_input("Q_max - Maximum power (MW)", min_value=0.0, value=15.0, step=0.1,
                                    key="dsr_q_max")

            # Reaction time slider with fixed values (same as BEKS)
            reaction_time_labels = {
                30: "<=30s",
                300: "<=300s",
                750: "<=750s",
                1000: ">750s"
            }

            reaction_time = st.select_slider(
                "reaction_time (s)",
                options=[30, 300, 750, 1000],
                value=300,
                format_func=lambda x: reaction_time_labels[x],
                key="dsr_reaction_time"
            )

            t_shift = st.number_input("T_shift - Time shift for restoration (quarters)", min_value=1, value=1, step=1,
                                      key="dsr_t_shift")

        with col2:
            # Economic parameters
            capex = st.number_input("CAPEX (tūkst. EUR/MW)", min_value=0.0, value=150.0, step=10.0,
                                    key="dsr_capex")
            opex = st.number_input("OPEX (tūkst. EUR/MW/year)", min_value=0.0, value=10.0, step=1.0,
                                   key="dsr_opex")
            discount_rate = st.number_input("discount_rate (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1,
                                            key="dsr_discount_rate")
            number_of_years = st.number_input("number_of_years", min_value=1, value=10, step=1,
                                              key="dsr_number_of_years")

        # Restoration investment section
        st.subheader("Device Restoration Investment")
        restoration_investment_needed = st.checkbox("Include restoration investment in calculation", value=False,
                                                    key="dsr_restoration_needed")
        st.info("If checkbox above is checked, the restoration parameters below will be included in the calculation.")

        col3, col4 = st.columns(2)
        with col3:
            restoration_investment_percentage = st.number_input("Investment (% of CAPEX)", min_value=0.0,
                                                                max_value=100.0, value=25.0, step=1.0,
                                                                key="dsr_restoration_percentage")
        with col4:
            restoration_working_hours = st.number_input("Working hours until restoration", min_value=0,
                                                        value=45000, step=1000,
                                                        key="dsr_restoration_hours")

        # Optional hourly power profiles section
        st.subheader("Optional Hourly Power Profiles")

        # Checkbox to include hourly power in request
        use_hourly_power = st.checkbox("Use hourly power profile (check to include in request)", value=False,
                                       key="dsr_use_hourly_power")

        st.info(
            "Enter power consumption for each hour (0-23). If checkbox above is checked, all 24 values will be included in the request.")
        cols = st.columns(6)
        hourly_power = {}
        for h in range(24):
            col_idx = h % 6
            with cols[col_idx]:
                hourly_power[str(h)] = st.number_input(
                    f"Hour {h}",
                    min_value=0.0,
                    value=q_avg,
                    step=0.1,
                    key=f"dsr_hourly_power_{h}"
                )

        # Checkbox to include hourly min/max in request
        use_hourly_min_max = st.checkbox("Use hourly min/max power profiles (check to include in request)", value=False,
                                         key="dsr_use_hourly_min_max")

        st.info(
            "Enter minimum and maximum power for each hour. If checkbox above is checked, all 48 values will be included in the request.")

        # Min power inputs
        st.write("**Minimum Power (MW) by Hour:**")
        cols_min = st.columns(6)
        hourly_min_power = {}
        for h in range(24):
            col_idx = h % 6
            with cols_min[col_idx]:
                hourly_min_power[str(h)] = st.number_input(
                    f"Min Hour {h}",
                    min_value=0.0,
                    value=q_min,
                    step=0.1,
                    key=f"dsr_hourly_min_{h}"
                )

        # Max power inputs
        st.write("**Maximum Power (MW) by Hour:**")
        cols_max = st.columns(6)
        hourly_max_power = {}
        for h in range(24):
            col_idx = h % 6
            with cols_max[col_idx]:
                hourly_max_power[str(h)] = st.number_input(
                    f"Max Hour {h}",
                    min_value=0.0,
                    value=q_max,
                    step=0.1,
                    key=f"dsr_hourly_max_{h}"
                )

        # Price threshold sections (no FCR for DSR)
        st.subheader("Minimali siūloma kaina už balansavimo pajėgumus:")
        col6, col7, col8, col9 = st.columns(4)

        with col6:
            p_afrru_cap_bsp = st.number_input("aFRRu", min_value=0.0, value=0.0, step=1.0,
                                              key="dsr_afrru_cap_thresh")
        with col7:
            p_afrrd_cap_bsp = st.number_input("aFRRd", min_value=0.0, value=0.0, step=1.0,
                                              key="dsr_afrrd_cap_thresh")
        with col8:
            p_mfrru_cap_bsp = st.number_input("mFRRu", min_value=0.0, value=0.0, step=1.0,
                                              key="dsr_mfrru_cap_thresh")
        with col9:
            p_mfrrd_cap_bsp = st.number_input("mFRRd", min_value=0.0, value=0.0, step=1.0,
                                              key="dsr_mfrrd_cap_thresh")

        st.subheader("Minimali siūloma kaina už balansavimo energiją:")
        col10, col11, col12, col13 = st.columns(4)

        with col10:
            p_afrru_bsp = st.number_input("aFRRu", min_value=0.0, value=0.0, step=1.0,
                                          key="dsr_afrru_energy_thresh")
        with col11:
            p_afrrd_bsp = st.number_input("aFRRd", min_value=0.0, value=0.0, step=1.0,
                                          key="dsr_afrrd_energy_thresh")
        with col12:
            p_mfrru_bsp = st.number_input("mFRRu", min_value=0.0, value=0.0, step=1.0,
                                          key="dsr_mfrru_energy_thresh")
        with col13:
            p_mfrrd_bsp = st.number_input("mFRRd", min_value=0.0, value=0.0, step=1.0,
                                          key="dsr_mfrrd_energy_thresh")

        # Submit button
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        # Determine produktai based on regulation direction (no FCR for DSR)
        if regulation_direction == "Aukštyn":
            produktai = {"aFRRu": True, "aFRRd": False, "mFRRu": True, "mFRRd": False}
        elif regulation_direction == "Žemyn":
            produktai = {"aFRRu": False, "aFRRd": True, "mFRRu": False, "mFRRd": True}
        else:  # "Į abi puses"
            produktai = {"aFRRu": True, "aFRRd": True, "mFRRu": True, "mFRRd": True}

        # Create the request body
        request_body = {
            "Q_avg": q_avg,
            "Q_min": q_min,
            "Q_max": q_max,
            "reaction_time": reaction_time,
            "T_shift": t_shift,
            "CAPEX": capex,
            "OPEX": opex,
            "discount_rate": discount_rate,
            "number_of_years": number_of_years,
            "provider": provider,
            "Sector": sector,
            "P_aFRRu_CAP_BSP": p_afrru_cap_bsp,
            "P_aFRRd_CAP_BSP": p_afrrd_cap_bsp,
            "P_mFRRu_CAP_BSP": p_mfrru_cap_bsp,
            "P_mFRRd_CAP_BSP": p_mfrrd_cap_bsp,
            "P_aFRRu_BSP": p_afrru_bsp,
            "P_aFRRd_BSP": p_afrrd_bsp,
            "P_mFRRu_BSP": p_mfrru_bsp,
            "P_mFRRd_BSP": p_mfrrd_bsp,
            "produktai": produktai
        }

        # Only add restoration parameters if checkbox is checked
        if restoration_investment_needed:
            request_body["restoration_investment_needed"] = True
            request_body["restoration_investment_percentage"] = restoration_investment_percentage
            request_body["restoration_working_hours"] = restoration_working_hours
        else:
            request_body["restoration_investment_needed"] = False
            request_body["restoration_investment_percentage"] = 0.0
            request_body["restoration_working_hours"] = 0

        # Only add hourly profiles if checkboxes are checked
        if use_hourly_power:
            request_body["hourly_power"] = hourly_power

        if use_hourly_min_max:
            request_body["hourly_min_power"] = hourly_min_power
            request_body["hourly_max_power"] = hourly_max_power

        with st.expander("Request Body"):
            st.json(request_body)

        with st.spinner("Processing request..."):
            try:
                response = requests.post(f"{BE_URL}dsr", json=request_body)

                if response.status_code == 200:
                    data = response.json()
                    st.success("Request successful!")

                    # Display results in tabs (removed Performance tab)
                    tab1, tab2, tab3, tab4 = st.tabs(
                        ["Summary", "Markets", "Economic Results", "Comparison"])

                    with tab1:
                        if 'aggregated' in data and 'summary' in data['aggregated']:
                            summary = data['aggregated']['summary']

                            # Display yearly and project summary tables
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("#### YEARLY SUMMARY")
                                if 'yearly_summary_table' in summary:
                                    st.table(summary['yearly_summary_table'])

                            with col2:
                                st.write("#### PROJECT SUMMARY")
                                if 'project_summary_table' in summary:
                                    st.table(summary['project_summary_table'])

                            # Display charts
                            col1, col2 = st.columns(2)

                            with col1:
                                # NPV CHART
                                npv_data = summary.get('npv_chart_data', {})
                                if npv_data and all(key in npv_data for key in ['years', 'npv', 'dcfs']):
                                    fig_npv = make_subplots(specs=[[{"secondary_y": True}]])

                                    # Discounted Cash Flows
                                    fig_npv.add_trace(
                                        go.Bar(x=npv_data['years'], y=npv_data['dcfs'],
                                               name='Discounted Cash Flow',
                                               hovertemplate='%{y:,.2f}<extra></extra>'),
                                        secondary_y=False
                                    )

                                    # Cumulative NPV
                                    fig_npv.add_trace(
                                        go.Scatter(x=npv_data['years'], y=npv_data['npv'],
                                                   mode='lines+markers',
                                                   name='Cumulative NPV',
                                                   hovertemplate='%{y:,.2f}<extra></extra>'),
                                        secondary_y=True
                                    )

                                    # Add break-even point if available
                                    if npv_data.get('break_even_point') is not None:
                                        break_even_year = npv_data['years'][npv_data['break_even_point']]
                                        break_even_value = npv_data['npv'][npv_data['break_even_point']]
                                        fig_npv.add_scatter(
                                            x=[break_even_year],
                                            y=[break_even_value],
                                            mode="markers",
                                            marker=dict(size=10, color="green"),
                                            name="Break-even Point",
                                            secondary_y=True
                                        )

                                    fig_npv.update_xaxes(title_text="Year")
                                    fig_npv.update_yaxes(title_text="Discounted Cash Flow (tūkst. EUR)",
                                                         secondary_y=False)
                                    fig_npv.update_yaxes(title_text="Cumulative NPV (tūkst. EUR)",
                                                         secondary_y=True)
                                    fig_npv.update_layout(
                                        title="NET PRESENT VALUE ANALYSIS",
                                        hovermode='x unified'
                                    )

                                    st.plotly_chart(fig_npv, use_container_width=True)

                            with col2:
                                # REVENUE vs COST BY PRODUCTS CHART
                                rev_cost_data = summary.get('revenue_cost_chart_data', {})
                                if rev_cost_data and 'products' in rev_cost_data and 'values' in rev_cost_data:
                                    fig_rev_cost = px.bar(
                                        x=rev_cost_data['products'],
                                        y=rev_cost_data['values'],
                                        labels={"x": "Product", "y": "Value (tūkst. EUR)"},
                                        title="REVENUE vs COST BY PRODUCTS"
                                    )

                                    # Color code based on positive/negative values
                                    colors = ['red' if v < 0 else 'green' for v in rev_cost_data['values']]
                                    fig_rev_cost.update_traces(marker_color=colors,
                                                               hovertemplate='%{y:,.2f}<extra></extra>')

                                    st.plotly_chart(fig_rev_cost, use_container_width=True)

                            # Utilization chart
                            util_data = summary.get('utilisation_chart_data', {})
                            if util_data and 'products' in util_data and 'values' in util_data:
                                st.write("#### UTILISATION BY PRODUCT")
                                fig_util = px.bar(
                                    x=util_data['products'],
                                    y=util_data['values'],
                                    labels={"x": "Product", "y": "Utilisation (%)"},
                                    title="PRODUCT UTILISATION"
                                )
                                fig_util.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
                                st.plotly_chart(fig_util, use_container_width=True)

                    with tab2:
                        # Display markets information
                        if 'aggregated' in data and 'markets' in data['aggregated']:
                            markets = data['aggregated']['markets']

                            # Balansavimo Pajėgumų Rinka
                            if 'BALANSAVIMO_PAJEGUMU_RINKA' in markets:
                                st.write("### BALANSAVIMO PAJĖGUMŲ RINKA")
                                bpr = markets['BALANSAVIMO_PAJEGUMU_RINKA']

                                # Display only aFRR and mFRR (no FCR for DSR)
                                for service in ['aFRR', 'mFRR']:
                                    if service in bpr:
                                        with st.expander(f"{service} - {bpr[service]['description']}"):
                                            service_data = bpr[service]

                                            # Volume of procured reserves
                                            if 'volume_of_procured_reserves' in service_data:
                                                st.write("**VOLUME OF PROCURED RESERVES**")
                                                vol_data = service_data['volume_of_procured_reserves']
                                                if 'upward' in vol_data:
                                                    col1, col2 = st.columns(2)
                                                    with col1:
                                                        st.metric("Upward",
                                                                  f"{vol_data['upward']['value']} {vol_data['upward']['unit']}")
                                                    with col2:
                                                        st.metric("Downward",
                                                                  f"{vol_data['downward']['value']} {vol_data['downward']['unit']}")

                                            # Utilisation
                                            if 'utilisation' in service_data:
                                                st.write("**UTILISATION (% OF TIME)**")
                                                util_data = service_data['utilisation']
                                                if 'upward' in util_data:
                                                    col1, col2 = st.columns(2)
                                                    with col1:
                                                        st.metric("Upward",
                                                                  f"{util_data['upward']['value']} {util_data['upward']['unit']}")
                                                    with col2:
                                                        st.metric("Downward",
                                                                  f"{util_data['downward']['value']} {util_data['downward']['unit']}")

                                            # Potential revenue
                                            if 'potential_revenue' in service_data:
                                                st.write("**POTENTIAL REVENUE**")
                                                rev_data = service_data['potential_revenue']
                                                if 'upward' in rev_data:
                                                    col1, col2 = st.columns(2)
                                                    with col1:
                                                        st.metric("Upward",
                                                                  f"{rev_data['upward']['value']} {rev_data['upward']['unit']}")
                                                    with col2:
                                                        st.metric("Downward",
                                                                  f"{rev_data['downward']['value']} {rev_data['downward']['unit']}")

                            # Other markets
                            for market_key in ['BALANSAVIMO_ENERGIJOS_RINKA', 'INTROS_DIENOS_RINKA']:
                                if market_key in markets:
                                    market = markets[market_key]
                                    st.write(f"### {market_key.replace('_', ' ')}")

                                    if 'summary' in market:
                                        for key, value in market['summary'].items():
                                            st.metric(key, f"{value['value']} {value['unit']}")

                    with tab3:
                        # Display economic results
                        if 'aggregated' in data and 'economic_results' in data['aggregated']:
                            econ_data = data['aggregated']['economic_results']

                            # Display revenue table and chart
                            st.write("##### REVENUE BY PRODUCT")
                            if 'revenue_table' in econ_data and econ_data['revenue_table']:
                                st.table(econ_data['revenue_table'])

                                # Create graph from table data
                                fig_rev = px.bar(
                                    econ_data['revenue_table'],
                                    x="Product",
                                    y="Value (tūkst. EUR)",
                                    title="REVENUE BY PRODUCT"
                                )
                                fig_rev.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
                                st.plotly_chart(fig_rev, use_container_width=True)

                            # Display costs table and chart
                            st.write("##### COST BY PRODUCT")
                            if 'cost_table' in econ_data and econ_data['cost_table']:
                                st.table(econ_data['cost_table'])

                                # Create graph from table data
                                fig_cost = px.bar(
                                    econ_data['cost_table'],
                                    x="Product",
                                    y="Value (tūkst. EUR)",
                                    title="COST BY PRODUCT"
                                )
                                fig_cost.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
                                st.plotly_chart(fig_cost, use_container_width=True)

                            # Display total profit
                            if 'total_profit' in econ_data:
                                st.metric("TOTAL PROFIT", f"{econ_data['total_profit']:.2f} tūkst. EUR")

                            # Display yearly results table
                            st.write("##### YEARLY RESULTS")
                            if 'yearly_table' in econ_data:
                                st.table(econ_data['yearly_table'])

                                # Plot yearly NPV
                                yearly_df = pd.DataFrame(econ_data['yearly_table'])
                                if 'YEAR' in yearly_df.columns and 'NPV (tūkst. EUR)' in yearly_df.columns:
                                    fig_yearly_npv = px.line(
                                        yearly_df,
                                        x="YEAR",
                                        y="NPV (tūkst. EUR)",
                                        markers=True,
                                        title="NET PRESENT VALUE OVER TIME"
                                    )
                                    fig_yearly_npv.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
                                    st.plotly_chart(fig_yearly_npv, use_container_width=True)

                    with tab4:
                        # DSR-specific comparison section
                        if 'aggregated' in data and 'comparison' in data['aggregated']:
                            comparison = data['aggregated']['comparison']

                            st.write("### SAVINGS COMPARISON")
                            st.write("Comparison between baseline operation and optimized DSR operation")

                            # Check the actual structure of comparison data
                            if isinstance(comparison, dict):
                                # Create comparison metrics based on available keys
                                comparison_items = []

                                # Common keys to look for
                                baseline_keys = ['baseline', 'be DSR', 'tik katilas', 'without DSR']
                                optimized_keys = ['optimized', 'su DSR', 'with DSR', 'DSR']
                                savings_keys = ['DA sutaupoma', 'savings', 'profit', 'sutaupoma']

                                # Find baseline cost
                                baseline_cost = None
                                for key in baseline_keys:
                                    if key in comparison:
                                        baseline_cost = comparison[key]
                                        comparison_items.append(("Baseline Cost", baseline_cost,
                                                                 "Cost of operation without DSR optimization"))
                                        break

                                # Find optimized cost
                                optimized_cost = None
                                for key in optimized_keys:
                                    if key in comparison:
                                        optimized_cost = comparison[key]
                                        comparison_items.append(("Optimized Cost", optimized_cost,
                                                                 "Cost of operation with DSR optimization"))
                                        break

                                # Find savings
                                savings = None
                                for key in savings_keys:
                                    if key in comparison:
                                        savings = comparison[key]
                                        comparison_items.append(
                                            ("Savings", savings, "Savings from optimized scheduling"))
                                        break

                                # Display all other items in comparison
                                for key, value in comparison.items():
                                    if key not in baseline_keys + optimized_keys + savings_keys:
                                        comparison_items.append((key.replace('_', ' ').title(), value, f"{key} value"))

                                # Display metrics
                                if comparison_items:
                                    cols = st.columns(min(len(comparison_items), 3))
                                    for idx, (label, value, help_text) in enumerate(comparison_items[:3]):
                                        col_idx = idx % 3
                                        with cols[col_idx]:
                                            if "savings" in label.lower() or "sutaupoma" in label.lower():
                                                st.metric(label,
                                                          f"{abs(value):.2f} tūkst. EUR",
                                                          delta=f"{abs(value):.2f}",
                                                          delta_color="normal" if value >= 0 else "inverse",
                                                          help=help_text)
                                            else:
                                                st.metric(label,
                                                          f"{value:.2f} tūkst. EUR",
                                                          help=help_text)

                                    # If more than 3 items, display the rest
                                    if len(comparison_items) > 3:
                                        st.write("#### Additional Comparison Data")
                                        for label, value, help_text in comparison_items[3:]:
                                            st.metric(label, f"{value:.2f}", help=help_text)

                                # If we can calculate savings from baseline and optimized
                                if baseline_cost is not None and optimized_cost is not None and savings is None:
                                    calculated_savings = baseline_cost - optimized_cost
                                    st.metric("Calculated Savings",
                                              f"{abs(calculated_savings):.2f} tūkst. EUR",
                                              delta=f"{abs(calculated_savings):.2f}",
                                              delta_color="normal" if calculated_savings >= 0 else "inverse",
                                              help="Calculated from baseline minus optimized costs")

                                # Display raw comparison data in expander for debugging
                                with st.expander("Raw Comparison Data"):
                                    st.json(comparison)
                            else:
                                st.info("Comparison data structure is not as expected.")
                                st.write(f"Received type: {type(comparison)}")
                                st.write(f"Data: {comparison}")
                        else:
                            st.info("No comparison data available in the response.")

                else:
                    st.error(f"Request failed with status code: {response.status_code}")
                    st.text(response.text)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
