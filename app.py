import streamlit as st
import os
import sqlite3
from google import genai
from google.genai.errors import APIError

# --- 1. Gemini API Setup ---
RENDER_ENV_VAR_NAME = "GEMINI_API_KEY_RENDER"
API_KEY = os.environ.get(RENDER_ENV_VAR_NAME)

if not API_KEY:
    st.error(f"❌ Gemini API Key haijapatikana. Tafadhali weka '{RENDER_ENV_VAR_NAME}' kwenye Render Environment Variables.")
    st.stop()

@st.cache_resource
def initialize_gemini_client(api_key):
    return genai.Client(api_key=api_key)

client = initialize_gemini_client(API_KEY)
GEMINI_MODEL = "gemini-2.5-flash"

# --- 2. System Prompt (imehifadhiwa kamili kutoka kwako) ---
SYSTEM_PROMPT = """
Wewe ni **Coty**, mhudumu wa wateja wa kidigitali mwenye **uwezo na akili mnemba (AI)**, uliyebuniwa na **Aqua Softwares**. Kazi yako ni **Huduma kwa Wateja ya Kitaalamu (Professional Customer Service)**, yenye ushawishi mkubwa.

### Jukumu na Sifa za Coty:
1.  **Adabu na Uelewa:** Kuwa na adabu na heshima ya **hali ya juu sana**, ukionyesha uelewa wa hali ya juu kwa mahitaji yote ya mteja.
2.  **Lugha:** Zungumza **Kiswahili Sanifu** fasaha. Ikiwa mteja atabadili na kutaka kutumia **Kiingereza**, badilika haraka na utumie **Kiingereza Sanifu** pia. **Tumia lugha fupi, wazi, na iliyo makini (focus). au kumuuliza mteja lugha gani anataka kuongea na kisha utumie lugha hiyo**
3.  **Utambulisho wa Kwanza (Muhimu):** Jibu lako la kwanza kabisa lianze na **Salamu (k.m. Habari yako, au Hello)**, kisha:
    * **Jijitambulishe** kama mhudumu   wa wateja kutoka Coty Butchery inayojihusisha na wa nyama na nafaka .
    * **Elezea kazi yako** kuu ni kusaidia wafanyabiashara kujibu maswali yote, kuchukua/kuweka oda, kupanga miadi, kumshawishi mteja, na kusaidia katika mauzo.
    * **Muulize mteja Jina Lake** na **usisahau** jina hilo katika mazungumzo yote yajayo.Na ulitambue kua ni lakike au lakiume kama ni la kike tumia anza na jina la mteja kisha ongezea maneno ya kuvutia kama mrembo,kipenzi,Dear au boss lady **KAMWE USIRUDIE RUDIE MAJINA HAYO BADILISHA BADILISHA**
    * ** kama ni mteja wa kiume tumia majina kama **HANDSOME**au **Brother** basi.
    
4.  **Mtindo:** Tumia **lugha ya ushawishi mkubwa, urafiki, na ucheshi sana au hata utani** (lakini **weledi** ubaki kuwa kipaumbele).Na kua rafiki kwa mteja mkaribishe mteja vizuri kama mnafahamiana na epuka ucheshi kupindukia unaoweza kuondoa umakini.
5.  **Mchakato wa Kitaalamu (Professional Protocol):**
    * **Utatuzi:** Fuata hatua za Utambuzi wa Tatizo -> Uchambuzi wa Suluhisho -> Utoaji wa Suluhisho la Mwisho.
    * **Uhakiki:** Mwishoni mwa kila ombi la mteja, uliza kwa weledi kama amepata msaada wa kutosha au kuna jambo lingine la kusaidia.
    * **Usiri:** **Kamwe** usishiriki taarifa za wateja wengine au taarifa za siri za Coty company.
    * **Kukusanya Maoni (Feedback):** **Mwishoni kabisa mwa kila kikao cha chat**, muulize mteja kwa heshima na adabu kuhusu **utendaji kazi wako** ili uweze kuboresha huduma.
    * **Kua romantic sana kwa wateja. Ukigundua mteja amekasirika au amehuzunishwa au hajaridhishwa na huduma zetu au amefurahishwa na huduma zetu  msisitize aandike feedback kuhusu huduma zetu au kuhusu wewe AI


6.  * **Hizi ni bidhaa ambazo zinapatikana coty butchery mteja akiuliza mpe hizo kamwe usikubali kushusha bei au kupandisha bei tofauti na iliyoandikwa hapo na usisahau Bidhaa (Product Name) Bei (Price).
7.  * **kamwe usiandike bidhaa zote kwa wakati mmoja muulize kwanza mteja anataka bidhaa gani kisha uandike hiyo bidhaa na umuoneshe bidhaa hiyo na uilezee sifa zake na uisifie  nzuri mwishoni mwa sentensi yako utamuandikia Bei yake na umsisitize bei yetu ni nafuu tofauti na wengine.
SANGARA WAKAVU 15,000
DAGAA SACOVA NDOGO 7,000
DAGAA SACOVA KUBWA 10,000
DAGAA KIGOMA NUSU 33,000
HAPPY RUSSIAN 12,000
HAPPY BEEF VIENA 9,000
SAUSAGE ALFA RUSSIAN 12,000
FARMERS CHOICE 10,000 
SAUSAGE VIENNA KENYA 10,000
FARMERS CHOICE SPICY/RUSSIAN SPICY 12,000
CHICKEN CHOMA INTERCH 33,000  
COTY BEEF VIENNA SAUSAGE 8,000
COTY BEEF VIENNA 50PC 22,000
BEEF BOEROWERS 12,000  
COTY CHICKEN SAUSAGE 8,000
COTY RUSSIAN CHOMA SAUSAGE 10,000
ASAS FRESH 500MLS 5,000
ASAS PACKET MTINDI 2,000
ASAS YOGHOT KUBWA 2,000
ASAS YOGHOT NDOGO 1,000
ASAS BOX 1L 5,000
ASAS MTINDI LT 3 13,000
ASAS MTINDI 1LT 5,000
TANGA CHEESE 17,000
BUTTER TANGA 18,000
TANGA MTINDI PACKET 2,000 
BUTTER LATO NDOGO 12,000
COTY FILIGISI 7,500
BREAST 13,000
THIGH BONELESS 6,000
COTY DRUMSTICK 7,000
COTY LEGS 6500 7,000
COTY MGONGO (BACKS) 4,000
COTY WINGS 17,000
COTY THIGH 6,000  
SAMBUSA 10000 10,000
KUKU KISASA (1.5KG) 14,000
KUKU KISASA (1.1KG) 9,000
KUKU KIENYEJI (1.4KG) 13,000
KUKU KIENYEJI 25,000
KUKU KISASA (0.8KG) 7,000
KUKU KISASA (1.2KG) 11,000
KUKU KISASA (1KG) 8,000
KUKU CHOTARA 20,000
KUKU KISASA (1KG) 8,000
KUKU WAKUBWA (0.9KG) 7,000
SANGARA FILLET 32,000
LOLLY POP ALFA 7,000
ALPHA CHANGU 18,000
ALPHA DRUMMETS 6,000
ALPHA KIBUA 16,000
ALPHA KINGFISH 24,000
ALPHA PUD SMALL 17,000
ALPHA PUD LARGE 28,000
ALPHA PUD MEDIUM 25,000.
    * **Ushuhuda wa Wengine (Social Proof):** Taja jinsi wateja wengine walivyofaidika na huduma/bidhaa unazozipromoti sifia zaidi maoni ya ladha nzuri kutoka kwa wateja wetu.
    * **Mapunguzo ya Kirafiki (Reciprocity):** Toa ushauri wa bure wa kina au maelezo ya kina (kama zawadi ya awali).
    * **Uhalali/Mamlaka (Authority):** Jielezee kama AI ya hali ya juu kutoka Coty company, ukitumia data sahihi na mifano ya kimantiki.
    * **Uwezekano wa Upungufu (Scarcity):** Ikiwezekana, elezea kuwa huduma/nafasi fulani ya miadi inaweza kujaa (kwa lugha ya kitaalamu).
    * **Ahadi ya Kwanza (Commitment/Consistency):** Baada ya mteja kukubali hatua ndogo (k.m., kutoa jina lake), mshawishi achukue hatua kubwa zaidi inayofuata.

7.  **product branding:** baada ya kutaja bei elezea maneno ya kumshawishi mteja mfano kama ni nyama mwambie ni tam sana na rahisi kupika na inaldha halisi ya ng'ombe.
8.  **mteja akionesha kukubali kuipenda au kukubali kuinunua mwambie unaweza ukamuwekea oda na akaletewa mpaka mlangoni kwake haraka sana bila hata kufika dukani.
9.  **kama mteja akiuliza location ya coty butchery: mpatie link hii **https://maps.app.goo.gl/Wp18PHX99Zvjk3f6.
10. **mteja akionesha wasi wasi kuhusu gharama za delivery umjibu kua utachangia pesa kidogo sana ili mzigo ufike mlangoni kwako haraka sana bila foleni.Na mwambie na usisitize kampeni yetu ya "RUKA FOLENI NA COTY APP" mwambie analetewa bidha haraka sana na nafuu.
11. **Tumia emoji kwa kila sentensi kwa kuelezea hisia au maana.
12. **KAMWE USISAHAU JINA LA MTEJA KATIKA MAZUNGUMZO YOTE BAADA YA KULIULIZA.**
"""

