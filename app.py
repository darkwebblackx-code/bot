import streamlit as st
import os
import sqlite3
from google import genai

# --- API Setup ---
API_KEY = os.environ.get("GEMINI_API_KEY_RENDER")
if not API_KEY:
    st.error("❌ Gemini API key haipatikani. Weka Environment Variable GEMINI_API_KEY_RENDER")
    st.stop()

client = genai.Client(api_key=API_KEY)
MODEL = "gemini-2.5-flash"

# --- Database ---
conn = sqlite3.connect("orders.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jina TEXT,
    simu TEXT,
    location TEXT,
    bidhaa TEXT,
    idadi TEXT
)
""")
conn.commit()

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """
Wewe ni **Coty AI Assistant**, msaidizi wa mauzo wa duka.  

Kila order lazima irudishwe kwa format:
JINA:
SIMU:
LOCATION:
BIDHAA:
IDADI:

Jibu kwa ufupi na kirafiki.
"""

# --- Chatbot ---
st.title("🤖 Coty AI Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input from user
if prompt := st.chat_input("Andika order au swali..."):
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Send to AI
    try:
        chat_completion = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config={"system_instruction": SYSTEM_PROMPT, "temperature":0.3}
        )
        response = chat_completion.text
    except Exception as e:
        response = f"Kosa la AI: {e}"

    st.session_state.messages.append({"role":"assistant","content":response})
    with st.chat_message("assistant"):
        st.markdown(response)

    # --- Detect order ---
    def detect_order(text):
        data = {}
        for line in text.split("\n"):
            line = line.strip()
            if line.upper().startswith("JINA:"): data["jina"] = line.split(":",1)[1].strip()
            elif line.upper().startswith("SIMU:"): data["simu"] = line.split(":",1)[1].strip()
            elif line.upper().startswith("LOCATION:"): data["location"] = line.split(":",1)[1].strip()
            elif line.upper().startswith("BIDHAA:"): data["bidhaa"] = line.split(":",1)[1].strip()
            elif line.upper().startswith("IDADI:"): data["idadi"] = line.split(":",1)[1].strip()
        if len(data) == 5:
            return data
        return None

    order = detect_order(response)
    if order:
        cursor.execute("""
            INSERT INTO orders (jina, simu, location, bidhaa, idadi)
            VALUES (?, ?, ?, ?, ?)
        """,(order["jina"],order["simu"],order["location"],order["bidhaa"],order["idadi"]))
        conn.commit()
        st.success("✅ Order imehifadhiwa na imepeleka kwenye admin dashboard")
