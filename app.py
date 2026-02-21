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
                            "system_instruction": "Wewe ni mhudumu rafiki wa Coty. Uliza jina, namba ya simu, location, na idadi ya bidhaa. Jibu kwa ufupi, kirafiki na kwa heshima.ditect order kisha uitume kwenye admin page na taarifa ake muhim",
                            "temperature": 0.2
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

        # --- 5. Detect order data from AI response ---
        # Tunatazama kama mteja ametoa jina, phone, location, product, quantity
        import re
        name_match = re.search(r"Jina[:\s]*([A-Za-z ]+)", response, re.IGNORECASE)
        phone_match = re.search(r"(?:Simu|Phone)[:\s]*(\+?\d+)", response, re.IGNORECASE)
        location_match = re.search(r"Location[:\s]*([A-Za-z0-9 ,.-]+)", response, re.IGNORECASE)
        product_match = re.search(r"Bidhaa[:\s]*([A-Za-z0-9 ]+)", response, re.IGNORECASE)
        quantity_match = re.search(r"Idadi[:\s]*(\d+)", response, re.IGNORECASE)

        if name_match and phone_match and location_match and product_match and quantity_match:
            c.execute(
                "INSERT INTO orders (name, phone, location, product, quantity, date) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    name_match.group(1).strip(),
                    phone_match.group(1).strip(),
                    location_match.group(1).strip(),
                    product_match.group(1).strip(),
                    int(quantity_match.group(1)),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )
            conn.commit()
            st.success("✅ Order imehifadhiwa kikamilifu!")

# --- 6. Admin page ---
if page == "Admin":
    st.subheader("Admin - Orders Details 📋")
    df = None
    try:
        import pandas as pd
        df = pd.read_sql_query("SELECT * FROM orders ORDER BY id DESC", conn)
    except Exception as e:
        st.error(f"Kosa kufetch orders: {e}")
    
    if df is not None and not df.empty:
        st.dataframe(df)
        st.audio("https://www.soundjay.com/buttons/sounds/button-16.mp3")  # kengele ya sauti
    else:
        st.info("Hakuna orders kwa sasa.")
