import streamlit as st
import requests
import json
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd


def render_p2g_calculator(BE_URL, LOCAL_MODE, P2X_APIM_SECRET):
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
            p_afrru_bsp = st.number_input("aFRRu", value=0.0, step=1.0, key="p2g_afrru_energy")
        with col9:
            p_afrrd_bsp = st.number_input("aFRRd", value=0.0, step=1.0, key="p2g_afrrd_energy")
        with col10:
            p_mfrru_bsp = st.number_input("mFRRu", value=0.0, step=1.0, key="p2g_mfrru_energy")
        with col11:
            p_mfrrd_bsp = st.number_input("mFRRd", value=0.0, step=1.0, key="p2g_mfrrd_energy")

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
                # Build headers for local mode
                headers = {}
                if LOCAL_MODE:
                    headers["P2X-APIM-Secret"] = P2X_APIM_SECRET

                # response = requests.post(f"{BE_URL}p2g", json=request_body)
                response = requests.post(f"{BE_URL}p2g", data={"parameters": json.dumps(request_body)}, headers=headers)
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
                            yearly_summary_table = summary.get('yearly_summary_table', [])
                            # Format values with units
                            for row in yearly_summary_table:
                                if 'Value' in row and isinstance(row['Value'], (int, float)):
                                    value = row['Value']
                                    sign = "+" if value > 0 else ""
                                    row['Value'] = f"{sign}{value:.2f} tūkst. EUR/year"
                            st.table(yearly_summary_table)
                            st.write("##### PROJECT (LIFETIME) SUMMARY")
                            project_summary_table = summary.get('project_summary_table', [])
                            # Format values with units
                            for row in project_summary_table:
                                if 'Value' in row and isinstance(row['Value'], (int, float)):
                                    value = row['Value']
                                    sign = "+" if value > 0 else ""
                                    row['Value'] = f"{sign}{value:.2f} tūkst. EUR"
                            st.table(project_summary_table)
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
