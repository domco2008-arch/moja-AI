import streamlit as st
from google import genai
from google.genai import types
import uuid

# 1. Konfigurácia stránky
st.set_page_config(page_title="Moja Vlastná AI", page_icon="🤖", layout="wide")

# 2. Inicializácia pamäte (Session State)
if "chats" not in st.session_state:
    # Ukladá jednotlivé konverzácie: { chat_id: {"title": "Názov chatu", "messages": [...] } }
    st.session_state.chats = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# Funkcia na vytvorenie nového chatu
def create_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.chats[new_id] = {
        "title": "Nový chat",
        "messages": []
    }
    st.session_state.current_chat_id = new_id

# Ak ešte neexistuje žiadny chat, vytvoríme prvý
if not st.session_state.chats or st.session_state.current_chat_id is None:
    create_new_chat()

# 3. BOČNÝ PANEL (Sidebar)
with st.sidebar:
    st.title("🤖 Moja AI App")
    
    # Tlačidlo pre Nový chat
    if st.button("➕ Nový chat", use_container_width=True):
        create_new_chat()
        st.rerun()

    st.markdown("---")
    st.subheader("História chatov")

    # Zoznam minulých chatov
    for chat_id, chat_data in list(st.session_state.chats.items()):
        # Označenie aktuálne zvoleného chatu
        button_label = chat_data["title"]
        if chat_id == st.session_state.current_chat_id:
            button_label = f"💬 {button_label}"
        else:
            button_label = f"📁 {button_label}"
            
        if st.button(button_label, key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun()

    st.markdown("---")
    # Zadávanie API kľúča (vhodné, ak to budú používať iní)
    user_api_key = st.text_input(
        "Tvoj Gemini API Kľúč:", 
        type="password", 
        value="AQ.Ab8RN6IuscjLll1vRzi4CS9RhgiKy5jjtKzXCfmg08lFGD4DxQ", # Tvoj predvolený kľúč
        help="Sem si môže používateľ zadať vlastný kľúč."
    )

# 4. HLAVNÉ OKNO CHATU
current_chat = st.session_state.chats[st.session_state.current_chat_id]

# Zobrazenie histórie správ zvoleného chatu
for message in current_chat["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Vstup pre novú správu
if prompt := st.chat_input("Názov alebo otázka pre AI..."):
    if not user_api_key:
        st.error("Prosím, vlož API kľúč v ľavom menu.")
        st.stop()

    # Ak je to prvá správa v novom chate, nastavíme názov chatu podľa nej
    if len(current_chat["messages"]) == 0:
        current_chat["title"] = prompt[:20] + ("..." if len(prompt) > 20 else "")

    # Zobrazenie a uloženie správy používateľa
    st.chat_message("user").markdown(prompt)
    current_chat["messages"].append({"role": "user", "content": prompt})

    # Pripravenie správ pre Gemini
    contents = []
    for msg in current_chat["messages"]:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))

    # Zavolanie AI API
    client = genai.Client(api_key=user_api_key)
    with st.chat_message("assistant"):
        with st.spinner("AI premýšľa..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction="Si priateľský, múdry a nápomocný AI asistent. Odpovedaj prehľadne a vždy v slovenčine."
                    )
                )
                st.markdown(response.text)
                current_chat["messages"].append({"role": "assistant", "content": response.text})
                st.rerun()
            except Exception as e:
                st.error(f"Chyba: {e}")