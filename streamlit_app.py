import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px

# Set page title and description
st.set_page_config(page_title="BEKS Demo", layout="wide")
st.title("BEKS Demo")
st.write("Fill in the form below to submit a request to the BEKS API.")

# Create form for input parameters
with st.form("input_form"):
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

            # Visualization section
            st.header("Visualization")

            # Create tabs for different visualizations
            tab1, tab2, tab3, tab4 = st.tabs(["Prices", "Quantities", "Optimization", "Economics"])

            with tab1:
                st.subheader("Price Data")

                # Create subtabs for different price categories
                price_tab1, price_tab2 = st.tabs(["Market Prices", "Reserve Prices"])

                with price_tab1:
                    fig = px.line(raw_data, x="dt", y=["P_DA", "P_ID"],
                                  labels={"value": "Price (EUR/MWh)", "dt": "Date", "variable": "Price Type"},
                                  title="Day-Ahead and Intraday Prices")
                    st.plotly_chart(fig, use_container_width=True)

                with price_tab2:
                    reserve_price_cols = [col for col in raw_data.columns if col.startswith("P_")
                                          and col not in ["P_DA", "P_ID", "P_DA_FORECAST"]]
                    if reserve_price_cols:
                        fig = px.line(raw_data, x="dt", y=reserve_price_cols,
                                      labels={"value": "Price (EUR/MWh)", "dt": "Date", "variable": "Price Type"},
                                      title="Reserve Prices")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No reserve price data available")

            with tab2:
                st.subheader("Quantity Data")

                # Create subtabs for different quantity categories
                q_tab1, q_tab2, q_tab3 = st.tabs(["Imbalance", "Reserve Quantities", "Other Quantities"])

                with q_tab1:
                    imbalance_cols = [col for col in raw_data.columns if "imbalance" in col.lower()]
                    if imbalance_cols:
                        fig = px.line(raw_data, x="dt", y=imbalance_cols,
                                      labels={"value": "Quantity (MWh)", "dt": "Date", "variable": "Metric"},
                                      title="Imbalance Quantities")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No imbalance data available")

                with q_tab2:
                    reserve_qty_cols = [col for col in raw_data.columns if col.startswith("Q_")
                                        and ("aFRR" in col or "mFRR" in col)]
                    if reserve_qty_cols:
                        fig = px.line(raw_data, x="dt", y=reserve_qty_cols,
                                      labels={"value": "Quantity (MWh)", "dt": "Date", "variable": "Metric"},
                                      title="Reserve Quantities")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No reserve quantity data available")

                with q_tab3:
                    other_qty_cols = [col for col in raw_data.columns if col.startswith("Q_")
                                      and col not in imbalance_cols + reserve_qty_cols]
                    if other_qty_cols:
                        fig = px.line(raw_data, x="dt", y=other_qty_cols,
                                      labels={"value": "Quantity (MWh)", "dt": "Date", "variable": "Metric"},
                                      title="Other Quantities")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No other quantity data available")

            with tab3:
                st.subheader("Optimization Results")

                # Create subtabs for different optimization result categories
                opt_tab1, opt_tab2, opt_tab3 = st.tabs(["State of Charge", "Buy/Sell Decisions", "Cost Results"])

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

                with opt_tab3:
                    cost_cols = [col for col in raw_data.columns if "_C_" in col]
                    if cost_cols:
                        fig = px.line(raw_data, x="dt", y=cost_cols,
                                      labels={"value": "Cost (EUR)", "dt": "Date", "variable": "Metric"},
                                      title="Cost Results")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No cost data available")

            with tab4:
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