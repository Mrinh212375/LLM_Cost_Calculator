import streamlit as st
from calculate import calculator
import json

# Open and read the JSON file
with open('pricing_data.json', 'r') as file:
    data = json.load(file)

provider_model_mapping= {}

for p, v in data.items():
    provider_model_mapping[p] = []
    for m in v:
        provider_model_mapping[p].append(m)

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
st.sidebar.markdown("N.B - You can choose upto 3 (provider,model) of your choice.")

with st.sidebar.header("Select Provider"):
    selected_provider = st.selectbox("Select Provider",list(provider_model_mapping.keys()))

with st.sidebar.header("Select Model from {}".format(selected_provider)):
    models = provider_model_mapping.get(selected_provider, [])
    selected_model = st.selectbox("Select Model from {}".format(selected_provider),models)

Input_text = st.sidebar.text_area("Write your Input Text", placeholder="Input Text",height=100)
Output_tokens = st.sidebar.number_input("Output Tokens(Integer Only)", placeholder="please provide the number of output tokens",format="%d",value=0)

st.title("Welcome to The LLM Cost Calculator")


# Handle "Calculate Cost" button
if st.sidebar.button("Calculate Cost"):
    # Save result visibility state
    st.session_state.show_result = True
    st.session_state.show_details = False  # Reset details visibility

    # Calculate the cost
    c = calculator(selected_provider, selected_model)
    Input_tokens = c.count_from_text(Input_text)
    st.session_state.cost = c.calculate(Input_tokens, Output_tokens)
    st.session_state.result_text = (
        f'<p style="font-size: 18px;">The total costs for 1 query with {Input_tokens + Output_tokens} tokens '
        f'when using <span style="color: rgb(255, 75, 75);font-size: 20px;">{selected_model}</span> in '
        f'<span style="color: rgb(255, 75, 75);font-size: 20px;">{selected_provider}</span> are: </p>'
    )

# Show result if available
if st.session_state.show_result:
    st.write(st.session_state.result_text, unsafe_allow_html=True)
    st.markdown(
        f'<p style="text-align:center; font-weight: bold;"><span style="color: rgb(255, 75, 75); font-size: 32px">'
        f'${st.session_state.cost:.10f}</span></p>',
        unsafe_allow_html=True,
    )

    # Handle "Details" button
    if st.button("Click here to see the detailed information"):
        st.session_state.show_details = True

    # Show details if available
    if st.session_state.show_details:

        
        st.write(
    f'<p style="font-size: 18px; font-weight: bold;">Input Token Rate:</p> '
    f'<p style="font-size: 20px;">Rate per 1000 Input tokens for {selected_model} in {selected_provider} is '
    f'<strong>${float(data[selected_provider][selected_model][0] * 0.001):.10f}</strong></p>',
    unsafe_allow_html=True
    )

        st.write(
            f'<p style="font-size: 18px; font-weight: bold;">Output Token Rate:</p> '
            f'<p style="font-size: 20px;">Rate per 1000 Output tokens for {selected_model} in {selected_provider} is '
            f'<strong>${float(data[selected_provider][selected_model][1] * 0.001):.10f}</strong></p>',
            unsafe_allow_html=True
        )

        st.write(
            f'<p style="font-size: 18px; font-weight: bold;">Input Tokens Cost:</p> '
            f'<p style="font-size: 20px;">Cost incurred for {Input_tokens} Input tokens is '
            f'<strong>${float(data[selected_provider][selected_model][0] * Input_tokens * 0.000001):.10f}</strong></p>',
            unsafe_allow_html=True
        )

        st.write(
            f'<p style="font-size: 18px; font-weight: bold;">Output Tokens Cost:</p> '
            f'<p style="font-size: 20px;">Cost incurred for {Output_tokens} Output tokens is '
            f'<strong>${float(data[selected_provider][selected_model][1] * Output_tokens * 0.000001):.10f}</strong></p>',
            unsafe_allow_html=True
        )

        st.write(
            f'<p style="font-size: 18px; font-weight: bold;">Total Cost:</p> '
            f'<p style="font-size: 24px; font-weight: bold;">Your Total Cost is '
            f'<strong>${st.session_state.cost:.10f}</strong></p>',
            unsafe_allow_html=True
        )

