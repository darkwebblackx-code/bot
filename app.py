# app.py - Coty AI Chatbot & Order Tracker

import streamlit as st
import os
import sqlite3
from google import genai
from google.genai.errors import APIError
from datetime import datetime

# --- 1. Setup Gemini API ---
RENDER_ENV_VAR_NAME = "GEMINI_API_KEY_RENDER"

API_KEY = os.environ.get(RENDER_ENV_VAR_NAME)
if not API_KEY:
    st.error(f"❌ Gemini API key haipatikani. Weka Environment Variable '{RENDER_ENV_VAR_NAME}'")
    st.stop()

@st.cache_resource
def init_client(key):
    return genai.Client(api_key=key)

client = init_client(API_KEY)
GEMINI_MODEL = "gemini-2.5-flash"

# --- 2. Database setup ---
DB_NAME = "orders.db"
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()



# --- 3. Streamlit page setup ---
st.set_page_config(page_title="Coty Chatbot & Admin", page_icon="✨")
st.title("Coty Butchery - Chatbot na Orders")
st.sidebar.header("Navigation")
page = st.sidebar.selectbox("Chagua page", ["Chatbot", "Admin"])

# --- 4. Chatbot page ---
if page == "Chatbot":
    st.subheader("Karibu kwenye AI Customer Service 🤖")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Onyesha historia
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input ya mteja
    if prompt := st.chat_input("Uliza swali au toa order hapa:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        gemini_contents = [
            {"role": "user" if m["role"]=="user" else "model", "parts":[{"text":m["content"]}]} 
            for m in st.session_state.messages
        ]

        try:
            with st.chat_message("assistant"):
                with st.spinner("AI inafikiria..."):
                    chat_completion = client.models.generate_content(
                        model=GEMINI_MODEL,
                        contents=gemini_contents,
                        config={
                           SYSTEM_PROMPT = """
Wewe ni **Coty**, mhudumu wa wateja wa kidigitali mwenye **uwezo na akili mnemba (AI)**, uliyebuniwa na **Aqua Softwares**. Kazi yako ni **Huduma kwa Wateja ya Kitaalamu (Professional Customer Service)**, yenye ushawishi mkubwa.

### Jukumu na Sifa za Coty:
1.  **Adabu na Uelewa:** Kuwa na adabu na heshima ya **hali ya juu sana**, ukionyesha uelewa wa hali ya juu kwa mahitaji yote ya mteja.
2.  **Lugha:** Zungumza **Kiswahili Sanifu** fasaha. Ikiwa mteja atabadili na kutaka kutumia **Kiingereza**, badilika haraka na utumie **Kiingereza Sanifu** pia. **Tumia lugha fupi, wazi, na iliyo makini (focus). au kumuuliza mteja lugha gani anataka kuongea na kisha utumie lugha hiyo**
3.  **Utambulisho wa Kwanza (Muhimu):** Jibu lako la kwanza kabisa lianze na **Salamu (k.m. Habari yako, au Hello)**, kisha:
    * **Jijitambulishe** kama mhudumu   wa wateja kutoka Coty

Jibu kwa ufupi na kirafiki.

Kabla ya kuthibitisha order, hakikisha umepata:

- Jina kamili
- Namba ya simu
- Location
- Bidhaa anayotaka
- Idadi ya bidhaa

Ukikosa taarifa yoyote, muulize kwa ufupi.
Ukishapata zote, rudisha taarifa kwa format hii:

JINA:
SIMU:
LOCATION:
BIDHAA:
IDADI:"""

Jibu kwa ufupi na kirafiki.

Kabla ya kuthibitisha order, hakikisha umepata:

- Jina kamili
- Namba ya simu
- Location
- Bidhaa anayotaka
- Idadi ya bidhaa

Ukikosa taarifa yoyote, muulize kwa ufupi.
Ukishapata zote, rudisha taarifa kwa format hii:

JINA:
SIMU:
LOCATION:
BIDHAA:
IDADI:""",
                            "temperature": 0.9
                        }
                    )
                    response = chat_completion.text
                    st.markdown(response)
        except APIError as e:
            response = f"Kosa la AI: {e}"
            st.markdown(response)
        except Exception as e:
            response = f"Kosa lisilotarajiwa: {e}"
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

      import re

def detect_order(ai_response):
    fields = {
        "jina": None,
        "simu": None,
        "location": None,
        "bidhaa": None,
        "idadi": None
    }

    for line in ai_response.split("\n"):
        line = line.strip()

        if line.upper().startswith("JINA:"):
            fields["jina"] = line.split(":",1)[1].strip()

        elif line.upper().startswith("SIMU:"):
            fields["simu"] = line.split(":",1)[1].strip()

        elif line.upper().startswith("LOCATION:"):
            fields["location"] = line.split(":",1)[1].strip()

        elif line.upper().startswith("BIDHAA:"):
            fields["bidhaa"] = line.split(":",1)[1].strip()

        elif line.upper().startswith("IDADI:"):
            fields["idadi"] = line.split(":",1)[1].strip()

    # Hakikisha zote zipo
    if all(fields.values()):
        return fields
    return None

order = detect_order(ai_response)

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
    st.success("Order imehifadhiwa!")
st.header("Admin Orders")

cursor.execute("SELECT * FROM orders")
data = cursor.fetchall()

if data:
    for row in data:
        st.write(f"""
        Jina: {row[1]}
        Simu: {row[2]}
        Location: {row[3]}
        Bidhaa: {row[4]}
        Idadi: {row[5]}
        """)
else:
    st.info("Hakuna order bado.")

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
