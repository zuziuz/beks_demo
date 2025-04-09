import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px

# Set page title and description
st.set_page_config(page_title="Energy Optimization", layout="wide")
st.title("Energy Optimization Tools")

# Create a selector for the calculator type
calculator_type = st.radio("Select Calculator", ["BEKS", "P2H"], horizontal=True)

if calculator_type == "BEKS":
    st.header("BEKS Demo")
    st.write("Fill in the form below to submit a request to the BEKS API.")

    # Create form for input parameters
    with st.form("beks_input_form"):
        st.header("Input Parameters")

        # Create columns for a more compact layout
        col1, col2 = st.columns(2)

        with col1:
            rte = st.number_input("RTE (%)", min_value=0.0, max_value=100.0, value=88.0, step=1.0)
            q_max = st.number_input("Q_max (MWh)", min_value=0.0, value=1.0, step=0.1)
            q_total = st.number_input("Q_total (MWh)", min_value=0.0, value=2.0, step=0.1)
            soc_min = st.number_input("SOC_min (%)", min_value=0.0, max_value=100.0, value=10.0, step=1.0)
            soc_max = st.number_input("SOC_max (%)", min_value=0.0, max_value=100.0, value=95.0, step=1.0)
            n_cycles_da = st.number_input("N_cycles_DA (kartai/d.)", min_value=0, value=1, step=1)
            n_cycles_id = st.number_input("N_cycles_ID (kartai/d.)", min_value=0, value=4, step=1)

        with col2:
            startup_time = st.number_input("startup_time (s)", min_value=0, value=1, step=1)
            delay = st.number_input("delay (s)", min_value=0, value=0, step=1)
            capex_p = st.number_input("CAPEX_P (tūkst. EUR/MW)", min_value=0.0, value=1000.0, step=10.0)
            capex_c = st.number_input("CAPEX_C (tūkst. Eur/MWh)", min_value=0.0, value=500.0, step=10.0)
            opex_p = st.number_input("OPEX_P (tūkst. Eur/MW/m)", min_value=0.0, value=2.52, step=0.1)
            opex_c = st.number_input("OPEX_C (tūkst. Eur/MWh)", min_value=0.0, value=0.5125, step=0.1)
            discount_rate = st.number_input("discount_rate (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1)
            number_of_years = st.number_input("number_of_years", min_value=1, value=10, step=1)

        # Create a section for produktai
        st.subheader("Produktai")
        col3, col4 = st.columns(2)

        with col3:
            fcr = st.checkbox("FCR", value=True)
            afrrd = st.checkbox("aFRRd", value=True)
            afrru = st.checkbox("aFRRu", value=True)

        with col4:
            mfrrd = st.checkbox("mFRRd", value=True)
            mfrru = st.checkbox("mFRRu", value=True)

        # Submit button
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        # Create the request body
        request_body = {
            "RTE": rte,
            "Q_max": q_max,
            "Q_total": q_total,
            "SOC_min": soc_min,
            "SOC_max": soc_max,
            "N_cycles_DA": n_cycles_da,
            "N_cycles_ID": n_cycles_id,
            "startup_time": startup_time,
            "delay": delay,
            "CAPEX_P": capex_p,
            "CAPEX_C": capex_c,
            "OPEX_P": opex_p,
            "OPEX_C": opex_c,
            "discount_rate": discount_rate,
            "number_of_years": number_of_years,
            "produktai": {
                "FCR": "True" if fcr else "False",
                "aFRRd": "True" if afrrd else "False",
                "aFRRu": "True" if afrru else "False",
                "mFRRd": "True" if mfrrd else "False",
                "mFRRu": "True" if mfrru else "False"
            }
        }

        # Display the request body
        with st.expander("Request Body"):
            st.json(request_body)

        # Make the POST request
        with st.spinner("Processing request..."):
            try:
                # response = requests.post("http://0.0.0.0:80/beks", json=request_body)
                response = requests.post("https://epsogapitest.orangebush-c16de4cd.westeurope.azurecontainerapps.io/beks", json=request_body)

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

                # Convert raw data to DataFrame for visualization
                raw_data = pd.DataFrame(data["raw"])

                # Convert datetime column
                raw_data["dt"] = pd.to_datetime(raw_data["dt"])
                raw_data = raw_data.sort_values(by="dt")
                # Visualization section
                st.header("Visualization")

                # Create tabs for different visualizations
                tab1, tab2 = st.tabs(["Optimization", "Economics"])

                with tab1:
                    st.subheader("Optimization Results")

                    # Create subtabs for different optimization result categories
                    opt_tab1, opt_tab2 = st.tabs(["State of Charge", "Buy/Sell Decisions"])

                    with opt_tab1:
                        soc_cols = [col for col in raw_data.columns if "SOC" in col]
                        if soc_cols:
                            fig = px.line(raw_data, x="dt", y=soc_cols,
                                          labels={"value": "State of Charge", "dt": "Date", "variable": "Metric"},
                                          title="State of Charge")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No state of charge data available")

                    with opt_tab2:
                        buy_sell_cols = [col for col in raw_data.columns if "_Q_" in col
                                         and ("BUY" in col or "SELL" in col)]
                        if buy_sell_cols:
                            fig = px.line(raw_data, x="dt", y=buy_sell_cols,
                                          labels={"value": "Quantity (MWh)", "dt": "Date", "variable": "Metric"},
                                          title="Buy/Sell Decisions")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No buy/sell decision data available")

                with tab2:
                    st.subheader("Economic Analysis")

                    # Display the aggregated data
                    if "aggregated" in data:
                        # Create a summary dashboard with aggregated visualizations
                        st.subheader("Summary Dashboard")

                        # Create a layout for the dashboard
                        col1, col2 = st.columns(2)

                        # 1. Energy Chart (Energija)
                        with col1:
                            if "total_energy" in data["aggregated"]:
                                energy_data = data["aggregated"]["total_energy"]
                                energy_df = pd.DataFrame({
                                    "Category": list(energy_data.keys()),
                                    "Value (GWh)": list(energy_data.values())
                                })

                                fig = px.bar(energy_df, x="Category", y="Value (GWh)",
                                             title="Energija (GWh)",
                                             labels={"Value (GWh)": "GWh", "Category": ""})
                                fig.update_layout(height=300)
                                # Allow scientific notation on axis but show full number on hover
                                fig.update_yaxes(exponentformat="power")
                                fig.update_traces(hovertemplate='%{y:,.8f}<extra></extra>')
                                st.plotly_chart(fig, use_container_width=True)

                        # 2. Power Chart (Galia)
                        with col2:
                            if "average_power" in data["aggregated"]:
                                power_data = data["aggregated"]["average_power"]
                                power_df = pd.DataFrame({
                                    "Category": list(power_data.keys()),
                                    "Value (MW)": list(power_data.values())
                                })

                                fig = px.bar(power_df, x="Category", y="Value (MW)",
                                             title="Galia (MW)",
                                             labels={"Value (MW)": "MW", "Category": ""})
                                fig.update_layout(height=300)
                                # Allow scientific notation on axis but show full number on hover
                                fig.update_yaxes(exponentformat="power")
                                fig.update_traces(hovertemplate='%{y:,.8f}<extra></extra>')
                                st.plotly_chart(fig, use_container_width=True)

                        # 3. Time Chart (Laikas)
                        with col1:
                            if "total_time" in data["aggregated"]:
                                time_data = data["aggregated"]["total_time"]
                                time_df = pd.DataFrame({
                                    "Category": list(time_data.keys()),
                                    "Value (%)": list(time_data.values())
                                })

                                fig = px.bar(time_df, x="Category", y="Value (%)",
                                             title="Laikas (%)",
                                             labels={"Value (%)": "%", "Category": ""})
                                fig.update_layout(height=300)
                                # Allow scientific notation on axis but show full number on hover
                                fig.update_yaxes(exponentformat="power")
                                fig.update_traces(hovertemplate='%{y:,.8f}<extra></extra>')
                                st.plotly_chart(fig, use_container_width=True)

                        # 4. Revenue/Expenses Chart (Pajamos(+)/išlaidos(-))
                        with col2:
                            if "total_finance" in data["aggregated"]:
                                finance_data = data["aggregated"]["total_finance"]
                                finance_df = pd.DataFrame({
                                    "Category": list(finance_data.keys()),
                                    "Value (mln. Eur)": [value / 1000000 for value in finance_data.values()]
                                    # Convert to millions
                                })

                                fig = px.bar(finance_df, x="Category", y="Value (mln. Eur)",
                                             title="Pajamos(+)/išlaidos(-) (mln. Eur)",
                                             labels={"Value (mln. Eur)": "mln. Eur", "Category": ""})
                                fig.update_layout(height=300)
                                # Allow scientific notation on axis but show full number on hover
                                fig.update_yaxes(exponentformat="power")
                                fig.update_traces(hovertemplate='%{y:,.8f}<extra></extra>')
                                st.plotly_chart(fig, use_container_width=True)

                        # 5. Total Revenue/Expenses (Suminės pajamos(+)/išlaidos(-))
                        with col1:
                            if "comparison" in data["aggregated"] and "BEKS" in data["aggregated"]["comparison"]:
                                beks_value = data["aggregated"]["comparison"]["BEKS"]
                                beks_df = pd.DataFrame({
                                    "Category": ["BEKS"],
                                    "Value (mln. Eur)": [beks_value / 1000000]  # Convert to millions
                                })

                                fig = px.bar(beks_df, x="Category", y="Value (mln. Eur)",
                                             title="Suminės pajamos(+)/išlaidos(-) (mln. Eur)",
                                             labels={"Value (mln. Eur)": "mln. Eur", "Category": ""})
                                fig.update_layout(height=300)
                                # Allow scientific notation on axis but show full number on hover
                                fig.update_yaxes(exponentformat="power")
                                fig.update_traces(hovertemplate='%{y:,.8f}<extra></extra>')
                                st.plotly_chart(fig, use_container_width=True)

                        # 6. Discounted Payback Chart (Diskontuoto atsipirkimo grafikas)
                        with col2:
                            if "yearly" in data["aggregated"]:
                                yearly_data = pd.DataFrame(data["aggregated"]["yearly"])

                                fig = px.bar(yearly_data, x="YEAR", y="NPV",
                                             title="Diskontuoto atsipirkimo grafikas",
                                             labels={"NPV": "mln. Eur", "YEAR": ""})
                                fig.update_layout(height=300)
                                # Allow scientific notation on axis but show full number on hover
                                fig.update_yaxes(exponentformat="power")
                                fig.update_traces(hovertemplate='%{y:,.8f}<extra></extra>')
                                st.plotly_chart(fig, use_container_width=True)

                        # Additional detailed data in expanders
                        st.subheader("Detailed Analysis")
                        for category, values in data["aggregated"].items():
                            if category != "yearly":  # Handle yearly data separately
                                with st.expander(f"{category.replace('_', ' ').title()}"):
                                    # Convert to DataFrame for better display
                                    if isinstance(values, dict):
                                        df = pd.DataFrame(values.items(), columns=["Metric", "Value"])
                                        st.dataframe(df, use_container_width=True)
                                    elif isinstance(values, list):
                                        df = pd.DataFrame(values)
                                        st.dataframe(df, use_container_width=True)
                                    else:
                                        st.write(values)

                        # Create a special visualization for yearly data if available
                        if "yearly" in data["aggregated"]:
                            yearly_data = pd.DataFrame(data["aggregated"]["yearly"])

                            with st.expander("Yearly Results", expanded=True):
                                st.dataframe(yearly_data, use_container_width=True)

                                # Plot NPV over years
                                fig = px.line(yearly_data, x="YEAR", y="NPV", markers=True,
                                              labels={"NPV": "Net Present Value (EUR)", "YEAR": "Year"},
                                              title="Net Present Value Over Time")
                                # Allow scientific notation on axis but show full number on hover
                                fig.update_yaxes(exponentformat="power")
                                fig.update_traces(hovertemplate='%{y:,.8f}<extra></extra>')
                                st.plotly_chart(fig, use_container_width=True)

                                # Plot other yearly metrics
                                metrics = ["CYCLES", "SOH", "CAPEX", "OPEX", "CF"]
                                metrics = [m for m in metrics if m in yearly_data.columns]

                                if metrics:
                                    fig = px.line(yearly_data, x="YEAR", y=metrics, markers=True,
                                                  labels={"value": "Value", "YEAR": "Year", "variable": "Metric"},
                                                  title="Yearly Metrics")
                                    # Allow scientific notation on axis but show full number on hover
                                    fig.update_yaxes(exponentformat="power")
                                    fig.update_traces(hovertemplate='%{y:,.8f}<extra></extra>')
                                    st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No aggregated data available")

                # Add a section to view raw data
                with st.expander("Raw Data"):
                    st.dataframe(raw_data, use_container_width=True)

            except requests.exceptions.RequestException as e:
                st.error(f"Error making request: {str(e)}")
            except json.JSONDecodeError:
                st.error("Error parsing response JSON")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")

elif calculator_type == "P2H":
    st.header("P2H Demo")
    st.write("Fill in the form below to submit a request to the P2H API.")

    # Create form for P2H input parameters
    with st.form("p2h_input_form"):
        st.header("Input Parameters")

        # Create columns for a more compact layout
        col1, col2 = st.columns(2)

        with col1:
            q_max_hp = st.number_input("Q_max_HP (MW)", min_value=0.0, value=2.0, step=0.1)
            startup_time_hp = st.number_input("startup_time_HP (s)", min_value=0, value=300, step=10)
            delay_hp = st.number_input("delay_HP (s)", min_value=0, value=30, step=1)
            t_hp = st.number_input("T_HP (°C)", value=-10.0, step=0.5)
            q_max_boiler = st.number_input("Q_max_BOILER (MW)", min_value=0.0, value=3.0, step=0.1)
            p_fuel = st.number_input("P_FUEL (EUR/nm³)", min_value=0.0, value=0.75, step=0.01)
            q_fuel = st.number_input("q_FUEL (kWh/nm³)", min_value=0.0, value=9550.0, step=10.0)
            eta_boiler = st.number_input("eta_BOILER (%)", min_value=0.0, max_value=100.0, value=98.0, step=0.1)
            d_hs = st.number_input("d_HS (m)", min_value=0.0, value=5.0, step=0.1)

        with col2:
            h_hs = st.number_input("H_HS (m)", min_value=0.0, value=12.0, step=0.1)
            t_min_hs = st.number_input("T_min_HS (°C)", min_value=0.0, value=30.0, step=1.0)
            t_max_hs = st.number_input("T_max_HS (°C)", min_value=0.0, value=85.0, step=1.0)
            lambda_hs = st.number_input("lambda_HS (W/m·K)", min_value=0.0, value=0.032, step=0.001)
            dx_hs = st.number_input("dx_HS (m)", min_value=0.0, value=0.25, step=0.01)
            capex_hp = st.number_input("CAPEX_HP (EUR/kW)", min_value=0.0, value=6000.0, step=100.0)
            capex_hs = st.number_input("CAPEX_HS (EUR/kWh)", min_value=0.0, value=0.1, step=0.01)
            opex_hp = st.number_input("OPEX_HP (EUR/kW/year)", min_value=0.0, value=300.0, step=10.0)
            opex_hs = st.number_input("OPEX_HS (EUR/kWh/year)", min_value=0.0, value=0.005, step=0.001)

        # Row for discount rate and number of years
        col3, col4 = st.columns(2)
        with col3:
            discount_rate = st.number_input("discount_rate (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1)
        with col4:
            number_of_years = st.number_input("number_of_years", min_value=1, value=5, step=1)

        # Create a section for produktai
        st.subheader("Produktai")
        col5, col6 = st.columns(2)

        with col5:
            fcr = st.checkbox("FCR", value=True, key="p2h_fcr")
            afrrd = st.checkbox("aFRRd", value=True, key="p2h_afrrd")
            afrru = st.checkbox("aFRRu", value=True, key="p2h_afrru")

        with col6:
            mfrrd = st.checkbox("mFRRd", value=True, key="p2h_mfrrd")
            mfrru = st.checkbox("mFRRu", value=True, key="p2h_mfrru")

        # Submit button
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        # Create the request body
        request_body = {
            "Q_max_HP": q_max_hp,
            "startup_time_HP": startup_time_hp,
            "delay_HP": delay_hp,
            "T_HP": t_hp,
            "Q_max_BOILER": q_max_boiler,
            "P_FUEL": p_fuel,
            "q_FUEL": q_fuel,
            "eta_BOILER": eta_boiler,
            "d_HS": d_hs,
            "H_HS": h_hs,
            "T_min_HS": t_min_hs,
            "T_max_HS": t_max_hs,
            "lambda_HS": lambda_hs,
            "dx_HS": dx_hs,
            "CAPEX_HP": capex_hp,
            "CAPEX_HS": capex_hs,
            "OPEX_HP": opex_hp,
            "OPEX_HS": opex_hs,
            "discount_rate": discount_rate,
            "number_of_years": number_of_years,
            "produktai": {
                "FCR": "True" if fcr else "False",
                "aFRRd": "True" if afrrd else "False",
                "aFRRu": "True" if afrru else "False",
                "mFRRd": "True" if mfrrd else "False",
                "mFRRu": "True" if mfrru else "False"
            }
        }

        # Display the request body
        with st.expander("Request Body"):
            st.json(request_body)

        # Make the POST request
        with st.spinner("Processing request..."):
            try:
                # response = requests.post("http://0.0.0.0:80/p2h", json=request_body)
                response = requests.post(
                    "https://epsogapitest.orangebush-c16de4cd.westeurope.azurecontainerapps.io/p2h", json=request_body)

                response.raise_for_status()  # Raise exception for 4XX/5XX status codes

                # Parse the response
                data = response.json()

                # Display success message
                st.success("Request successful!")

                # Add download button for the JSON response
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(data, indent=2),
                    file_name="p2h_response.json",
                    mime="application/json"
                )

                # Convert raw data to DataFrame for visualization
                raw_data = pd.DataFrame(data["raw"])

                # Convert datetime column
                raw_data["dt"] = pd.to_datetime(raw_data["dt"])
                raw_data = raw_data.sort_values(by="dt")

                # Visualization section
                st.header("Visualization")

                # Create tabs for different visualizations
                tab1, tab2 = st.tabs(["Optimization", "Economics"])

                with tab1:
                    st.subheader("Optimization Results")

                    # Create the two specified graphs
                    energy_tab, temp_tab = st.tabs(["Energy (MWh)", "Temperature (°C)"])

                    with energy_tab:
                        # Find energy-related columns
                        # Lithuanian labels: poreikis, katilinė, perkama DA, perkama ID, parduodama ID
                        energy_cols = {}

                        # Map the Lithuanian labels to possible column names in the data
                        if "Q" in raw_data.columns:
                            energy_cols["poreikis"] = "Q"

                        if "OPT_Q_BOILER_DA" in raw_data.columns:
                            energy_cols["katilinė"] = "OPT_Q_BOILER_DA"

                        # Buy/sell columns - check which ones exist
                        buy_da_cols = [c for c in raw_data.columns if "BUY" in c and "DA" in c]
                        buy_id_cols = [c for c in raw_data.columns if "BUY" in c and "ID" in c]
                        sell_id_cols = [c for c in raw_data.columns if "SELL" in c and "ID" in c]

                        # Create a dataframe for the MWh chart with columns that exist
                        energy_df = pd.DataFrame({
                            "dt": raw_data["dt"]
                        })

                        # Add each energy column that exists
                        if "poreikis" in energy_cols:
                            energy_df["poreikis"] = raw_data[energy_cols["poreikis"]]

                        if "katilinė" in energy_cols:
                            energy_df["katilinė"] = raw_data[energy_cols["katilinė"]]

                        # For perkama DA (bought day-ahead), sum all relevant columns
                        if buy_da_cols:
                            energy_df["perkama DA"] = raw_data[buy_da_cols].sum(axis=1)

                        # For perkama ID (bought intraday), sum all relevant columns
                        if buy_id_cols:
                            energy_df["perkama ID"] = raw_data[buy_id_cols].sum(axis=1)

                        # For parduodama ID (sold intraday), sum all relevant columns
                        if sell_id_cols:
                            energy_df["parduodama ID"] = raw_data[sell_id_cols].sum(axis=1)

                        # If we have any energy columns, create the chart
                        if len(energy_df.columns) > 1:  # More than just the dt column
                            # Melt the dataframe for plotting
                            energy_melt = pd.melt(
                                energy_df,
                                id_vars=["dt"],
                                var_name="Category",
                                value_name="MWh"
                            )

                            # Create a bar chart showing total energy by category
                            energy_sum = energy_melt.groupby("Category")["MWh"].sum().reset_index()

                            fig = px.bar(
                                energy_sum,
                                x="Category",
                                y="MWh",
                                title="Energijos paskirstymas (MWh)",
                                labels={"MWh": "MWh", "Category": "Kategorija"}
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Energijos duomenų nerasta")

                    with temp_tab:
                        # Find temperature-related columns
                        temp_cols = {
                            "Aplinkos temperatūra": None,
                            "Minimali paduodamo vandens temperatūra": None,
                            "Planuojama temperatūra talpykloje DA": None,
                            "Galutinė temperatūra talpykloje": None
                        }

                        # Map to potential column names
                        if "Ta" in raw_data.columns:
                            temp_cols["Aplinkos temperatūra"] = "Ta"

                        if "T1" in raw_data.columns:
                            temp_cols["Minimali paduodamo vandens temperatūra"] = "T1"

                        if "OPT_T_HS_DA" in raw_data.columns:
                            temp_cols["Planuojama temperatūra talpykloje DA"] = "OPT_T_HS_DA"

                        if "OPT_T_HS_ID" in raw_data.columns:
                            temp_cols["Galutinė temperatūra talpykloje"] = "OPT_T_HS_ID"

                        # Create a dataframe for the temperature chart
                        temp_df = pd.DataFrame({
                            "dt": raw_data["dt"]
                        })

                        # Add each temperature column that exists
                        for label, col in temp_cols.items():
                            if col and col in raw_data.columns:
                                temp_df[label] = raw_data[col]

                        # If we have any temperature columns, create the chart
                        if len(temp_df.columns) > 1:  # More than just the dt column
                            # Create a line chart for temperatures over time
                            fig = px.line(
                                temp_df,
                                x="dt",
                                y=[c for c in temp_df.columns if c != "dt"],
                                title="Temperatūros kitimas",
                                labels={
                                    "value": "Temperatūra (°C)",
                                    "dt": "Data",
                                    "variable": "Parametras"
                                }
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Temperatūros duomenų nerasta")

                with tab2:
                    st.subheader("Economic Analysis")

                    # Display the aggregated data
                    if "aggregated" in data:
                        # Create a summary dashboard with aggregated visualizations
                        st.subheader("Summary Dashboard")

                        # Create a layout for the dashboard
                        col1, col2 = st.columns(2)

                        # 1. Energy Chart (Energija)
                        with col1:
                            if "total_energy" in data["aggregated"]:
                                energy_data = data["aggregated"]["total_energy"]
                                energy_df = pd.DataFrame({
                                    "Category": list(energy_data.keys()),
                                    "Value (GWh)": list(energy_data.values())
                                })

                                fig = px.bar(energy_df, x="Category", y="Value (GWh)",
                                             title="Energija (GWh)",
                                             labels={"Value (GWh)": "GWh", "Category": ""})
                                fig.update_layout(height=300)
                                # Allow scientific notation on axis but show full number on hover
                                fig.update_yaxes(exponentformat="power")
                                fig.update_traces(hovertemplate='%{y:,.8f}<extra></extra>')
                                st.plotly_chart(fig, use_container_width=True)

                        # 2. Power Chart (Galia)
                        with col2:
                            if "average_power" in data["aggregated"]:
                                power_data = data["aggregated"]["average_power"]
                                power_df = pd.DataFrame({
                                    "Category": list(power_data.keys()),
                                    "Value (MW)": list(power_data.values())
                                })

                                fig = px.bar(power_df, x="Category", y="Value (MW)",
                                             title="Galia (MW)",
                                             labels={"Value (MW)": "MW", "Category": ""})
                                fig.update_layout(height=300)
                                # Allow scientific notation on axis but show full number on hover
                                fig.update_yaxes(exponentformat="power")
                                fig.update_traces(hovertemplate='%{y:,.8f}<extra></extra>')
                                st.plotly_chart(fig, use_container_width=True)

                        # 3. Time Chart (Laikas)
                        with col1:
                            if "total_time" in data["aggregated"]:
                                time_data = data["aggregated"]["total_time"]
                                time_df = pd.DataFrame({
                                    "Category": list(time_data.keys()),
                                    "Value (%)": list(time_data.values())
                                })

                                fig = px.bar(time_df, x="Category", y="Value (%)",
                                             title="Laikas (%)",
                                             labels={"Value (%)": "%", "Category": ""})
                                fig.update_layout(height=300)
                                # Allow scientific notation on axis but show full number on hover
                                fig.update_yaxes(exponentformat="power")
                                fig.update_traces(hovertemplate='%{y:,.8f}<extra></extra>')
                                st.plotly_chart(fig, use_container_width=True)

                        # 4. Revenue/Expenses Chart (Pajamos(+)/išlaidos(-))
                        with col2:
                            if "total_finance" in data["aggregated"]:
                                finance_data = data["aggregated"]["total_finance"]
                                finance_df = pd.DataFrame({
                                    "Category": list(finance_data.keys()),
                                    "Value (mln. Eur)": [value / 1000000 for value in finance_data.values()]
                                    # Convert to millions
                                })

                                fig = px.bar(finance_df, x="Category", y="Value (mln. Eur)",
                                             title="Pajamos(+)/išlaidos(-) (mln. Eur)",
                                             labels={"Value (mln. Eur)": "mln. Eur", "Category": ""})
                                fig.update_layout(height=300)
                                # Allow scientific notation on axis but show full number on hover
                                fig.update_yaxes(exponentformat="power")
                                fig.update_traces(hovertemplate='%{y:,.8f}<extra></extra>')
                                st.plotly_chart(fig, use_container_width=True)

                        # 5. Comparison Chart
                        with col1:
                            if "comparison" in data["aggregated"]:
                                comparison_data = data["aggregated"]["comparison"]
                                comparison_df = pd.DataFrame({
                                    "Category": list(comparison_data.keys()),
                                    "Value (mln. Eur)": [value / 1000000 for value in comparison_data.values()]
                                })

                                fig = px.bar(comparison_df, x="Category", y="Value (mln. Eur)",
                                             title="Suminės pajamos(+)/išlaidos(-) (mln. Eur)",
                                             labels={"Value (mln. Eur)": "mln. Eur", "Category": ""})
                                fig.update_layout(height=300)
                                # Allow scientific notation on axis but show full number on hover
                                fig.update_yaxes(exponentformat="power")
                                fig.update_traces(hovertemplate='%{y:,.8f}<extra></extra>')
                                st.plotly_chart(fig, use_container_width=True)

                        # 6. Discounted Payback Chart (Diskontuoto atsipirkimo grafikas)
                        with col2:
                            if "yearly" in data["aggregated"]:
                                yearly_data = pd.DataFrame(data["aggregated"]["yearly"])

                                fig = px.bar(yearly_data, x="YEAR", y="NPV",
                                             title="Diskontuoto atsipirkimo grafikas",
                                             labels={"NPV": "mln. Eur", "YEAR": ""})
                                fig.update_layout(height=300)
                                # Allow scientific notation on axis but show full number on hover
                                fig.update_yaxes(exponentformat="power")
                                fig.update_traces(hovertemplate='%{y:,.8f}<extra></extra>')
                                st.plotly_chart(fig, use_container_width=True)

                        # Additional detailed data in expanders
                        st.subheader("Detailed Analysis")
                        for category, values in data["aggregated"].items():
                            if category != "yearly":  # Handle yearly data separately
                                with st.expander(f"{category.replace('_', ' ').title()}"):
                                    # Convert to DataFrame for better display
                                    if isinstance(values, dict):
                                        df = pd.DataFrame(values.items(), columns=["Metric", "Value"])
                                        st.dataframe(df, use_container_width=True)
                                    elif isinstance(values, list):
                                        df = pd.DataFrame(values)
                                        st.dataframe(df, use_container_width=True)
                                    else:
                                        st.write(values)

                        # Create a special visualization for yearly data if available
                        if "yearly" in data["aggregated"]:
                            yearly_data = pd.DataFrame(data["aggregated"]["yearly"])

                            with st.expander("Yearly Results", expanded=True):
                                st.dataframe(yearly_data, use_container_width=True)

                                # Plot NPV over years
                                fig = px.line(yearly_data, x="YEAR", y="NPV", markers=True,
                                              labels={"NPV": "Net Present Value (EUR)", "YEAR": "Year"},
                                              title="Net Present Value Over Time")
                                # Allow scientific notation on axis but show full number on hover
                                fig.update_yaxes(exponentformat="power")
                                fig.update_traces(hovertemplate='%{y:,.8f}<extra></extra>')
                                st.plotly_chart(fig, use_container_width=True)

                                # Plot other yearly metrics
                                metrics = ["CYCLES", "SOH", "CAPEX", "OPEX", "CF"]
                                metrics = [m for m in metrics if m in yearly_data.columns]

                                if metrics:
                                    fig = px.line(yearly_data, x="YEAR", y=metrics, markers=True,
                                                  labels={"value": "Value", "YEAR": "Year", "variable": "Metric"},
                                                  title="Yearly Metrics")
                                    # Allow scientific notation on axis but show full number on hover
                                    fig.update_yaxes(exponentformat="power")
                                    fig.update_traces(hovertemplate='%{y:,.8f}<extra></extra>')
                                    st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No aggregated data available")

                # Add a section to view raw data
                with st.expander("Raw Data"):
                    st.dataframe(raw_data, use_container_width=True)

            except requests.exceptions.RequestException as e:
                st.error(f"Error making request: {str(e)}")
            except json.JSONDecodeError:
                st.error("Error parsing response JSON")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
