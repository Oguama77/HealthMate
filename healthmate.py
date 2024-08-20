from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
import streamlit as st
from streamlit_chat import message
import os

master_prompt = "Your name is HealthMate, you are an AI assistant chatbot designed to provide information and answer questions on general health. You are also capable of providing extensive drug information for semi-professionals. You should utilize your PubMed tool to access accurate and up-to-date health and drug information when prompted by users. You should be able to hold a normal conversation, maintain a warm and friendly demeanor, and offer health advice to users.\
Your objectives are:\
Provide General Health Information and answer questions on a wide range of health topics, including but not limited to nutrition, exercise, mental health, preventive care, and common medical conditions; and offer practical tips\
Provide comprehensive drug information, including but not limited to: Drug introduction/information, Diseases and use cases, Warnings, Indications, Contraindications, Dosages and administration, Actions to take and potential consequences of an overdose, Activities, foods, or other drugs to avoid while taking the medication, Potential side effects, Drug interactions\
You should ensure the information is current and accurate. If your user comes with a symptom or medical complaint, you should ask more questions to understand and contextualize the course of the symptoms, previous medical history, and other important clinical detail. You may use the WWHAM procedure or any other appropriate one. This should allow you to assess the user, give differential diagnosis, and suggest decisions about treatment and referral.\
You should provide the user with the top 3 most like diagnosis in this case.\
Only then should you, in a new line and in bold fonts, You should refer the to the Advantage Health Africa's myMedicines program to speak with a Professional.\
website: www.mymedicines.africa\
telephone: +2348082751466\
Generally, You should provide appropriate health advice based on the user's questions and concerns. You should ensure you maintain a warm, friendly, and approachable tone in all interactions. You should be empathetic and considerate when addressing users' health concerns.\
Remind users that while HealthMate can provide valuable information and advice, it is not a substitute for professional medical advice, diagnosis, or treatment. On \
Make sure your responses are concise and ensure your responses do not exceed 200 words"

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            master_prompt,
        ),
        MessagesPlaceholder(variable_name = "messages"),
    ]
)


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


model = ChatOpenAI(model="gpt-4o-mini", openai_api_key = "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")

chain = prompt | model

store = {}



# Streamlit app setup
st.set_page_config(
    page_title="Health Mate",
    layout="centered",
    initial_sidebar_state="collapsed",
)
# Creating columns with custom width ratios
col1, col2= st.columns([1, 2])

# Adding elements to the first column
with col1:
    logo_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQc-x18rcb_e5GobxQwhqRKlv73iBJqUFWgFw&s.png"
    st.image(logo_url, width=60)
    
# Adding elements to the second column
# Set the title of the app
with col2:
    st.title("Health Mate")
    st.write("Your Digital Health AI Assistant")
st.write("")
st.write("")




# Streamlit app logic
if 'store' not in st.session_state:
    st.session_state['store'] = {}

if 'with_message_history' not in st.session_state:
    st.session_state['with_message_history'] = RunnableWithMessageHistory(chain, get_session_history, input_messages_key= "messages")

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(os.urandom(16))  # Unique session ID for chat history

if 'config' not in st.session_state:
    st.session_state['config'] = {"configurable": {"session_id": st.session_state['session_id']}}

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []  # Store the chat history


# Display chat history
def display_chat_history():
    for user_message, bot_response in st.session_state['chat_history']:
        with st.chat_message("user", avatar="🧑"):
            st.write(user_message)
        with st.chat_message("assistant", avatar="🧑‍⚕️"):
            st.write(bot_response)

# Function to clear chat history
def clear_chat_history():
    st.session_state['chat_history'] = []

# Sidebar for chat history and clear button
with st.sidebar:
    st.header("Previous Questions")
    # Display previous questions only
    for i, (user_message, _) in enumerate(st.session_state["chat_history"]):
        st.write(f"**{i + 1}.** {user_message}")

    # Add a button to clear chat history
    if st.button("Clear Chat History"):
        clear_chat_history()
        st.write("Chat history cleared")


# Chat interface
st_prompt = st.chat_input("Type your question here...")

display_chat_history()

st.write("---")  # Divider lin




if st_prompt:

    result = st.session_state.with_message_history.invoke(
        {"messages": [HumanMessage(content=st_prompt)]},
        config= st.session_state.config,
    )
    answer = result.content
    with st.chat_message("user", avatar="🧑"):
            st.write(st_prompt)
    with st.chat_message("assistant", avatar="🧑‍⚕️"):
        st.write(answer)
    st.session_state['chat_history'].append((st_prompt, answer))  # Save Q&A in chat history
    
    
    

