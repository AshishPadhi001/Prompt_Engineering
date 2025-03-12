import openai
import os
import PyPDF2
import requests
from bs4 import BeautifulSoup
from docx import Document
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

def summarize_text(text, summary_type, length, tone, language):
    """Generates an AI-powered summary while ensuring accuracy and meaning preservation."""
    
    if not text or not summary_type or not length or not tone or not language:
        return "Error: All parameters must be provided."

    prompt = f"""
    You are an expert text summarizer with a deep understanding of context, key ideas, and meaningful compression. 
    Your goal is to create a **{summary_type}** summary that accurately conveys the core message of the provided text **without distorting its meaning**.

    ### Guidelines:
    - Ensure the summary **retains the original intent, key facts, and context**.
    - Do not omit **critical details** that impact understanding.
    - The summary should be **{length}**, adapting dynamically to content complexity rather than a fixed number of sentences.
    - Format the summary as per the selected **{summary_type}**:
      - **Concise** → Provide a **brief** yet **informative** summary.
      - **Detailed** → Provide a **well-structured** paragraph covering all essential points.
      - **Bullet Points** → List key takeaways clearly and concisely.
    - Maintain the selected tone (**{tone}**) and ensure the output is natural and readable.
    - Generate the summary in **{language}**.

    ### Input Text:
    {text}

    ### Output:
    Provide the summarized version below in the requested format.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3  # Low randomness for precise summaries
        )
        return response["choices"][0]["message"]["content"].strip()

    except openai.error.OpenAIError as e:
        return f"API Error: {str(e)}"
    except Exception as e:
        return f"Unexpected Error: {str(e)}"

def extract_text_from_pdf(pdf_file):
    """Extracts raw text from an uploaded PDF file using PyPDF2."""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip() if text else "Error: Could not extract text from PDF."
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def extract_text_from_docx(docx_file):
    """Extracts raw text from an uploaded DOCX file using python-docx."""
    try:
        doc = Document(docx_file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip() if text else "Error: Could not extract text from DOCX."
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def fetch_text_from_url(url):
    """Fetches and extracts text content from a given web URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract visible text from the webpage
        paragraphs = soup.find_all("p")
        text = "\n".join([para.get_text() for para in paragraphs])
        
        return text.strip() if text else "Error: No text found on the page."
    except Exception as e:
        return f"Error fetching content: {str(e)}"
