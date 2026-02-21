# app.py - Coty AI Chatbot & Order Tracker (FIXED)

import streamlit as st
import os
import sqlite3
from google import genai
from google.genai.errors import APIError

# ----------------------------
# GEMINI SETUP
# ----------------------------
API_KEY = os.environ.get("GEMINI_API_KEY_RENDER")

if not API_KEY:
    st.error("Weka GEMINI_API_KEY_RENDER kwenye Environment Variables")
    st.stop()

@st.cache_resource
def init_client(key):
    return genai.Client(api_key=key)

client = init_client(API_KEY)
MODEL = "gemini-2.5-flash"

# ----------------------------
# DATABASE
# ----------------------------
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

# ----------------------------
# SYSTEM PROMPT
# ----------------------------
SYSTEM_PROMPT = """
Wewe ni mhudumu wa wateja.

Jibu kwa ufupi.

Kabla ya kuthibitisha order hakikisha una:

Jina
Simu
Location
Bidhaa
Idadi

Ukishapata zote rudisha hivi:

JINA:
SIMU:
LOCATION:
BIDHAA:
IDADI:
"""

# ----------------------------
# DETECT ORDER
# ----------------------------
def detect_order(text):
    data = {}
    lines = text.split("\n")

    for line in lines:
        if line.startswith("JINA:"):
            data["jina"] = line.replace("JINA:", "").strip()
        elif line.startswith("SIMU:"):
            data["simu"] = line.replace("SIMU:", "").strip()
        elif line.startswith("LOCATION:"):
            data["location"] = line.replace("LOCATION:", "").strip()
        elif line.startswith("BIDHAA:"):
            data["bidhaa"] = line.replace("BIDHAA:", "").strip()
        elif line.startswith("IDADI:"):
            data["idadi"] = line.replace("IDADI:", "").strip()

    if len(data) == 5:
        return data
    return None

# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title="Coty Orders", page_icon="🛒")
st.title("Coty Butchery System")

page = st.sidebar.selectbox("Chagua Page", ["Chatbot", "Admin"])

# ----------------------------
# CHATBOT
# ----------------------------
if page == "Chatbot":

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Andika ujumbe..."):

        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            response_obj = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config={
                    "system_instruction": SYSTEM_PROMPT,
                    "temperature": 0.3
                }
            )

            response = response_obj.text

        except Exception as e:
            response = f"AI Error: {e}"

        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.messages.append({"role":"assistant","content":response})

        # SAVE ORDER IF VALID
        order = detect_order(response)

        if order:
            cursor.execute("""
                INSERT INTO orders (jina, simu, location, bidhaa, idadi)
                VALUES (?, ?, ?, ?, ?)
            """, (
                order["jina"],
                order["simu"],
                order["location"],
                order["bidhaa"],
                order["idadi"]
            ))
            conn.commit()
            st.success("✅ Order yako imehifadhiwa kikamilifu!")

# ----------------------------
# ADMIN PAGE
# ----------------------------
if page == "Admin":

    st.header("📦 Orders Zote")

    cursor.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = cursor.fetchall()

    if not orders:
        st.warning("Hakuna order bado.")
    else:
        for order in orders:
            col1, col2 = st.columns([5,1])

            with col1:
                st.markdown(f"""
                **Jina:** {order[1]}  
                **Simu:** {order[2]}  
                **Location:** {order[3]}  
                **Bidhaa:** {order[4]}  
                **Idadi:** {order[5]}
                """)

            with col2:
                if st.button("Delete", key=f"delete_{order[0]}"):
                    cursor.execute("DELETE FROM orders WHERE id=?", (order[0],))
                    conn.commit()
                    st.success("Order imefutwa!")
                    st.rerun()
