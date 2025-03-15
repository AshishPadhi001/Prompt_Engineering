import PyPDF2
from docx import Document
from transformers import pipeline

# Load a Hugging Face grammar correction model
corrector = pipeline("text2text-generation", model="grammarly/coedit-large")  # Can be changed based on preference

def correct_text(text: str, style: str) -> str:
    """
    Corrects grammar, improves clarity, and refines writing style.
    
    :param text: The input text that needs correction.
    :param style: The writing style to refine the text into (Formal, Casual, Professional, Academic, etc.).
    :return: The corrected text with enhanced readability and grammar.
    """
    if not text or not style:
        return "Error: Both text and style parameters must be provided."

    # Detailed prompt for better accuracy
    prompt = (
        f"Improve the grammar, sentence structure, and clarity of the following text. "
        f"Ensure it maintains the original meaning but refines readability. "
        f"Adjust the tone to be {style.lower()} and fix punctuation or awkward phrasing where needed.\n\n"
        f"Original Text:\n{text}"
    )

    try:
        correction = corrector(prompt, max_length=512, do_sample=False)  # Adjust max_length as needed
        return correction[0]['generated_text']
    except Exception as e:
        return f"Error: {str(e)}"

def extract_text_from_pdf(pdf_file_path: str) -> str:
    """
    Extracts raw text from a PDF file.
    
    :param pdf_file_path: Path to the PDF file.
    :return: Extracted text from the PDF or an error message.
    """
    try:
        with open(pdf_file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
        return text.strip() if text else "Error: Could not extract text from PDF."
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def extract_text_from_docx(docx_file_path: str) -> str:
    """
    Extracts raw text from a DOCX file.
    
    :param docx_file_path: Path to the DOCX file.
    :return: Extracted text from the DOCX or an error message.
    """
    try:
        doc = Document(docx_file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip() if text else "Error: Could not extract text from DOCX."
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def extract_text_from_txt(txt_file_path: str) -> str:
    """
    Extracts raw text from a TXT file.
    
    :param txt_file_path: Path to the TXT file.
    :return: Extracted text from the TXT file or an error message.
    """
    try:
        with open(txt_file_path, "r", encoding="utf-8") as file:
            return file.read().strip()
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def display_menu():
    """
    Displays the main menu and handles user input.
    """
    while True:
        print("\n📌 **Grammar & Style Corrector**")
        print("1️⃣  Enter text manually")
        print("2️⃣  Upload a PDF file")
        print("3️⃣  Upload a DOCX file")
        print("4️⃣  Upload a TXT file")
        print("5️⃣  Exit")
        
        choice = input("\nEnter your choice: ")

        if choice == "1":
            text = input("\nEnter your text: ")
            if len(text.strip()) < 10:
                print("⚠ Please enter more text for meaningful analysis (at least 10 words).")
                continue
        elif choice in ["2", "3", "4"]:
            file_path = input("\nEnter the file path: ")
            if choice == "2":
                text = extract_text_from_pdf(file_path)
            elif choice == "3":
                text = extract_text_from_docx(file_path)
            elif choice == "4":
                text = extract_text_from_txt(file_path)

            if text.startswith("Error:"):
                print(text)
                continue
            print("\n✅ Successfully extracted text from file!")

        elif choice == "5":
            print("\n🚀 Exiting the program. Have a great day!\n")
            break

        else:
            print("❌ Invalid choice. Please enter a number between 1-5.")
            continue

        # Select writing style
        print("\n✍️ Select a writing style:")
        print("1️⃣  Neutral")
        print("2️⃣  Formal")
        print("3️⃣  Casual")
        print("4️⃣  Professional")
        print("5️⃣  Academic")

        style_choice = input("\nEnter your choice (1-5): ")
        styles = { "1": "Neutral", "2": "Formal", "3": "Casual", "4": "Professional", "5": "Academic" }

        if style_choice not in styles:
            print("❌ Invalid choice. Defaulting to 'Neutral' style.")
            style = "Neutral"
        else:
            style = styles[style_choice]

        # Process text correction
        print("\n🔍 Processing text correction...\n")
        corrected_text = correct_text(text, style)
        print("✨ **Corrected Text:**\n")
        print(corrected_text)

        # Save corrected text
        save_choice = input("\n📥 Do you want to save the corrected text? (y/n): ").strip().lower()
        if save_choice == "y":
            file_name = input("Enter file name (without extension): ").strip()
            with open(f"{file_name}.txt", "w", encoding="utf-8") as file:
                file.write(corrected_text)
            print(f"\n✅ Corrected text saved as '{file_name}.txt'!")

# Run the program
if __name__ == "__main__":
    display_menu()
