import streamlit as st
from dotenv import load_dotenv
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient
import re

# Load environment variables
load_dotenv(override=True)
ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
ai_key = os.getenv('AI_SERVICE_KEY')

# Define project names and example questions
project_names = ["CrewAi", "LangGraph"]
example_questions = {
    "CrewAi": ["How does CrewAi work?", "What are the advantages of CrewAi?", "How does CrewAi integrate with other systems?"],
    "LangGraph": ["What does LangGraph do?", "How is a graph structured in LangGraph?", "What are the use cases of LangGraph?"]
}

# Initialize chat selection
if "selected_project" not in st.session_state:
    st.session_state.selected_project = project_names[0]

# UI to select QnA project
st.title("Azure Question Answering Chat")
col1, col2 = st.columns([3, 1])

with col1:
    selected_project = st.radio("Selecciona un proyecto:", project_names, horizontal=True)
    st.session_state.selected_project = selected_project

# Initialize Azure Question Answering client
credential = AzureKeyCredential(ai_key)
ai_client = QuestionAnsweringClient(endpoint=ai_endpoint, credential=credential)

# Initialize chat history per project
if "messages" not in st.session_state:
    st.session_state.messages = {project: [] for project in project_names}

# Chat display with scroll
with col1:
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages[st.session_state.selected_project]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

# Function to handle user input

def handle_user_input(question):
    st.session_state.messages[st.session_state.selected_project].append({"role": "user", "content": question})
    
    try:
        response = ai_client.get_answers(
            question=question,
            project_name=st.session_state.selected_project,
            deployment_name=os.getenv('QA_DEPLOYMENT_NAME')
        )
        
        if response.answers:
            answer = response.answers[0].answer  # Best response
            confidence = response.answers[0].confidence
            source = response.answers[0].source or "Desconocida"
            
            reply = f"**Respuesta:** {answer}\n\n**Confianza:** {confidence:.2f}\n\n**Fuente:** {source}"
        else:
            reply = "No se encontró una respuesta relevante."
        
    except Exception as ex:
        reply = f"Error: {str(ex)}"
    
    st.session_state.messages[st.session_state.selected_project].append({"role": "assistant", "content": reply})
    st.rerun()

# Example questions section
with col2:
    st.write("### Preguntas de ejemplo")
    for question in example_questions[st.session_state.selected_project]:
        if st.button(question):
            handle_user_input(question)

# Chat input box
user_question = st.chat_input("Escribe tu mensaje aquí...")
if user_question:
    handle_user_input(user_question)
