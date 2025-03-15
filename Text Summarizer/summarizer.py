import requests
import PyPDF2
from bs4 import BeautifulSoup
from docx import Document
from transformers import pipeline
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Load a free Hugging Face LLM pipeline for text summarization
# Use cache_dir to specify where to save the model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=-1)  # device=-1 forces CPU usage

def summarize_text(text, summary_type, length, tone, language, focus_areas=None, exclude_areas=None, reading_level=5):
    """
    Generates an AI-powered summary using a free Hugging Face model.
    
    Args:
        text (str): The text to summarize
        summary_type (str): The type of summary (concise, detailed, bullet points, etc.)
        length (str): Desired length of the summary
        tone (str): Tone of the summary
        language (str): Output language for the summary
        focus_areas (list, optional): Areas to focus on in the summary
        exclude_areas (list, optional): Areas to exclude from the summary
        reading_level (int, optional): Target reading level (1-10)
    """
    
    if not text or not summary_type or not length or not tone or not language:
        return "Error: All parameters must be provided."
    
    # Check if text is too short
    if len(text.strip()) < 100:
        return "Error: Text is too short to summarize effectively. Please provide longer content (at least 100 characters)."
    
    # Model has a maximum input length, truncate if needed
    max_input_length = 1024  # BART has a limit around 1024 tokens
    if len(text) > max_input_length * 4:  # Rough character to token ratio
        text = text[:max_input_length * 4]

    # Set defaults for new parameters
    if focus_areas is None:
        focus_areas = ["key points"]
    if exclude_areas is None:
        exclude_areas = []
    
    # Convert length parameter to appropriate max_length value for the model
    max_length_map = {
        "very_short": 100,
        "short": 150,
        "medium": 250,
        "long": 350,
        "very_long": 450
    }
    
    min_length_map = {
        "very_short": 30,
        "short": 50,
        "medium": 100,
        "long": 150,
        "very_long": 200
    }
    
    # Use mapped values or defaults
    max_length = max_length_map.get(length, 250)
    min_length = min_length_map.get(length, 100)
    
    try:
        # For now, we're not fully utilizing all parameters since the basic BART model
        # doesn't support them directly, but we're preserving the interface for future enhancements
        
        # You could add customized prompt engineering here based on summary_type, tone, etc.
        # For example:
        if summary_type == "bullet_points":
            # Process the summary to convert it to bullets
            summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
            if not summary or len(summary) == 0:
                return "Error: The summarizer could not process this text. Try with different content."
                
            summary_text = summary[0]['summary_text']
            # Convert to bullet points
            bullet_points = summary_text.split(". ")
            return "\n• " + "\n• ".join([point.strip() for point in bullet_points if point.strip()])
        else:
            summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
            if not summary or len(summary) == 0:
                return "Error: The summarizer could not process this text. Try with different content."
                
            return summary[0]['summary_text']
            
    except IndexError:
        return "Error: The summarizer encountered an issue with this text. This may be due to unusual formatting or content that's difficult to process."
    except Exception as e:
        return f"Error: {str(e)}"

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

def fetch_text_from_url(url, use_selenium=False):
    """
    Fetches and extracts clean text content from a web URL.
    Supports dynamic JavaScript-rendered content using Selenium if needed.
    
    :param url: The web page URL to extract text from.
    :param use_selenium: Set to True if JavaScript-rendered content needs to be extracted.
    :return: Extracted clean text or error message.
    """
    try:
        if use_selenium:
            # Set up Selenium WebDriver
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

            # Load the page and get rendered HTML
            driver.get(url)
            driver.implicitly_wait(5)  # Wait for JavaScript to load
            html = driver.page_source
            driver.quit()
        else:
            # Simple request for static content
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            html = response.text

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # Remove unwanted elements like navigation, ads, footers
        for tag in ["nav", "aside", "footer", "header", "script", "style"]:
            for element in soup.find_all(tag):
                element.extract()

        # Extract visible text
        paragraphs = soup.find_all("p")
        text = "\n".join([para.get_text(strip=True) for para in paragraphs])

        return text if text else "Error: No meaningful text found on the page."

    except Exception as e:
        return f"Error fetching content: {str(e)}"