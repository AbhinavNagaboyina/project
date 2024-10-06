import streamlit as st
import os
from PIL import Image
import openai
import torch
from torchvision import transforms
from image_train import load_model, load_image, MedicalImageDataset, predict_label, generate_medical_info_turbo, get_class_mapping
from symptom_analysis import analyze_symptom
from test import create_vector_embedding_from_file,process_query,summarize_document
import base64
import pdfplumber 
import docx
from customized_bot import CustomizedBot
import shutil

# Set up OpenAI API key
open_api_key = ""

# Function for chatbot responses
def generate_chatbot_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful medical assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7
    )
    return response['choices'][0]['message']['content']

# Custom CSS for removing top space, styling the page with Eagle Lake font, input boxes & buttons
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Eagle+Lake&display=swap');
    
    body {
        background-color: #f0f0f5;
        color: #333333;
        font-family: 'Arial', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Eagle Lake', cursive;
        color: #1a73e8;
        font-weight: 600;
        text-align: center;
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    img {
        width: 100%;
        max-height: 350px;
        object-fit: cover;
        border-radius: 8px;
    }

    .custom-input {
        border: 2px solid #4CAF50;
        border-radius: 12px;
        padding: 12px;
        width: 100%;
        margin-bottom: 20px;
        font-size: 16px;
        font-family: 'Arial', sans-serif;
    }
    
    .custom-button {
        background-color: #1a73e8;
        color: white;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 10px 2px;
        cursor: pointer;
        border-radius: 12px;
        border: none;
    }
    
    .custom-button:hover {
        background-color: #0066cc;
    }

    .no-top-margin {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    </style>
    """, unsafe_allow_html=True)

# Load section banner images
def load_image_as_base64(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def display_image_and_content(image_path, content):
    """Display image and content after the header."""
    st.markdown(f"""
        <img src="data:image/jpeg;base64,{load_image_as_base64(image_path)}" alt="Image">
    """, unsafe_allow_html=True)
    st.write(content)

# Paths for small images to be placed beside the headings
image_analysis_small = r"C:\Users\paill\Downloads\Image.jpg"
symptom_analysis_small = r"C:\Users\paill\Downloads\symptom.jpg"
chatbot_small = r"C:\Users\paill\Downloads\chatbot.jpg"
document_analysis_small = r"C:\Users\paill\Downloads\document_analysis.jpg"
home_image = r"C:\Users\paill\Downloads\AI powered heathcare.jpg"

# Sidebar navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.selectbox("Choose a section", ["Home", "Image Analysis", "Symptom Analysis", "Medical Chatbot", "Document Analysis"])

# Home Page
if app_mode == "Home":
    st.title("Welcome to AI Healthcare App")
    display_image_and_content(home_image, """
        This app provides several features like:
        - Image Analysis for medical images
        - Symptom Analysis based on input
        - Medical Chatbot to answer your health-related queries
        - Document Analysis to analyze and interact with medical documents

        Use the sidebar to navigate through the features.
    """)

# Image Analysis Page
if app_mode == "Image Analysis":
    st.title("Image Analysis")
    display_image_and_content(image_analysis_small, "Upload and analyze medical images like X-rays or CT scans.")
    
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    @st.cache_resource
    def load_model_and_dataset():
        model_save_path = r"C:\Users\paill\Coding\Projects_for_resume\AI_Healthcare_App\Code\models\Image_analysis\saved_model"
        dataset = MedicalImageDataset(img_folder=r"C:\Users\paill\Coding\Projects_for_resume\AI_Healthcare_App\data\Image_analysis", transform=transform)
        idx_to_class = get_class_mapping(dataset)
        model = load_model(dataset)
        model.load_state_dict(torch.load(model_save_path))
        model.eval()
        return model, dataset, idx_to_class

    model, dataset, idx_to_class = load_model_and_dataset()

    uploaded_file = st.file_uploader("Upload an image (e.g., X-ray, MRI, CT scan)", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        try:
            image = load_image(uploaded_file)
            predicted_label, probabilities = predict_label(model, image, idx_to_class)
            st.write(f"**Predicted Label**: {predicted_label}")
            medical_info = generate_medical_info_turbo(predicted_label)
            st.write(f"**Medical Information**: {medical_info}")
            
        except Exception as e:
            st.error(f"Error processing the image: {e}")
    else:
        st.write("Please upload an image to get started.")

# Symptom Analysis Page
if app_mode == "Symptom Analysis":
    st.title("Symptom Analysis")
    display_image_and_content(symptom_analysis_small, "Analyze medical symptoms to provide insights and possible conditions.")
    
    symptoms_input = st.text_input("Enter symptoms (comma separated)", "", key="symptoms_input", help="Enter symptoms to analyze")
    
    if st.button("Analyze Symptoms"):
        symptoms_list = [s.strip() for s in symptoms_input.split(",") if s.strip()]
        analysis_result = analyze_symptom(symptoms_list)
        st.write("**Symptoms Analysis Result**:", analysis_result)

# Medical Chatbot Page
if app_mode == "Medical Chatbot":
    st.title("Medical Chatbot")
    display_image_and_content(chatbot_small, "Ask medical questions and get assistance from the AI-powered chatbot.")
    
    user_question = st.text_input("Ask a medical question:", "", key="chatbot_input", help="Enter a question")
    
    if st.button("Get Response"):
        if user_question:
            response = generate_chatbot_response(user_question)
            st.write("**Chatbot Response**:", response)
        else:
            st.write("Please enter a question.")

# Document Analysis Page
if app_mode == "Document Analysis":
    st.title("Document Analysis")
    class BotManager:
        if 'bots' not in st.session_state:
            st.session_state['bots'] = {}

    def save_bot(self, name, details):
        st.session_state['bots'][name] = details

    def delete_bot(self, name):
        if name in st.session_state['bots']:
            bot_details = st.session_state['bots'][name]
            # Reset or adjust selected_bot_details
            if bot_details['type'] == 'Customized Bot' and 'input_dir' in bot_details:
                directory = bot_details['input_dir']
                if os.path.exists(directory) and os.path.isdir(directory):
                    shutil.rmtree(directory)  # Remove the directory
            del st.session_state['bots'][name]

            if 'selected_bot_details' in st.session_state and st.session_state['selected_bot_details']['name'] == name:
                if st.session_state['bots']:
                    # Optional: Select a previous bot, e.g., the first in the list
                    st.session_state['selected_bot_details'] = next(iter(st.session_state['bots'].values()))
                else:
                    # If no bots are left, clear the selection
                    del st.session_state['selected_bot_details']
    
    def display_bots(self):
        for name, details in list(st.session_state['bots'].items()):
            if st.sidebar.button(f"Click to start the {name} bot", key=f"start_{name}"):
                st.session_state['selected_bot_details'] = details
            if st.sidebar.button(f"Delete {name}", key=f"delete_{name}"):
                self.delete_bot(name)

    def initialize_new_bot(self):
        # Reset the input field in the session state
        st.session_state['user_input'] = ''

    botmanager = BotManager()
    def st_centered_text(text: str):
        st.markdown(f"<h1 style='text-align: center; color: white;'><big><b><u>{text} 🤖🗣️</u></b></big></h1>", unsafe_allow_html=True)

    def st_bigtext(text: str):
        st.markdown(f"<h1 style='text-align: left; color: white;'<b>{text}</b></h1>", unsafe_allow_html=True)

    with st.sidebar:
        st_bigtext("Create your own Chatbot:")
        if st.button("Create New Bot"):
            st.session_state['show_create_bot_form'] = True

        if st.session_state.get('show_create_bot_form', False):
            with st.form("bot_creation_form", clear_on_submit=True):
                name = st.text_input("Name (Unique identifier for each bot):")
                context_prompt = st.text_area("Context Prompt:")
                documents = st.file_uploader("Upload additional knowledge bases for the bot:", accept_multiple_files=True)
                create_button = st.form_submit_button("Create Bot")
                if create_button:
                    if not name:
                        st.warning("Please fill in all required fields.")
                    else:
                        if documents:
                            DATA_DIR = os.path.join('files', name)
                            if not os.path.exists(DATA_DIR):
                                os.makedirs(DATA_DIR)
                            for document in documents:
                                file_path = os.path.join(DATA_DIR, document.name)
                                with open(file_path, "wb") as f:
                                    f.write(document.getbuffer())
                            input_dir = DATA_DIR
                            bot_details = {'name': name, 'type': 'Customized Bot','context_prompt': context_prompt, 'input_dir': input_dir}
                            botmanager.save_bot(name, bot_details)
                            botmanager.initialize_new_bot()
                    st.session_state['show_create_bot_form'] = False
                
        botmanager.display_bots()

    if 'selected_bot_details' in st.session_state:
        botmanager.initialize_new_bot()  # Clear input field when a bot is selected
        selected_bot_details = st.session_state['selected_bot_details']
        chat_bot = CustomizedBot(selected_bot_details['name'], selected_bot_details['context_prompt'], selected_bot_details['input_dir'])
        chat_bot.run()

    