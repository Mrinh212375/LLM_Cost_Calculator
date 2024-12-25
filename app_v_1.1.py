import streamlit as st
from calculate import calculator
import json
import pandas as pd  # For table creation

# Open and read the JSON file
with open('pricing_data.json', 'r') as file:
    data = json.load(file)

provider_model_mapping = {}
for p, v in data.items():
    provider_model_mapping[p] = [m for m in v]

st.set_page_config(
    page_title="LLM Cost Calculator",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state variables
if "show_result" not in st.session_state:
    st.session_state.show_result = False

if "show_details" not in st.session_state:
    st.session_state.show_details = False

st.sidebar.title("Please fill the below inputs to calculate the cost")
st.sidebar.markdown("N.B - You can choose up to 3 (provider, model) of your choice.")

# Multiselect logic for providers and models
selected_models = []

for i in range(3):  # Max of 3 selections
    with st.sidebar.header(f"Select Provider for Choice {i + 1} (Optional)"):
        selected_provider = st.selectbox(
            f"Select Provider (Choice {i + 1})",
            ["Select Provider"] + list(provider_model_mapping.keys()),
            key=f"provider_{i}"
        )
        if selected_provider != "Select Provider":
            models = provider_model_mapping.get(selected_provider, [])
            selected_model = st.selectbox(
                f"Select Model from {selected_provider} (Choice {i + 1})",
                ["Select Model"] + models,
                key=f"model_{i}"
            )
            if selected_model != "Select Model":
                selected_models.append((selected_provider, selected_model))

# Enforce selection rules
if len(selected_models) == 0:
    st.sidebar.warning("You must select at least 1 and at most 3 (provider, model) pairs.")
else:
    st.sidebar.subheader("You have selected:")
    for provider, model in selected_models:
        st.sidebar.write(f"- {provider}: {model}")

# Input and output fields
if len(selected_models) >= 1:
    Input_text = st.sidebar.text_area("Write your Input Text", placeholder="Input Text", height=100)
    Output_tokens = st.sidebar.number_input(
        "Output Tokens (Integer Only)",
        placeholder="Please provide the number of output tokens",
        format="%d",
        value=0,
    )
    st.session_state.Output_tokens = Output_tokens

st.title("Welcome to The LLM Cost Calculator")

# Handle "Calculate Cost" button
if st.sidebar.button("Calculate Cost"):
    # Save result visibility state
    st.session_state.show_result = True
    st.session_state.show_details = False  # Reset details visibility

    # Process cost calculation for each selected model
    results = []
    for provider, model in selected_models:
        c = calculator(provider, model)
        Input_tokens = c.count_from_text(Input_text)
        total_cost = c.calculate(Input_tokens, Output_tokens)
        st.session_state.Input_tokens = Input_tokens
        st.session_state.Total_cost = total_cost

        # Append data for the table
        results.append({
            "Provider : Model": f"{provider}  :  {model}",
            "Input Token Cost/1000 Tokens": f"${data[provider][model][0] * 0.001:.10f}",
            "Output Token Cost/1000 Tokens": f"${data[provider][model][1] * 0.001:.10f}",
            "Input Cost": f"${data[provider][model][0] * Input_tokens * 0.000001:.10f}",
            "Output Cost": f"${data[provider][model][1] * Output_tokens * 0.000001:.10f}",
            "Total Cost": f"${total_cost:.10f}",
        })

    # Convert to a DataFrame for display
    results_df = pd.DataFrame(results)
    # Extract the row with the minimum Total Cost
    min_cost_row = results_df.loc[results_df["Total Cost"].str.replace('$', '', regex=False).astype(float).idxmin()]

    # Extract the minimum Total Cost, Provider, and Model
    min_total_cost = min_cost_row["Total Cost"]
    provider_model = min_cost_row["Provider : Model"]
    provider, model = provider_model.split(":")

    st.session_state.min_total_cost = min_total_cost
    st.session_state.provider = provider.strip()
    st.session_state.model = model.strip()
    
    # Save results in session state for details display
    st.session_state.results_df = results_df

# Show results if available
if st.session_state.show_result:
    if len(selected_models) > 1:
        st.write(
            f'<p style="font-size: 18px;">From your selection, the most cost-effective model is '
            f'<span style="color: rgb(255, 75, 75); font-size: 20px; font-weight: bold;">{st.session_state.model}</span> in '
            f'<span style="color: rgb(255, 75, 75); font-size: 20px; font-weight: bold;">{st.session_state.provider}</span> with cost for 1 query:</p>',
    unsafe_allow_html=True
)

        st.markdown(
            f'<p style="text-align:center; font-weight: bold;"><span style="color: rgb(255, 75, 75); font-size: 32px">'
            f'{st.session_state.min_total_cost}</span></p>',
            unsafe_allow_html=True
        )
    else:
        st.write(
            f'<p style="font-size: 18px;">The total costs for 1 query with {st.session_state.Input_tokens + st.session_state.Output_tokens} tokens '
            f'when using <span style="color: rgb(255, 75, 75);font-size: 20px;">{selected_models[0][1]}</span> in '
            f'<span style="color: rgb(255, 75, 75);font-size: 20px;">{selected_models[0][0]}</span> are: </p>',unsafe_allow_html=True
        )
        st.markdown(
            f'<p style="text-align:center; font-weight: bold;"><span style="color: rgb(255, 75, 75); font-size: 32px">'
            f'${st.session_state.Total_cost:.10f}</span></p>',unsafe_allow_html=True)
    

    # Handle "Details" button
    if st.button("Click here to see Detailed Summary"):
        st.session_state.show_details = True

    # Show detailed table if available
    if st.session_state.show_details:
        st.subheader("Detailed Cost Summary of your select models")
        st.dataframe(st.session_state.results_df, use_container_width=True)
