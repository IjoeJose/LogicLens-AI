import streamlit as st
from google import genai
from google.genai import types

# --- 1. PAGE CONFIG & DESIGN ---
st.set_page_config(page_title="Logic & Truth AI", page_icon="⚖️", layout="wide")

st.markdown("""
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
    
    <style>
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
            color: #e2e8f0;
        }
        .glass-card {
            background: rgba(15, 23, 42, 0.5);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 1rem;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        .heading-font { font-family: 'Space Grotesk', sans-serif; }
        .stTextArea textarea, .stTextInput input {
            background: rgba(30, 41, 59, 0.5) !important;
            border: 1px solid #475569 !important;
            color: white !important;
            border-radius: 0.75rem !important;
        }
        .stTabs [data-baseweb="tab-list"] { gap: 12px; }
        .stTabs [data-baseweb="tab"] {
            border: 1px solid #475569;
            background: rgba(30, 41, 59, 0.5);
            border-radius: 0.75rem;
            padding: 10px 20px;
            color: #94a3b8;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #a855f7 0%, #9333ea 100%) !important;
            color: white !important;
            border: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGIC FUNCTIONS (With Multi-Model Fallback) ---

def get_client(api_key):
    return genai.Client(api_key=api_key)

@st.cache_data(show_spinner=False)
def run_ai_logic(_client, prompt, use_search=False):
    """
    Tries multiple model identifiers to prevent 404 errors.
    """
    # List of possible model IDs the SDK might expect
    model_candidates = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-flash-latest"]
    
    last_error = None
    for model_id in model_candidates:
        try:
            if use_search:
                config = types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
                return _client.models.generate_content(model=model_id, contents=prompt, config=config)
            else:
                return _client.models.generate_content(model=model_id, contents=prompt)
        except Exception as e:
            last_error = e
            if "404" in str(e):
                continue # Try the next model name
            raise e # If it's a 429 or other error, stop and report it
            
    raise last_error

# --- 3. HEADER ---
st.markdown("""
    <header class="glass-card" style="margin-top: -50px;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="width: 50px; height: 50px; background: linear-gradient(135deg, #a855f7 0%, #3b82f6 100%); border-radius: 1rem; display: flex; align-items: center; justify-content: center;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
            </div>
            <div>
                <h1 class="heading-font" style="font-size: 1.5rem; font-weight: 700; color: #c084fc; margin:0;">Logic & Truth AI</h1>
                <p style="color: #94a3b8; font-size: 0.8rem; margin:0;">Hackathon Stable Edition</p>
            </div>
        </div>
    </header>
""", unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Settings")
    api_key = st.text_input("Gemini API Key", type="password")
    if st.button("Clear Cache"):
        st.cache_data.clear()
        st.success("Cache Cleared")
    st.markdown('</div>', unsafe_allow_html=True)

if not api_key:
    st.warning("Please enter your API Key in the sidebar.")
    st.stop()

client = get_client(api_key)

# --- 5. MAIN INTERFACE ---
tab1, tab2 = st.tabs(["🧩 Fallacy Detector", "🌐 Fact Checker"])

with tab1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h2 class='heading-font'>Logical Fallacy Detection</h2>", unsafe_allow_html=True)
    user_input = st.text_area("Paste an argument:", placeholder="e.g., Everyone is doing it, so it must be right.", height=150)
    
    if st.button("Detect Fallacies"):
        if user_input:
            with st.spinner("Analyzing..."):
                try:
                    prompt = f"Analyze for logical fallacies. Format: FALLACY: [Name] SEGMENT: [Exact words] EXPLANATION: [Short]. Text: {user_input}"
                    response = run_ai_logic(client, prompt, use_search=False)
                    st.markdown("### Analysis Breakdown")
                    st.write(response.text)
                except Exception as e:
                    if "429" in str(e):
                        st.error("🚦 Rate Limit Hit. Please wait 60 seconds.")
                    else:
                        st.error(f"Error: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h2 class='heading-font'>Live Fact Verification</h2>", unsafe_allow_html=True)
    claim_input = st.text_input("Enter a claim:", placeholder="e.g., The Great Wall of China is visible from space.")
    
    if st.button("Verify Claim"):
        if claim_input:
            with st.spinner("Searching..."):
                try:
                    response = run_ai_logic(client, claim_input, use_search=True)
                    st.success("### Verification Result")
                    st.write(response.text)
                except Exception as e:
                    if "429" in str(e):
                        st.error("🚦 Quota Exhausted. Try again in 1 minute.")
                    else:
                        st.error(f"Search Error: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='text-align: center; color: #64748b; font-size: 0.8rem; margin-top: 2rem;'>Built with Streamlit & Google Gemini</div>", unsafe_allow_html=True)
