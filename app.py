import streamlit as st
import base64
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import initialize_agent, AgentType
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler


def img_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

GEMINI_API_KEY = st.secrets["api_keys"]["GEMINI_API_KEY"]

st.set_page_config(
    page_title="Yojna Tau",
    page_icon="img/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

logo_base64 = img_to_base64("img/logo.png")
bg_base64 = img_to_base64("img/background.png")

page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{bg_base64}");
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    [data-testid="stSidebar"] > div:first-child {{
        background-image: url("data:image/png;base64,{bg_base64}");
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    .block-container {{
        background-color: transparent !important;
    }}

    /* Make chat input block and footer bar transparent */
    div[data-testid="stBottom"] {{
        background: transparent !important;
        box-shadow: none !important;
    }}

    div[data-testid="stChatInput"] {{
        background: transparent !important;
        box-shadow: none !important;
    }}

    div[data-baseweb="select"] > div {{
        background-color: #d6f0ff !important;
        color: #003366 !important;
        border-radius: 8px !important;
        border: 2px solid #003366 !important;
        font-weight: bold;
    }}

    div[data-baseweb="select"] span {{
        color: #003366 !important;
        font-weight: bold;
    }}

    ul[data-testid="stSelectboxVirtualDropdown"] {{
        background-color: #f0f8ff !important;
        border: 2px solid #003366 !important;
        border-radius: 8px !important;
        padding: 4px;
    }}

    ul[data-testid="stSelectboxVirtualDropdown"] li {{
        color: #003366 !important;
        padding: 8px;
        font-weight: 500;
        border-radius: 4px;
    }}

    ul[data-testid="stSelectboxVirtualDropdown"] li:hover {{
        background-color: #cdefff !important;
        color: #002244 !important;
        cursor: pointer;
    }}

    ul[data-testid="stSelectboxVirtualDropdown"] li[aria-selected="true"] {{
        background-color: #a1dafb !important;
        font-weight: bold;
    }}

    .chat-message {{
        font-family: 'Segoe UI', sans-serif;
        font-size: 16px;
        padding: 12px 18px;
        margin: 10px 0;
        max-width: 85%;
        word-wrap: break-word;
        border-radius: 12px;
        line-height: 1.5;
        position: relative;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        border: 2px solid transparent;
    }}

    .chat-message.assistant {{
        background-color: #d6f0ff;
        color: #003366;
        border-color: #003366;
        align-self: flex-start;
        border-top-left-radius: 0;
    }}

    .chat-message.user {{
        background-color: #fff3e0;
        color: #6d3b00;
        border-color: #fb8c00;
        align-self: flex-end;
        margin-left: auto;
        border-top-right-radius: 0;
    }}

    .chat-message.assistant:before {{
        content: "👳‍♂️ ";
        font-size: 18px;
        margin-right: 6px;
    }}

    .chat-message.user:before {{
        content: "🧑 ";
        font-size: 18px;
        margin-right: 6px;
    }}

    div[data-testid="stChatInput"] textarea::placeholder {{
        color: #ff6600 !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        font-family: 'Segoe UI', sans-serif !important;
        opacity: 1 !important;
    }}

    /* Override for textarea styling */
    div[data-testid="stChatInput"] textarea {{
        background-color: rgba(255, 255, 255, 1) !important;
        color: #ff6600 !important;
        border-radius: 18px !important;
        padding: 12px !important;
        font-size: 16px !important;
    }}

    /* Override for button styling */
    div[data-testid="stChatInput"] button {{
        background-color: #003366 !important;
        color: white !important;
        border-radius: 50% !important;
        padding: 0.5rem !important;
    }}

    /* Background for full wrapper element using partial class match */
    div[class*="st-bb"] {{
        background-color: rgba(255, 255, 255, 1) !important;
    }}
    
    /* If the wrapper has even deeper nesting, increase specificity */
    div[data-testid="stChatInput"] > div[class*="st-bb"] {{
        background-color: rgba(255, 255, 255, 1) !important;
    }}

    /* Optional: Transparent chat container backgrounds */
    div[class="st-emotion-cache-hzygls eht7o1d3"] {{
        background-color: rgba(0, 0, 0, 0);
    }}

    div[class="st-emotion-cache-x1bvup e1togvvn1"] {{
        background-color: rgba(255, 255, 255, 1);
    }}

    </style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

st.sidebar.markdown(
    f'<img src="data:image/png;base64,{logo_base64}" class="cover-glow">',
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state["messages"] = []
    st.session_state["messages"].append({
        "role": "system",
        "content": (
            "You are Yojna Tau, an expert guide for Haryana Government Schemes. "
            "Follow these instructions carefully: "
            "1. Role: Answer as an expert in Haryana Government Schemes. "
            "2. Content: Provide accurate and up-to-date information about government schemes, eligibility criteria, benefits, required documents, application process, and relevant timelines. "
            "3. User Question: The user's last message is their query. "
            "4. Language: Reply in the same language as the user's query: (Hindi, English). "
            "5. Tone: Use simple, clear, and friendly language. "
            "6. If unsure: Politely say you are unsure. Do not guess or make up information."
        )
    })
if "suggestion_clicked" not in st.session_state:
    st.session_state["suggestion_clicked"] = False


for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    role_class = f"chat-message {msg['role']}"
    st.markdown(f"<div class='{role_class}'>{msg['content']}</div>", unsafe_allow_html=True)

def processing(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    role_class = f"chat-message user"
    st.markdown(f"<div class='{role_class}'>{prompt}</div>", unsafe_allow_html=True)
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=GEMINI_API_KEY
    )
    search = DuckDuckGoSearchRun(name="Search")
    search_agent = initialize_agent(
        [search], llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, handle_parsing_errors=True
    )

    st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
    response = search_agent.run(st.session_state.messages, callbacks=[st_cb])
    st.session_state.messages.append({"role": "assistant", "content": response})
    role_class = f"chat-message assistant"
    st.markdown(f"<div class='{role_class}'>{response}</div>", unsafe_allow_html=True)

st.markdown("""
<style>
div.stButton > button {
    background: linear-gradient(135deg, #00B4DB, #FF8C00);
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 12px;
    font-size: 18px;
    font-weight: bold;
    transition: background 0.4s ease, transform 0.2s ease;
    box-shadow: 2px 4px 10px rgba(0, 0, 0, 0.2);
}

div.stButton > button:hover {
    background: linear-gradient(135deg, #00A6C1, #FF9933);
    color: white !important;  /* Fixes the red hover text */
    transform: scale(1.04);
    cursor: pointer;
}
</style>


""", unsafe_allow_html=True)

st.markdown("""
    <style>
    .suggestion-container {
        margin-top: 200px;  /* adjust this value as needed */
    }
    </style>
""", unsafe_allow_html=True)


suggestions_placeholder = st.empty()
with suggestions_placeholder.container():
    st.markdown('<div class="suggestion-container">', unsafe_allow_html=True)
    cols = st.columns(3)
    for idx, suggestion in enumerate(["What is the eligibilty criterion of Widow Pension Scheme?", "राजीव गांधी परिवार बीमा योजना क्या है?", "परिवार पहचान पत्र के लिए आवश्यक दस्तावेज़ क्या हैं?"]):
        if cols[idx].button(suggestion, key=f"suggestion_{suggestion}"):
            st.session_state.suggestion_clicked = True
            st.session_state.clicked_prompt = suggestion
    cols = st.columns(3)
    if cols[1].button("What is Old Age Samman Allowance?", key=f"suggestion_{"What is Old Age Samman Allowance?"}"):
        st.session_state.suggestion_clicked = True
        st.session_state.clicked_prompt = "What is Old Age Samman Allowance?"
    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.get("suggestion_clicked", False):
    suggestions_placeholder.empty()
    processing(st.session_state.clicked_prompt)
    st.session_state.suggestion_clicked = False
if prompt := st.chat_input(placeholder="Ask me something"):
    suggestions_placeholder.empty()
    processing(prompt)



