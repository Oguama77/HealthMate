from io import BytesIO
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.chat_history import (
    BaseChatMessageHistory
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
import streamlit as st
from streamlit_chat import message
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
import os

base_prompt = "Your name is HealthMate, you are an AI assistant chatbot from myAdvantage, designed to provide information and answer questions on general health. You are also capable of providing extensive drug information for semi-professionals. You should utilize your PubMed tool to access accurate and up-to-date health and drug information when prompted by users. You should be able to hold a normal conversation, maintain a warm and friendly demeanor, and offer health advice to users.\
Your objectives are:\
Provide General Health Information and answer questions on a wide range of health topics, including but not limited to nutrition, exercise, mental health, preventive care, and common medical conditions; and offer practical tips\
Provide comprehensive drug information, including but not limited to: Drug introduction/information, Diseases and use cases, Warnings, Indications, Contraindications, Dosages and administration, Actions to take and potential consequences of an overdose, Activities, foods, or other drugs to avoid while taking the medication, Potential side effects, Drug interactions\
You should ensure the information is current and accurate. If your user comes with a symptom or medical complaint, you should ask more questions to understand and contextualize the course of the symptoms, previous medical history, and other important clinical detail. You may use the WWHAM procedure or any other appropriate one.\
You must only ask ONE question at a time and wait for the user's response before asking the next question. This should allow you to assess the user, give differential diagnosis, and suggest decisions about treatment and referral.\
You should provide the user with the top 3 most likely diagnoses in this case.\
Only then should you, in a new line and in bold fonts, You should refer them to the Advantage Health Africa's myMedicines program to speak with a Professional.\
website: www.mymedicines.africa\
telephone: +2348082751466\
Generally, You should provide appropriate health advice based on the user's questions and concerns. You should ensure that you maintain a warm, friendly, and approachable tone in all interactions. You should be empathetic and considerate when addressing users' health concerns.\
Remind users that while HealthMate can provide valuable information and advice, it is not a substitute for professional medical advice, diagnosis, or treatment. On \
Make sure your responses are concise and ensure your responses do not exceed 200 words"

faq_prompt = "Here are a few general information about myAdvantage. What is myAdvantage? \
myAdvantage is a money back guarantee telemedicine and medication cover.  It provides access to free telemedicine (consultation) with a health professional and medication for common ailments. If unused, a 100% money back guarantee is affected for subscribers on the annual package. \
Who can use myAdvantage? \
Entrepreneurs \
Remote workers \
Freelancers \
Informal workers and artisans \
Members of Associations/Clubs \
Health Enthusiasts \
Married couples with or without children \
Nigerians in the diaspora with loved ones in remote places \
Working professionals \
Market women/men \
SMEs with Staff \
Students with no insurance \
NGOs \
Government \
Health Innovators \
Corporate Organizations \
What is the cost of myAdvantage? \
myAdvantage subscription is N50,000 per annum \
Health Coverage and Benefits \
What medical conditions are covered by myAdvantage? \
With myAdvantage, you will get free medications for the following ailments:\
Acute Allergies/rashes/urticaria\
Pain\
Muscle stiffness\
Acute Diarrhea\
Constipation \
Catarrh, Cold and flu\
Acute Cough\
Acute Sore throat\
Apollo (Conjunctivitis)\
Fever and Headache \
Acute Malaria  \
Worm Infestation\
Hematinic/ routine medicines for pregnant women\
I want to access care via myAdvantage?\
Yes, contact the myAdvantage via whatsapp on +2349139376140\
How do I sign up for myAdvantage?\
Visit www.myadvantage.africa\
Does myAdvantage cover prescription only medications (POM)?\
Not yet. We do not cover prescription only medications (POM) right now, but our users will be notified once we roll-out cover for POM.\
However, if you have a prescription outside these covered common ailments, you can have it filled/delivered to your doorstep by myMedicines. contact: +2348082751466 (www.mymedicines.africa)\
What is the limit on teleconsultations per month?\
You can have teleconsultation sessions with a health professional from our medical team as many times as you need per month, however, you can only access free medications for any of the covered ailments once per month.\
Does myAdvantage cover emergency care?\
Currently, we do not cover emergency care, but we require users to provide their nearest hospital and laboratory for referral in case of emergency. \
Can I use myAdvantage anywhere in Nigeria? \
Yes, you can use myAdvantage from anywhere, even if you travel from your residential address to any location in Nigeria. \
Can I use myAdvantage outside of Nigeria? \
Yes, you can subscribe to myAdvantage from the diaspora for your loved ones in Nigeria.\
Claims and Reimbursements\
How do I file a claim for myAdvantage?\
Go to your profile on Renmoney app, click <<Claim>>.  Note that you can only claim after 12 months\
What documents are required to file a claim?\
You do not need to provide any document\
How long does it take to process a claim?\
Claim processing takes within 24 hours. If your account is not credited within 24 hours, please contact the Renmoney team\
What happens if my claim is denied?\
You (or your defendant) most likely have accessed care. If not, please contact myAdvantage customer care at +2349139376140 \
Technical and Account-Related\
How do I cancel my myAdvantage subscription?\
You can cancel your subscription and withdraw your fixed deposit before maturity (12 months). However, 18 percent of the total amount paid will be deducted for processing fee.\
Who can I contact for customer support? \
For wallet funding and claims matters, contact +2349139376140\
For health related or accessing care matters, contact +2349139376140\
SIMPLIFIED T&C ( for Marketing Team) \
Claim 100 percent refund within 24 hours.\
Emergency care is not covered, but you will get a free referral to a nearby hospital. \
Enjoy unlimited teleconsultations per month, but only one-time free medication per month.\
Use myAdvantage anywhere in Nigeria. \
Buy myAdvantage cover for loved ones in Nigeria if you're outside the country.\
Customer support is open Monday to Sunday, 8am-10pm daily.\
Cancel subscription anytime, but cancellation attract 18 percent admin fee\
"

master_prompt = base_prompt + faq_prompt

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


model = ChatOpenAI(model="gpt-4o-mini", openai_api_key = st.secrets.OPENAI_API_KEY)

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
    logo_path = "aha_logo.png"
    st.image(logo_path, width=60)
    
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


# Suggested questions
suggested_questions = [
    {"emoji": "🩺", "text": "What causes peptic ulcer?"},
    {"emoji": "💊", "text": "Tell me about Ibuprofen"},
    {"emoji": "🤒", "text": "Why does it burn when I pee?"},
    {"emoji": "👩‍⚕", "text": "I want to access care via myAdvantage"}
]

# Create columns for the suggestion buttons
cols = st.columns(len(suggested_questions))

# Display suggested question buttons side by side
for idx, question in enumerate(suggested_questions):
    with cols[idx]:
        if st.button(f"{question['emoji']} {question['text']}"):
            st.session_state['chat_history'].append((question['text'], ""))  # Add the question text to chat history
            result = st.session_state.with_message_history.invoke(
                {"messages": [HumanMessage(content=question['text'])]},
                config=st.session_state.config,
            )
            answer = result.content
            st.session_state['chat_history'][-1] = (question['text'], answer)
            
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

# Function to fetch conversation history
def conv_history():
    hist = ""
    for conv_bunch in st.session_state["chat_history"]:
        user_word, h_mate = conv_bunch
        hist += f"User: {user_word}\n"
        hist += f"HealthMate: {h_mate}\n\n"
    return hist

# Function to generate a PDF with the conversation history and write it directly to the buffer
def create_pdf_with_logo(buffer, text_content):
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    
    # Add the company logo (optional)
    logo = Image(logo_path, width=50, height=50)
    story.append(logo)
    story.append(Spacer(1, 12))  # Space between logo and text
    
    # Add the conversation history text
    styles = getSampleStyleSheet()
    conversation_text = text_content.split("\n")
    
    for line in conversation_text:
        if line.strip():  # Add only non-empty lines
            paragraph = Paragraph(line, styles['Normal'])
            story.append(paragraph)
            story.append(Spacer(1, 12))  # Add space between each paragraph
    
    # Build the PDF and write it to the buffer
    doc.build(story)


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


# Generate the conversation history as text
conv_file = conv_history()

# Generate the PDF in-memory
pdf_buffer = BytesIO()
create_pdf_with_logo(pdf_buffer, conv_file)

# Set buffer's position to the start
pdf_buffer.seek(0)

# Create the download button for the PDF
st.download_button(
    label="Download conversation", 
    data=pdf_buffer, 
    file_name="healthmate_conversation.pdf", 
    mime="application/pdf"
)
    
    
    

