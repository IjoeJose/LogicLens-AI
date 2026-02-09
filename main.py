import streamlit as st
from google import genai
from google.genai import types
from annotated_text import annotated_text

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Logic & Truth AI", page_icon="⚖️", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f0f2f6; border-radius: 10px 10px 0 0; padding: 10px; }
    .stTabs [aria-selected="true"] { background-color: #FF4B4B; color: white; }
    .result-card { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #FF4B4B; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR ---
with st.sidebar:
    st.title("Settings")
    api_key = st.text_input("Enter Gemini API Key:", type="password")
    st.info("Logic Mode: Detects errors in reasoning.\nFact Mode: Verifies claims via Google Search.")

if not api_key:
    st.warning("Please enter your API Key in the sidebar.")
    st.stop()

client = genai.Client(api_key=api_key)

# --- 3. MAIN INTERFACE ---
st.title("⚖️ Logic & Truth Verification Suite")

# Create Tabs
tab1, tab2 = st.tabs(["🧩 Logical Fallacy Detector", "🌐 Live Fact Checker"])

# --- TAB 1: FALLACY DETECTOR ---
with tab1:
    user_input = st.text_area("Paste an argument to check for fallacies:", placeholder="e.g., Everyone is doing it, so it must be right.")
    if st.button("Detect Fallacies"):
        with st.spinner("Analyzing reasoning..."):
            prompt = f"Analyze for logical fallacies. Format: FALLACY: [Name] SEGMENT: [Exact words] EXPLANATION: [Short]. Text: {user_input}"
            response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
            
            # Simple UI for results
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.write(response.text)
            st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: FACT CHECKER ---
with tab2:
    claim_input = st.text_input("Enter a claim to verify:", placeholder="e.g., The Great Wall of China is visible from space.")
    if st.button("Verify Claim"):
        with st.spinner("Searching..."):
            try:
                # TRY the high-tech way first
                config = types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
                response = client.models.generate_content(model="gemini-3-flash-preview", contents=claim_input, config=config)
                st.success("✅ Live Fact Check Successful!")
                st.write(response.text)
            except Exception as e:
                # FALLBACK: If the limit is hit, give the user "Ready-to-Use" search links
                st.warning("🚦 High Traffic: Switching to 'Guided Verification' Mode.")
                
                # Use standard Gemini (no search tool) to build a research plan
                fallback_prompt = f"Break this claim into 3 specific search queries for Google: {claim_input}"
                search_plan = client.models.generate_content(model="gemini-3-flash-preview", contents=fallback_prompt)
                
                st.info("The AI couldn't reach the live web right now, but here is your verification plan:")
                st.write(search_plan.text)
                
                # Create a clickable Google button for them
                search_url = f"https://www.google.com/search?q={claim_input.replace(' ', '+')}"
                st.link_button("Verify on Google Manually", search_url)