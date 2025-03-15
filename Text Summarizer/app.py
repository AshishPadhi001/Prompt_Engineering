import streamlit as st
import os

# Import the functions from your existing file
from summarizer import (
    summarize_text, 
    extract_text_from_pdf, 
    extract_text_from_docx, 
    fetch_text_from_url
)

# Set page configuration
st.set_page_config(
    page_title="TextCrunch",
    page_icon="📝",
    layout="wide"
)

# App title and description
st.title("TextCrunch")
st.markdown("Upload documents, paste text, or enter a URL to generate AI-powered summaries.")

# Create tabs for different input methods
tab1, tab2, tab3 = st.tabs(["Text Input", "File Upload", "URL"])

# Variables to store the input text
input_text = ""
is_text_ready = False

# Tab 1: Text Input
with tab1:
    input_text = st.text_area("Enter the text you want to summarize:", height=300)
    if input_text:
        is_text_ready = True

# Tab 2: File Upload
with tab2:
    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt"])
    
    if uploaded_file is not None:
        # Get file extension
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        
        with st.spinner("Extracting text from document..."):
            # Process based on file type
            if file_extension == ".pdf":
                input_text = extract_text_from_pdf(uploaded_file)
            elif file_extension == ".docx":
                input_text = extract_text_from_docx(uploaded_file)
            elif file_extension == ".txt":
                input_text = uploaded_file.getvalue().decode("utf-8")
            
            if input_text and not input_text.startswith("Error"):
                is_text_ready = True
                st.success("Text extracted successfully!")
            else:
                st.error(input_text if input_text else "Failed to extract text from the document.")

# Tab 3: URL Input
with tab3:
    url = st.text_input("Enter a URL to extract and summarize content:")
    use_selenium = st.checkbox("Use Selenium for JavaScript-rendered content")
    
    if url:
        if st.button("Fetch Content"):
            with st.spinner("Fetching content from URL..."):
                input_text = fetch_text_from_url(url, use_selenium)
                
                if input_text and not input_text.startswith("Error"):
                    is_text_ready = True
                    st.success("Content fetched successfully!")
                else:
                    st.error(input_text if input_text else "Failed to fetch content from the URL.")

# Summarization options (only shown if text is ready)
if is_text_ready:
    st.header("Summarization Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        summary_type = st.selectbox(
            "Summary Type:",
            ["standard", "concise", "detailed", "bullet_points"]
        )
        
        tone = st.selectbox(
            "Tone:",
            ["neutral", "professional", "casual", "academic"]
        )
        
        focus_areas = st.multiselect(
            "Focus Areas (Optional):",
            ["key points", "facts", "events", "people", "analysis", "conclusions"]
        )
    
    with col2:
        length = st.select_slider(
            "Length:",
            options=["very_short", "short", "medium", "long", "very_long"]
        )
        
        language = st.selectbox(
            "Output Language:",
            ["english", "spanish", "french", "german", "chinese", "japanese"]
        )
        
        exclude_areas = st.multiselect(
            "Exclude Areas (Optional):",
            ["background", "details", "technical jargon", "examples"]
        )
    
    reading_level = st.slider("Reading Level (1-10):", 1, 10, 5)
    
    # Preview input text
    with st.expander("Preview Input Text"):
        st.write(input_text[:1000] + ("..." if len(input_text) > 1000 else ""))
        st.text(f"Character count: {len(input_text)}")
    
    # Generate summary button
    if st.button("Generate Summary"):
        if len(input_text.strip()) < 100:
            st.error("Input text is too short (less than 100 characters). Please provide longer content.")
        else:
            with st.spinner("Generating summary..."):
                summary = summarize_text(
                    text=input_text,
                    summary_type=summary_type,
                    length=length,
                    tone=tone,
                    language=language,
                    focus_areas=focus_areas if focus_areas else None,
                    exclude_areas=exclude_areas if exclude_areas else None,
                    reading_level=reading_level
                )
            
            if summary and not summary.startswith("Error"):
                st.header("Summary")
                st.markdown(summary)
                
                # Download button for the summary
                st.download_button(
                    label="Download Summary",
                    data=summary,
                    file_name="summary.txt",
                    mime="text/plain"
                )
            else:
                st.error(summary if summary else "Failed to generate summary.")
else:
    st.info("Please provide text using one of the methods above to generate a summary.")

# Footer
st.markdown("---")
st.markdown("TextCrunch powered by Hugging Face's BART model")