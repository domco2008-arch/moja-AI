import streamlit as st
from google import genai
from supabase import create_client, Client

st.set_page_config(page_title="AI Chatbot", page_icon="🤖")
st.title("💬 Môj AI Chatbot")

# Načítanie kľúčov zo Streamlit Secrets
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Inicializácia klientov
client = genai.Client(api_key=GEMINI_API_KEY)
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

    # Generovanie odpovede cez Gemini so správnym streamovaním textu
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Volanie streamu
        response_stream = client.models.generate_content_stream(
            model="gemini-3.5-flash",
            contents=prompt,
            config={
                "system_instruction": "Odpovedaj vždy plynulo po slovensky."
            }
        )
        
        # Postupné skladanie čistého textu
        for chunk in response_stream:
            if chunk.text:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
                
        # Zobrazenie finálneho textu bez blikajúceho kurzora
        message_placeholder.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Uloženie odpovede asistenta do Supabase
    try:
        supabase.table("chat_history").insert({"role": "assistant", "content": full_response}).execute()
    except Exception as e:
        pass
