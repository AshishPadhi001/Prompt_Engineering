import streamlit as st
from Code import generate_code, explain_code, save_file, LANGUAGE_EXTENSIONS  # Import functions from code.py
import time

# Page configuration with custom theme and icon
st.set_page_config(
    page_title="CodeCraft AI - Generate & Explain Code",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4A90E2;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #5C5C5C;
        margin-bottom: 1rem;
    }
    .success-msg {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #D1F0E0;
        border-left: 5px solid #28A745;
        margin: 1rem 0;
    }
    .footer {
        text-align: center;
        color: #888888;
        font-size: 0.8rem;
        margin-top: 3rem;
    }
    .sidebar-content {
        padding: 1.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown("<div class='main-header'>🧠 CodeCraft AI</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Generate, Explain & Optimize Code with AI</div>", unsafe_allow_html=True)

# Sidebar configuration with more information
with st.sidebar:
    st.image("https://via.placeholder.com/150x80?text=CodeCraft+AI", width=200)
    st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
    st.subheader("📌 Navigation")
    option = st.radio("Choose an option:", ["Generate Code", "Explain Code", "About"])
    
    st.subheader("⚙️ Settings")
    show_advanced = st.checkbox("Show advanced options", False)
    
    if show_advanced:
        model_choice = st.selectbox(
            "AI Model",
            ["GPT-4", "CodeLlama", "Mixtral", "Claude"]
        )
        temperature = st.slider("Creativity (Temperature)", 0.0, 1.0, 0.7, 0.1)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("🔄 Last updated: March 2025")

# Main content
if option == "Generate Code":
    st.markdown("<div class='sub-header'>💻 Generate Code</div>", unsafe_allow_html=True)
    
    # Input fields with better organization
    col1, col2 = st.columns([3, 1])
    with col1:
        question = st.text_area(
            "📝 Enter your coding problem or requirements:",
            placeholder="E.g., Create a function that sorts a list of dictionaries by a specified key",
            height=150
        )
    with col2:
        language = st.selectbox("💻 Programming Language:", list(LANGUAGE_EXTENSIONS.keys()))
        
        if show_advanced:
            optimization = st.multiselect(
                "Optimize for:",
                ["Speed", "Memory Usage", "Readability", "Maintainability"],
                default=["Readability"]
            )
    
    # Generate button with loading animation
    if st.button("🔮 Generate Optimized Code", key="gen_btn", type="primary"):
        if question.strip():
            with st.spinner("AI is crafting your code..."):
                # Simulating delay for better UX
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                generated_code = generate_code(question, language)
                
                st.markdown("### 🎉 Generated Code:")
                st.code(generated_code, language=language.lower())
                
                # Copy to clipboard button (using JavaScript)
                st.markdown("""
                <button onclick="navigator.clipboard.writeText(`{}`)">
                    📋 Copy to clipboard
                </button>
                """.format(generated_code.replace('`', '\\`')), unsafe_allow_html=True)
                
                # Explanation toggle
                if st.checkbox("Show explanation of how the code works"):
                    with st.spinner("Generating explanation..."):
                        explanation = explain_code(generated_code, language)
                        st.info(explanation)
                
                # Save options
                st.markdown("### 💾 Save Your Code")
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    file_name = st.text_input("📁 File name (without extension):", "generated_code")
                with col2:
                    file_format = st.selectbox("📂 Format:", ["TXT", "DOCX", "PDF", "Language-specific"])
                with col3:
                    if st.button("💾 Save File", key="save_gen"):
                        if file_format == "Language-specific":
                            extension = LANGUAGE_EXTENSIONS.get(language, ".txt")
                            saved_file = save_file(generated_code, file_name, extension)
                        else:
                            saved_file = save_file(generated_code, file_name, file_format)
                        
                        if saved_file:
                            st.markdown(f"<div class='success-msg'>✅ Code saved as `{saved_file}`</div>", unsafe_allow_html=True)
        else:
            st.warning("⚠️ Please enter a coding problem before generating.")

elif option == "Explain Code":
    st.markdown("<div class='sub-header'>📖 Explain & Analyze Code</div>", unsafe_allow_html=True)
    
    # Layout for code explanation
    col1, col2 = st.columns([3, 1])
    with col1:
        user_code = st.text_area(
            "✍️ Paste your code below:",
            placeholder="Paste the code you want explained here...",
            height=250
        )
    with col2:
        language = st.selectbox("💻 Code Language:", list(LANGUAGE_EXTENSIONS.keys()))
        
        if show_advanced:
            explanation_detail = st.select_slider(
                "Detail Level",
                options=["Basic", "Intermediate", "Advanced", "Expert"],
                value="Intermediate"
            )
            
            explanation_focus = st.multiselect(
                "Focus on:",
                ["Algorithm", "Data Structures", "Performance", "Best Practices", "Security"],
                default=["Algorithm", "Best Practices"]
            )
    
    # Analysis options
    if st.button("🔍 Analyze & Explain Code", type="primary"):
        if user_code.strip():
            with st.spinner("AI is analyzing your code..."):
                # Create tabs for different types of output
                tab1, tab2, tab3 = st.tabs(["Explanation", "Optimization Suggestions", "Visualization"])
                
                # Explanation tab
                with tab1:
                    explanation = explain_code(user_code, language)
                    st.markdown("### 📝 Code Explanation:")
                    st.markdown(explanation)
                    
                    if st.button("💾 Save Explanation", key="save_expl"):
                        file_name = st.text_input("📁 File name:", "code_explanation")
                        file_format = st.selectbox("📂 Format:", ["TXT", "DOCX", "PDF", "MD"])
                        saved_file = save_file(explanation, file_name, file_format)
                        if saved_file:
                            st.markdown(f"<div class='success-msg'>✅ Explanation saved as `{saved_file}`</div>", unsafe_allow_html=True)
                
                # Optimization tab (placeholder)
                with tab2:
                    st.markdown("### 🚀 Optimization Suggestions:")
                    st.info("Based on the analysis, here are some ways to improve your code:")
                    st.code("# Optimized version would go here", language=language.lower())
                
                # Visualization tab (placeholder)
                with tab3:
                    st.markdown("### 📊 Code Visualization:")
                    st.info("Flow chart visualization would appear here")
        else:
            st.warning("⚠️ Please paste your code before analyzing.")

elif option == "About":
    st.markdown("<div class='sub-header'>ℹ️ About CodeCraft AI</div>", unsafe_allow_html=True)
    
    st.markdown("""
    ## What is CodeCraft AI?
    
    CodeCraft AI is an advanced tool that helps developers and students with code generation and explanation.
    Using state-of-the-art AI models, it can:
    
    - Generate optimized, well-commented code in multiple languages
    - Provide detailed explanations of complex code
    - Suggest improvements and optimizations
    - Help you learn programming concepts
    
    ## How to use
    
    1. **Generate Code**: Describe what you want the code to do, select a language, and let AI generate it for you
    2. **Explain Code**: Paste existing code to get a detailed explanation of how it works
    
    ## Supported Languages
    
    Python, JavaScript, Java, C++, Ruby, PHP, Go, Swift, and many more!
    """)
    
    st.info("This tool is for educational and productivity purposes. Always review AI-generated code before using it in production environments.")

# Footer
st.markdown("---")
st.markdown("<div class='footer'>🔨 Built with ❤️ using Streamlit | AI-powered by state-of-the-art language models 🧠</div>", unsafe_allow_html=True)