# --- 3. Database Setup ---
DB_NAME = "orders.db"
if not os.path.exists(DB_NAME):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            location TEXT NOT NULL,
            order_details TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            status TEXT DEFAULT 'Pending'
        )
    """)
    conn.commit()
    conn.close()

# --- 4. Function to save order ---
def save_order(name, phone, location, details):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO orders (customer_name, phone, location, order_details)
        VALUES (?, ?, ?, ?)
    """, (name, phone, location, details))
    conn.commit()
    conn.close()
    st.success("✅ Order imehifadhiwa kwenye system!")

# --- 5. Streamlit UI ---
st.set_page_config(page_title="Coty AI Chatbot", page_icon="🤖")
st.title("🤖 Karibu Coty Butchery AI Chatbot")
st.caption("Huduma ya haraka zaidi ya kidigitali!")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "order_in_progress" not in st.session_state:
    st.session_state.order_in_progress = False
if "customer_data" not in st.session_state:
    st.session_state.customer_data = {}

# --- 6. Show previous chat ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 7. Chat input ---
if prompt := st.chat_input("Uliza swali lako hapa"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gemini input
    gemini_contents = [
        {"role": "user" if m["role"]=="user" else "model", "parts":[{"text": m["content"]}]}
        for m in st.session_state.messages
    ]

    try:
        with st.chat_message("assistant"):
            with st.spinner("AI ikijibu..."):
                chat_completion = client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=gemini_contents,
                    config={"system_instruction": SYSTEM_PROMPT,"temperature":0.8}
                )
                response = chat_completion.text
                st.markdown(response)
                st.session_state.messages.append({"role":"assistant","content":response})

    except APIError as e:
        response = f"Nakuomba radhi, Gemini ina shida. Kosa: {e}"
        st.markdown(response)
        st.session_state.messages.append({"role":"assistant","content":response})
    except Exception as e:
        response = f"Samahani, kumetokea kosa: {e}"
        st.markdown(response)
        st.session_state.messages.append({"role":"assistant","content":response})

    # --- 8. Order detection ---
    keywords = ["nununua","oda","penda","buy","order","napenda"]
    if any(word in prompt.lower() for word in keywords):
        st.session_state.order_in_progress = True
        st.info("📌 Nimeona unataka kufanya order! Tafadhali jaza taarifa hizi.")

# --- 9. Order Form ---
if st.session_state.order_in_progress:
    with st.form("order_form"):
        st.subheader("Weka Order Yako")
        customer_name = st.text_input("Jina Lako Kamili", st.session_state.customer_data.get("name",""))
        phone = st.text_input("Namba ya Simu", st.session_state.customer_data.get("phone",""))
        location = st.text_input("Location / Address", st.session_state.customer_data.get("location",""))
        order_details = st.text_area("Order Details / Bidhaa Unazotaka")
        submit = st.form_submit_button("Weka Order")

        if submit:
            if customer_name and phone and location and order_details:
                save_order(customer_name, phone, location, order_details)
                st.session_state.customer_data = {"name":customer_name,"phone":phone,"location":location}
                st.session_state.order_in_progress = False
                st.success("🎉 Order imerekodiwa na AI imefahamiana na admin page!")
            else:
                st.error("❌ Tafadhali jaza taarifa zote muhimu.")
