import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client

st.set_page_config(page_title="AI Chatbot", page_icon="🤖")
st.title("💬 Môj AI Chatbot")

# Načítanie kľúčov zo Streamlit Secrets
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Inicializácia Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Nastavenie modelu a slovenskej inštrukcie
generation_config = {
    "temperature": 0.7,
}
system_instruction = "Odpovedaj vždy plynulo po slovensky."

# Použijeme aktuálny podporovaný model
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config=generation_config,
    system_instruction=system_instruction
)

# Inicializácia Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Načítanie histórie správ zo session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Zobrazenie histórie chatu v aplikácii
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Vstup od používateľa
if prompt := st.chat_input("Napíš správu..."):
    # Zobrazenie správy používateľa
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Uloženie správy používateľa do Supabase
    try:
        supabase.table("chat_history").insert({"role": "user", "content": prompt}).execute()
    except Exception as e:
        pass

    # Generovanie odpovede cez Gemini API
    with st.chat_message("assistant"):
        try:
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            # Uloženie odpovede asistenta do Supabase
            try:
                supabase.table("chat_history").insert({"role": "assistant", "content": response.text}).execute()
            except Exception as e:
                pass
                
        except Exception as e:
            st.error(f"Chyba pri generovaní odpovede: {e}")
