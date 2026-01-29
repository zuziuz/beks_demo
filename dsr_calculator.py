import streamlit as st
import requests
import json
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd


def render_dsr_calculator(BE_URL, LOCAL_MODE, P2X_APIM_SECRET):
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
            p_afrru_bsp = st.number_input("aFRRu", value=0.0, step=1.0,
                                          key="dsr_afrru_energy_thresh")
        with col11:
            p_afrrd_bsp = st.number_input("aFRRd", value=0.0, step=1.0,
                                          key="dsr_afrrd_energy_thresh")
        with col12:
            p_mfrru_bsp = st.number_input("mFRRu", value=0.0, step=1.0,
                                          key="dsr_mfrru_energy_thresh")
        with col13:
            p_mfrrd_bsp = st.number_input("mFRRd", value=0.0, step=1.0,
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
                # Build headers for local mode
                headers = {}
                if LOCAL_MODE:
                    headers["P2X-APIM-Secret"] = P2X_APIM_SECRET

                # response = requests.post(f"{BE_URL}dsr", json=request_body)
                response = requests.post(f"{BE_URL}dsr", data={"parameters": json.dumps(request_body)}, headers=headers)

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
                                    yearly_summary_table = summary['yearly_summary_table']
                                    # Format values with units
                                    for row in yearly_summary_table:
                                        if 'Value' in row and isinstance(row['Value'], (int, float)):
                                            row['Value'] = f"{row['Value']:.2f} tūkst. EUR/year"
                                    st.table(yearly_summary_table)

                            with col2:
                                st.write("#### PROJECT SUMMARY")
                                if 'project_summary_table' in summary:
                                    project_summary_table = summary['project_summary_table']
                                    # Format values with units
                                    for row in project_summary_table:
                                        if 'Value' in row and isinstance(row['Value'], (int, float)):
                                            row['Value'] = f"{row['Value']:.2f} tūkst. EUR"
                                    st.table(project_summary_table)

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
                                # REVENUE vs COST BY PRODUCTS CHART - PROJECT LIFETIME
                                rev_cost_data = summary.get('revenue_cost_chart_data', {})
                                profit_data = summary.get('profit_breakdown_chart_data', {})
                                npv_data = summary.get('npv_chart_data', {})

                                if rev_cost_data and 'products' in rev_cost_data and 'values' in rev_cost_data:
                                    # Use annual values directly (consistent with BEKS and P2G)
                                    products = list(rev_cost_data['products'])
                                    values = list(rev_cost_data['values'])

                                    # Add Sutaupymai (DA savings) - annual value
                                    da_savings = profit_data.get('da_savings', 0)
                                    if abs(da_savings) > 0.01:
                                        products.append('Sutaupymai')
                                        values.append(da_savings)

                                    fig_rev_cost = px.bar(
                                        x=products,
                                        y=values,
                                        labels={"x": "Product", "y": "Value (tūkst. EUR)"},
                                        title="REVENUE vs COST BY PRODUCTS"
                                    )

                                    # Color code based on positive/negative values
                                    colors = ['red' if v < 0 else 'green' for v in values]
                                    fig_rev_cost.update_traces(marker_color=colors,
                                                               hovertemplate='%{y:,.2f}<extra></extra>')

                                    st.plotly_chart(fig_rev_cost, use_container_width=True)

                            # New profit breakdown chart and utilization chart
                            col1, col2 = st.columns(2)

                            with col1:
                                # Profit breakdown stacked chart - PROJECT LIFETIME
                                profit_data = summary.get('profit_breakdown_chart_data', {})
                                npv_data = summary.get('npv_chart_data', {})
                                if profit_data:
                                    # Get number of years from backend response
                                    number_of_years = len(npv_data.get('years', [])) - 1 if npv_data.get('years') else 1

                                    # Multiply by years for project lifetime (CAPEX and OPEX already project totals)
                                    da_savings_total = profit_data.get('da_savings', 0) * number_of_years
                                    balancing_revenue_total = profit_data.get('balancing_revenue', 0) * number_of_years
                                    capex = profit_data.get('capex', 0)
                                    opex = profit_data.get('opex', 0)

                                    fig_profit = go.Figure()

                                    # Positive values (revenue/savings) - green - above zero line
                                    fig_profit.add_trace(go.Bar(
                                        name='DA Sutaupymai',
                                        x=profit_data['categories'],
                                        y=[da_savings_total],
                                        marker_color='lightgreen',
                                        hovertemplate='%{y:,.2f} tūkst. EUR<extra></extra>',
                                        base=0
                                    ))

                                    fig_profit.add_trace(go.Bar(
                                        name='Pajamos iš balansavimo',
                                        x=profit_data['categories'],
                                        y=[balancing_revenue_total],
                                        marker_color='green',
                                        hovertemplate='%{y:,.2f} tūkst. EUR<extra></extra>',
                                        base=[da_savings_total]  # Stack on top of DA savings
                                    ))

                                    # Negative values (costs) - red - below zero line
                                    fig_profit.add_trace(go.Bar(
                                        name='CAPEX',
                                        x=profit_data['categories'],
                                        y=[-capex],  # Negative values
                                        marker_color='lightcoral',
                                        hovertemplate='%{y:,.2f} tūkst. EUR<extra></extra>',
                                        base=0
                                    ))

                                    fig_profit.add_trace(go.Bar(
                                        name='OPEX',
                                        x=profit_data['categories'],
                                        y=[-opex],  # Negative values
                                        marker_color='red',
                                        hovertemplate='%{y:,.2f} tūkst. EUR<extra></extra>',
                                        base=[-capex]  # Stack below CAPEX
                                    ))

                                    fig_profit.update_layout(
                                        title="PROJECT FINANCIAL BREAKDOWN",
                                        barmode='relative',  # Use relative mode for proper positive/negative separation
                                        yaxis_title="Value (tūkst. EUR)",
                                        yaxis=dict(zeroline=True, zerolinecolor='black', zerolinewidth=2),  # Show zero line
                                        showlegend=True
                                    )

                                    st.plotly_chart(fig_profit, use_container_width=True)

                            with col2:
                                # Utilization chart
                                util_data = summary.get('utilisation_chart_data', {})
                                if util_data and 'products' in util_data and 'values' in util_data:
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

                            # Balansavimo Energijos Rinka
                            if 'BALANSAVIMO_ENERGIJOS_RINKA' in markets:
                                st.write("### BALANSAVIMO ENERGIJOS RINKA")
                                ber = markets['BALANSAVIMO_ENERGIJOS_RINKA']

                                # Display aFRR and mFRR (same as power market but for energy)
                                for service in ['aFRR', 'mFRR']:
                                    if service in ber:
                                        with st.expander(f"{service} - {ber[service]['description']}"):
                                            service_data = ber[service]

                                            # Volume of procured energy
                                            if 'volume_of_procured_energy' in service_data:
                                                st.write("**VOLUME OF PROCURED ENERGY**")
                                                vol_data = service_data['volume_of_procured_energy']
                                                if 'upward' in vol_data:
                                                    col1, col2 = st.columns(2)
                                                    with col1:
                                                        st.metric("Upward",
                                                                  f"{vol_data['upward']['value']} {vol_data['upward']['unit'].strip()}")
                                                    with col2:
                                                        st.metric("Downward",
                                                                  f"{vol_data['downward']['value']} {vol_data['downward']['unit'].strip()}")

                                            # Utilisation
                                            if 'utilisation' in service_data:
                                                st.write("**UTILISATION (% OF TIME)**")
                                                util_data = service_data['utilisation']
                                                if 'upward' in util_data:
                                                    col1, col2 = st.columns(2)
                                                    with col1:
                                                        st.metric("Upward",
                                                                  f"{util_data['upward']['value']} {util_data['upward']['unit'].strip()}")
                                                    with col2:
                                                        st.metric("Downward",
                                                                  f"{util_data['downward']['value']} {util_data['downward']['unit'].strip()}")

                                            # Potential revenue
                                            if 'potential_revenue' in service_data:
                                                st.write("**POTENTIAL REVENUE**")
                                                rev_data = service_data['potential_revenue']
                                                if 'upward' in rev_data:
                                                    col1, col2 = st.columns(2)
                                                    with col1:
                                                        st.metric("Upward",
                                                                  f"{rev_data['upward']['value']} {rev_data['upward']['unit'].strip()}")
                                                    with col2:
                                                        st.metric("Downward",
                                                                  f"{rev_data['downward']['value']} {rev_data['downward']['unit'].strip()}")

                                            # Bids selected
                                            if 'bids_selected' in service_data:
                                                st.write("**% OF BIDS SELECTED**")
                                                bids_data = service_data['bids_selected']
                                                if 'upward' in bids_data:
                                                    col1, col2 = st.columns(2)
                                                    with col1:
                                                        st.metric("Upward",
                                                                  f"{bids_data['upward']['value']} {bids_data['upward']['unit'].strip()}")
                                                    with col2:
                                                        st.metric("Downward",
                                                                  f"{bids_data['downward']['value']} {bids_data['downward']['unit'].strip()}")

                            # Elektros Energijos Prekyba (Electricity Trading)
                            if 'ELEKTROS_ENERGIJOS_PREKYBA' in markets:
                                st.write("### ELEKTROS ENERGIJOS PREKYBA")
                                eep = markets['ELEKTROS_ENERGIJOS_PREKYBA']

                                # Day Ahead Market
                                if 'Day_Ahead' in eep:
                                    with st.expander(f"Day Ahead - {eep['Day_Ahead']['description']}"):
                                        da_data = eep['Day_Ahead']

                                        # Volume of energy exchange
                                        if 'volume_of_energy_exchange' in da_data:
                                            st.write("**VOLUME OF ENERGY EXCHANGE**")
                                            vol_data = da_data['volume_of_energy_exchange']
                                            if 'purchase' in vol_data:
                                                st.metric("Purchase",
                                                          f"{vol_data['purchase']['value']} {vol_data['purchase']['unit']}")

                                        # Percentage of time
                                        if 'percentage_of_time' in da_data:
                                            st.write("**% OF TIME**")
                                            time_data = da_data['percentage_of_time']
                                            if 'purchase' in time_data:
                                                st.metric("Purchase",
                                                          f"{time_data['purchase']['value']} {time_data['purchase']['unit']}")

                                        # Potential cost
                                        if 'potential_cost_revenue' in da_data:
                                            st.write("**POTENTIAL COST**")
                                            cost_data = da_data['potential_cost_revenue']
                                            if 'cost' in cost_data:
                                                st.metric("Cost",
                                                          f"{cost_data['cost']['value']} {cost_data['cost']['unit']}")

                                # Intraday Market
                                if 'Intraday' in eep:
                                    with st.expander(f"Intraday - {eep['Intraday']['description']}"):
                                        id_data = eep['Intraday']

                                        # Volume of energy exchange
                                        if 'volume_of_energy_exchange' in id_data:
                                            st.write("**VOLUME OF ENERGY EXCHANGE**")
                                            vol_data = id_data['volume_of_energy_exchange']
                                            if 'purchase' in vol_data and 'sale' in vol_data:
                                                col1, col2 = st.columns(2)
                                                with col1:
                                                    st.metric("Purchase",
                                                              f"{vol_data['purchase']['value']} {vol_data['purchase']['unit']}")
                                                with col2:
                                                    st.metric("Sale",
                                                              f"{vol_data['sale']['value']} {vol_data['sale']['unit']}")

                                        # Percentage of time
                                        if 'percentage_of_time' in id_data:
                                            st.write("**% OF TIME**")
                                            time_data = id_data['percentage_of_time']
                                            if 'purchase' in time_data and 'sale' in time_data:
                                                col1, col2 = st.columns(2)
                                                with col1:
                                                    st.metric("Purchase",
                                                              f"{time_data['purchase']['value']} {time_data['purchase']['unit']}")
                                                with col2:
                                                    st.metric("Sale",
                                                              f"{time_data['sale']['value']} {time_data['sale']['unit']}")

                                        # Potential cost & revenue
                                        if 'potential_cost_revenue' in id_data:
                                            st.write("**POTENTIAL COST & REVENUE**")
                                            cost_rev_data = id_data['potential_cost_revenue']
                                            if 'cost' in cost_rev_data and 'revenue' in cost_rev_data:
                                                col1, col2 = st.columns(2)
                                                with col1:
                                                    st.metric("Cost",
                                                              f"{cost_rev_data['cost']['value']} {cost_rev_data['cost']['unit']}")
                                                with col2:
                                                    st.metric("Revenue",
                                                              f"{cost_rev_data['revenue']['value']} {cost_rev_data['revenue']['unit']}")

                    with tab3:
                        # Display economic results
                        if 'aggregated' in data and 'economic_results' in data['aggregated']:
                            econ_data = data['aggregated']['economic_results']

                            # GROSS REVENUE BY PRODUCT (green bar chart)
                            st.write("##### GROSS REVENUE BY PRODUCT")
                            gross_revenue_data = econ_data.get('gross_revenue_by_product', [])
                            if gross_revenue_data:
                                st.table(gross_revenue_data)
                                fig_rev = px.bar(
                                    gross_revenue_data,
                                    x="Product",
                                    y="Value (tūkst. EUR)",
                                    title="GROSS REVENUE BY PRODUCT",
                                    color_discrete_sequence=['#2ecc71']  # Green
                                )
                                fig_rev.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
                                st.plotly_chart(fig_rev, use_container_width=True)
                            else:
                                st.info("No gross revenue data available")

                            # VARIABLE COSTS BY PRODUCT (red bar chart)
                            st.write("##### VARIABLE COSTS BY PRODUCT")
                            variable_costs_data = econ_data.get('variable_costs_by_product', [])
                            if variable_costs_data:
                                st.table(variable_costs_data)
                                fig_var = px.bar(
                                    variable_costs_data,
                                    x="Product",
                                    y="Value (tūkst. EUR)",
                                    title="VARIABLE COSTS BY PRODUCT",
                                    color_discrete_sequence=['#e74c3c']  # Red
                                )
                                fig_var.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
                                st.plotly_chart(fig_var, use_container_width=True)
                            else:
                                st.info("No variable costs data available")

                            # YEARLY RESULTS (table + NPV line chart)
                            st.write("##### YEARLY RESULTS")
                            if "yearly_table" in econ_data and econ_data["yearly_table"]:
                                st.table(econ_data["yearly_table"])

                                yearly_df = pd.DataFrame(econ_data["yearly_table"])
                                if "YEAR" in yearly_df.columns and "NPV (tūkst. EUR)" in yearly_df.columns:
                                    fig_yearly_npv = px.line(
                                        yearly_df, x="YEAR", y="NPV (tūkst. EUR)", markers=True,
                                        title="NET PRESENT VALUE OVER TIME"
                                    )
                                    fig_yearly_npv.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
                                    st.plotly_chart(fig_yearly_npv, use_container_width=True)
                            else:
                                st.info("No yearly results data available.")
                        else:
                            st.info("Economic results data not available.")

                    with tab4:
                        # DSR-specific comparison section
                        if 'aggregated' in data and 'comparison' in data['aggregated']:
                            comparison = data['aggregated']['comparison']

                            st.write("### DSR SAVINGS COMPARISON")
                            st.write("Comparison between baseline operation and optimized DSR operation")

                            # Display updated comparison metrics
                            if isinstance(comparison, dict):
                                # Get additional data
                                summary = data['aggregated'].get('summary', {})
                                profit_data = summary.get('profit_breakdown_chart_data', {})
                                chart_data = comparison.get('comparison_chart_data', {})

                                da_savings = profit_data.get('da_savings', 0)
                                balancing_revenue = chart_data.get('balancing_revenue', 0)

                                # Row 1: 3 metrics
                                row1_cols = st.columns(3)

                                # Baseline Cost (No DSR)
                                if 'be DSR' in comparison:
                                    baseline_data = comparison['be DSR']
                                    with row1_cols[0]:
                                        st.metric(
                                            baseline_data.get('label', 'Baseline Cost (No DSR)'),
                                            f"{baseline_data['value']:.2f} tūkst. EUR",
                                            help="Cost of operation without DSR optimization"
                                        )

                                # Optimized Cost (With DSR)
                                if 'su DSR' in comparison and 'comparison_chart_data' in comparison:
                                    optimized_data = comparison['su DSR']
                                    optimized_cost = chart_data['optimized_cost']
                                    with row1_cols[1]:
                                        st.metric(
                                            optimized_data.get('label', 'Optimized Cost (With DSR)'),
                                            f"{optimized_cost:.2f} tūkst. EUR",
                                            help="Cost with DSR optimization"
                                        )

                                # DA Sutaupymai
                                with row1_cols[2]:
                                    st.metric(
                                        "DA Sutaupymai",
                                        f"{da_savings:.2f} tūkst. EUR",
                                        help="Savings from DA market optimization"
                                    )

                                # Row 2: 2 metrics
                                row2_cols = st.columns(2)

                                # Pajamos iš balansavimo
                                with row2_cols[0]:
                                    st.metric(
                                        "Pajamos iš balansavimo",
                                        f"{balancing_revenue:.2f} tūkst. EUR",
                                        help="Revenue from balancing market participation"
                                    )

                                # Nauda iš DSR (total benefit)
                                if 'skirtumas' in comparison:
                                    benefit_data = comparison['skirtumas']
                                    with row2_cols[1]:
                                        value = benefit_data['value']
                                        st.metric(
                                            "Nauda iš DSR",
                                            f"{abs(value):.2f} tūkst. EUR",
                                            delta=f"{abs(value):.2f}",
                                            delta_color="normal" if value >= 0 else "inverse",
                                            help="Total benefit: DA Savings + Balancing Revenue"
                                        )

                                # Comparison chart
                                if 'comparison_chart_data' in comparison:
                                    st.write("#### COST COMPARISON BREAKDOWN")
                                    chart_data = comparison['comparison_chart_data']

                                    fig_comparison = go.Figure()

                                    # Baseline cost (negative, red)
                                    fig_comparison.add_trace(go.Bar(
                                        name='Neoptimizuotas energijos vartojimas',
                                        x=[chart_data['categories'][0]],
                                        y=[chart_data['baseline_cost']],  # Already negative from backend
                                        marker_color='red',
                                        hovertemplate='%{y:,.2f} tūkst. EUR<extra></extra>'
                                    ))

                                    # Optimized cost (negative, red)
                                    fig_comparison.add_trace(go.Bar(
                                        name='Optimizuotas energijos vartojimas',
                                        x=[chart_data['categories'][1]],
                                        y=[chart_data['optimized_cost']],  # Already negative from backend
                                        marker_color='lightcoral',
                                        hovertemplate='%{y:,.2f} tūkst. EUR<extra></extra>'
                                    ))

                                    # Balancing revenue (positive, green)
                                    fig_comparison.add_trace(go.Bar(
                                        name='Pajamos iš balansavimo energijos rinkų',
                                        x=[chart_data['categories'][1]],
                                        y=[chart_data['balancing_revenue']],  # Positive value
                                        marker_color='green',
                                        hovertemplate='%{y:,.2f} tūkst. EUR<extra></extra>'
                                    ))

                                    fig_comparison.update_layout(
                                        title="BASELINE vs DSR COST COMPARISON",
                                        barmode='relative',  # Use relative mode for proper negative/positive display
                                        yaxis_title="Cost/Revenue (tūkst. EUR)",
                                        yaxis=dict(zeroline=True, zerolinecolor='black', zerolinewidth=2),  # Show zero line
                                        showlegend=True
                                    )

                                    st.plotly_chart(fig_comparison, use_container_width=True)

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
