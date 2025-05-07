import streamlit as st
import requests
import json
import plotly.express as px

# Set page title and description
st.set_page_config(page_title="Energy Optimization", layout="wide")
st.title("Energy Optimization Tools")

# Create a selector for the calculator type
calculator_type = st.radio("Select Calculator", ["BEKS"], horizontal=True)

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
            reaction_time = st.select_slider(
                "reaction_time (s)",
                options=[30, 300, 750],
                value=300  # default value
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
                # response = requests.post("http://0.0.0.0:80/beks", json=request_body)

                 # Uncomment the line below to use Azure endpoint
                response = requests.post("https://p2x-container-app.wonderfulpebble-6684d847.westeurope.azurecontainerapps.io/beks", json=request_body)

                response.raise_for_status()  # Raise exception for 4XX/5XX status codes

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
                        fig_npv = px.line(
                            x=npv_data['years'],
                            y=npv_data['npv'],
                            markers=True,
                            labels={"x": "Year", "y": "NPV (tūkst. EUR)"},
                            title="NET PRESENT VALUE ANALYSIS"
                        )

                        # Highlight break-even point if exists
                        if npv_data['break_even_point'] is not None:
                            break_even_year = npv_data['years'][npv_data['break_even_point']]
                            break_even_value = npv_data['npv'][npv_data['break_even_point']]

                            fig_npv.add_scatter(
                                x=[break_even_year],
                                y=[break_even_value],
                                mode="markers",
                                marker=dict(size=10, color="red"),
                                name="Break-even Point"
                            )

                        fig_npv.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
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
                                        <td>{fcr_data['volume_of_procured_reserves']['value']} MW</td>
                                    </tr>
                                </table>

                                <table class="market-table power-table">
                                    <tr>
                                        <th class="power-header">{fcr_data['utilisation']['header']}</th>
                                    </tr>
                                    <tr>
                                        <td>{fcr_data['utilisation']['value']} %</td>
                                    </tr>
                                </table>

                                <table class="market-table power-table">
                                    <tr>
                                        <th class="power-header">{fcr_data['potential_revenue']['header']}</th>
                                    </tr>
                                    <tr>
                                        <td>{fcr_data['potential_revenue']['value']} EUR</td>
                                    </tr>
                                </table>

                                <table class="market-table power-table">
                                    <tr>
                                        <th class="power-header">{fcr_data['bids_selected']['header']}</th>
                                    </tr>
                                    <tr>
                                        <td>{fcr_data['bids_selected']['value']} %</td>
                                    </tr>
                                </table>
                                """,
                                unsafe_allow_html=True
                            )

                        # Add separator
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
                            # Create the aFRR table layout with ACTUAL VALUES
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
                                        <td>{afrr_data['volume_of_procured_reserves']['upward']['value']} MW</td>
                                        <td>{afrr_data['volume_of_procured_reserves']['downward']['value']} MW</td>
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
                                        <td>{afrr_data['utilisation']['upward']['value']} %</td>
                                        <td>{afrr_data['utilisation']['downward']['value']} %</td>
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
                                        <td>{afrr_data['potential_revenue']['upward']['value']} EUR</td>
                                        <td>{afrr_data['potential_revenue']['downward']['value']} EUR</td>
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
                                        <td>{afrr_data['bids_selected']['upward']['value']} %</td>
                                        <td>{afrr_data['bids_selected']['downward']['value']} %</td>
                                    </tr>
                                </table>
                                """,
                                unsafe_allow_html=True
                            )

                        # Add separator
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
                            # Create the mFRR table layout with ACTUAL VALUES
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
                                        <td>{mfrr_data['volume_of_procured_reserves']['upward']['value']} MW</td>
                                        <td>{mfrr_data['volume_of_procured_reserves']['downward']['value']} MW</td>
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
                                        <td>{mfrr_data['utilisation']['upward']['value']} %</td>
                                        <td>{mfrr_data['utilisation']['downward']['value']} %</td>
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
                                        <td>{mfrr_data['potential_revenue']['upward']['value']} EUR</td>
                                        <td>{mfrr_data['potential_revenue']['downward']['value']} EUR</td>
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
                                        <td>{mfrr_data['bids_selected']['upward']['value']} %</td>
                                        <td>{mfrr_data['bids_selected']['downward']['value']} %</td>
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
                            # Create the aFRR energy table layout with ACTUAL VALUES
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
                                        <td>{afrr_data['volume_of_procured_energy']['upward']['value']} MWh</td>
                                        <td>{afrr_data['volume_of_procured_energy']['downward']['value']} MWh</td>
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
                                        <td>{afrr_data['utilisation']['upward']['value']} %</td>
                                        <td>{afrr_data['utilisation']['downward']['value']} %</td>
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
                                        <td>{afrr_data['potential_revenue']['upward']['value']} EUR</td>
                                        <td>{afrr_data['potential_revenue']['downward']['value']} EUR</td>
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
                                        <td>{afrr_data['bids_selected']['upward']['value']} %</td>
                                        <td>{afrr_data['bids_selected']['downward']['value']} %</td>
                                    </tr>
                                </table>
                                """,
                                unsafe_allow_html=True
                            )

                        # Add separator
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
                            # Create the mFRR energy table layout with ACTUAL VALUES
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
                                        <td>{mfrr_data['volume_of_procured_energy']['upward']['value']} MWh</td>
                                        <td>{mfrr_data['volume_of_procured_energy']['downward']['value']} MWh</td>
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
                                        <td>{mfrr_data['utilisation']['upward']['value']} %</td>
                                        <td>{mfrr_data['utilisation']['downward']['value']} %</td>
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
                                        <td>{mfrr_data['potential_revenue']['upward']['value']} EUR</td>
                                        <td>{mfrr_data['potential_revenue']['downward']['value']} EUR</td>
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
                                        <td>{mfrr_data['bids_selected']['upward']['value']} %</td>
                                        <td>{mfrr_data['bids_selected']['downward']['value']} %</td>
                                    </tr>
                                </table>
                                """,
                                unsafe_allow_html=True
                            )

                    # Tab 3: Electricity Trading
                    with market_tabs[2]:
                        elektros_energijos_data = data['aggregated']['markets']['ELEKTROS_ENERGIJOS_PREKYBA']

                        # Day Ahead section
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
                            # Create the Day Ahead table layout with ACTUAL VALUES
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
                                        <td>{day_ahead_data['volume_of_energy_exchange']['purchase']['value']} MWh</td>
                                        <td>{day_ahead_data['volume_of_energy_exchange']['sale']['value']} MWh</td>
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
                                        <td>{day_ahead_data['percentage_of_time']['purchase']['value']} %</td>
                                        <td>{day_ahead_data['percentage_of_time']['sale']['value']} %</td>
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
                                        <td>{day_ahead_data['potential_cost_revenue']['cost']['value']} EUR</td>
                                        <td>{day_ahead_data['potential_cost_revenue']['revenue']['value']} EUR</td>
                                    </tr>
                                </table>
                                """,
                                unsafe_allow_html=True
                            )

                        # Add separator
                        st.markdown("<hr>", unsafe_allow_html=True)

                        # Intraday section
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
                            # Create the Intraday table layout with ACTUAL VALUES
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
                                        <td>{intraday_data['volume_of_energy_exchange']['purchase']['value']} MWh</td>
                                        <td>{intraday_data['volume_of_energy_exchange']['sale']['value']} MWh</td>
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
                                        <td>{intraday_data['percentage_of_time']['purchase']['value']} %</td>
                                        <td>{intraday_data['percentage_of_time']['sale']['value']} %</td>
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
                                        <td>{intraday_data['potential_cost_revenue']['cost']['value']} EUR</td>
                                        <td>{intraday_data['potential_cost_revenue']['revenue']['value']} EUR</td>
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
                    if econ_data['revenue_table']:
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
                    if econ_data['cost_table']:
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
                        y="NPV (tūkst. EUR)",
                        markers=True,
                        title="NET PRESENT VALUE OVER TIME"
                    )

                    fig_yearly_npv.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
                    st.plotly_chart(fig_yearly_npv, use_container_width=True)

            except requests.exceptions.RequestException as e:
                st.error(f"Error making request: {str(e)}")
            except json.JSONDecodeError:
                st.error("Error parsing response JSON")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
