import streamlit as st
import sys
import os
from io import StringIO
import contextlib

# Import functions from quiz.py
# Using this approach to avoid module import issues in Streamlit
from quiz import (
    get_badge, generate_quiz, parse_quiz, 
    generate_fallback_questions, BADGES
)

def main():
    st.set_page_config(
        page_title="Brain Booster", 
        page_icon="🤖",
        layout="wide"
    )
    
    # Application header with styling
    st.markdown("""
    <div style="text-align: center">
        <h1>🤖 AI Quiz Bot</h1>
        <p>Test your professional knowledge with a personalized AI-generated quiz</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = 'user_info'
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = []
    if 'user_details' not in st.session_state:
        st.session_state.user_details = {}
    if 'score' not in st.session_state:
        st.session_state.score = 0
    
    # Application flow
    if st.session_state.step == 'user_info':
        collect_user_details()
    elif st.session_state.step == 'quiz':
        show_quiz()
    elif st.session_state.step == 'results':
        show_results()
    
    # Sidebar with app info
    with st.sidebar:
        st.image("https://via.placeholder.com/150?text=Quiz+Bot", width=150)
        st.markdown("### About AI Quiz Bot")
        st.markdown("""
        This app uses AI to generate personalized quizzes based on your professional 
        background. Answer the questions to earn badges and test your knowledge!
        """)
        
        # Reset button
        if st.button("Start Over", type="primary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def collect_user_details():
    """Collect user information to personalize the quiz"""
    st.subheader("👤 Let's personalize your quiz experience!")
    
    with st.form("user_details_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("What's your name?", value="")
            age = st.number_input("How old are you?", min_value=5, max_value=120, value=25)
            country = st.text_input("Where are you from?", value="")
            
        with col2:
            field = st.text_input("Enter your field of expertise (e.g., IT, Medicine, Finance)", value="")
            role = st.text_input("What is your role in this field?", value="")
        
        submitted = st.form_submit_button("Generate My Quiz", type="primary")
        
        if submitted:
            if not field:
                st.error("Please enter your field of expertise to continue.")
            else:
                # Store user details
                user = {
                    "name": name if name else "Learner",
                    "age": str(age),
                    "country": country if country else "Global"
                }
                
                role_value = role if role else f"Professional in {field}"
                
                st.session_state.user_details = {
                    "user": user,
                    "field": field,
                    "role": role_value
                }
                
                # Generate quiz with loading indicator
                with st.spinner("⏳ Generating your personalized quiz..."):
                    try:
                        # Redirect stdout to capture any print statements from quiz.py
                        stdout_capture = StringIO()
                        with contextlib.redirect_stdout(stdout_capture):
                            questions = generate_quiz(user, field, role_value)
                        
                        if questions and len(questions) > 0:
                            st.session_state.questions = questions
                            st.session_state.user_answers = [""] * len(questions)
                            st.session_state.step = 'quiz'
                            st.rerun()
                        else:
                            st.error("Failed to generate quiz questions. Please try again.")
                    except Exception as e:
                        st.error(f"Error generating quiz: {str(e)}")

def show_quiz():
    """Display the quiz questions to the user"""
    user_details = st.session_state.user_details
    user = user_details["user"]
    
    st.subheader(f"🧠 Quiz for {user['name']} from {user['country']}")
    st.markdown(f"**Field:** {user_details['field']} | **Role:** {user_details['role']}")
    
    with st.form("quiz_form"):
        for i, question in enumerate(st.session_state.questions):
            q_num = i + 1
            st.markdown(f"### {q_num}. {question['question'].split('.', 1)[1].strip() if '.' in question['question'] else question['question']}")
            
            # Extract just the text part of each option (remove A., B., etc.)
            options = []
            for opt in question['options']:
                parts = opt.split('.', 1)
                options.append(parts[1].strip() if len(parts) > 1 else opt)
            
            # Display options as radio buttons
            answer = st.radio(
                f"Question {q_num}",
                options=["A", "B", "C", "D"],
                index=None,
                key=f"q_{i}",
                horizontal=True
            )
            
            # Display the actual option text
            cols = st.columns(2)
            with cols[0]:
                st.write(f"**A.** {options[0] if len(options) > 0 else ''}")
                st.write(f"**C.** {options[2] if len(options) > 2 else ''}")
            with cols[1]:
                st.write(f"**B.** {options[1] if len(options) > 1 else ''}")
                st.write(f"**D.** {options[3] if len(options) > 3 else ''}")
            
            if answer:
                st.session_state.user_answers[i] = answer
            
            st.markdown("---")
        
        # Submit button
        submitted = st.form_submit_button("Submit My Answers", type="primary")
        
        if submitted:
            if "" in st.session_state.user_answers:
                st.error("Please answer all questions before submitting.")
            else:
                # Calculate score
                score = sum(1 for i, ans in enumerate(st.session_state.user_answers) 
                           if ans == st.session_state.questions[i]['answer'])
                st.session_state.score = score
                st.session_state.step = 'results'
                st.rerun()

def show_results():
    """Display quiz results and badge"""
    user = st.session_state.user_details["user"]
    score = st.session_state.score
    badge = get_badge(score)
    
    # Colorful header
    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;">
        <h2>🏆 Quiz Results for {user['name']}</h2>
        <h3>You scored {score}/{len(st.session_state.questions)}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Display badge with appropriate styling
    badge_colors = {
        "Beginner": "#FFC107",
        "Intermediate": "#2196F3",
        "Advanced": "#4CAF50",
        "Expert": "#9C27B0",
        "Master": "#F44336"
    }
    
    badge_color = badge_colors.get(badge, "#808080")
    
    st.markdown(f"""
    <div style="display: flex; justify-content: center; margin: 30px 0;">
        <div style="background-color: {badge_color}; color: white; padding: 15px 40px; 
                  border-radius: 50px; font-size: 24px; font-weight: bold;">
            {badge} Badge Earned!
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress bar for score visualization
    st.progress(score / len(st.session_state.questions))
    
    # Show badge requirements
    st.markdown("### Badge Requirements")
    cols = st.columns(len(BADGES))
    for i, badge_info in enumerate(BADGES):
        with cols[i]:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; border-radius: 5px; 
                      background-color: {badge_colors.get(badge_info['name'], '#808080')}; 
                      color: white;">
                <strong>{badge_info['name']}</strong><br>
                {badge_info['min_score']}+ points
            </div>
            """, unsafe_allow_html=True)
    
    # Question review
    st.markdown("### Review Your Answers")
    for i, question in enumerate(st.session_state.questions):
        user_answer = st.session_state.user_answers[i]
        correct_answer = question['answer']
        is_correct = user_answer == correct_answer
        
        expander_label = f"Question {i+1}: " + ("✅ Correct" if is_correct else "❌ Incorrect")
        with st.expander(expander_label):
            # Extract question without the number prefix
            q_text = question['question'].split('.', 1)[1].strip() if '.' in question['question'] else question['question']
            st.markdown(f"**{q_text}**")
            
            # Display options with highlighting
            for j, opt in enumerate(question['options']):
                # Extract option text without the letter prefix
                opt_text = opt.split('.', 1)[1].strip() if '.' in opt else opt
                option_letter = chr(65 + j)  # A, B, C, D
                
                if option_letter == correct_answer:
                    st.markdown(f"**{option_letter}. {opt_text}** ✅ (Correct Answer)")
                elif option_letter == user_answer and not is_correct:
                    st.markdown(f"**{option_letter}. {opt_text}** ❌ (Your Answer)")
                else:
                    st.markdown(f"{option_letter}. {opt_text}")
    
    # Actions
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Take Another Quiz", type="primary"):
            # Reset quiz but keep user info
            st.session_state.step = 'user_info'
            st.session_state.questions = []
            st.session_state.user_answers = []
            st.session_state.score = 0
            st.rerun()
    
    with col2:
        # Download results as text
        results_text = generate_results_text(
            st.session_state.user_details,
            score,
            badge,
            st.session_state.questions,
            st.session_state.user_answers
        )
        
        st.download_button(
            "Download Results",
            data=results_text,
            file_name=f"quiz_results_{user['name']}.txt",
            mime="text/plain"
        )

def generate_results_text(user_details, score, badge, questions, user_answers):
    """Generate a text summary of the quiz results"""
    user = user_details["user"]
    
    text = f"""
==============================================
AI QUIZ BOT - RESULTS SUMMARY
==============================================

Name: {user['name']}
Age: {user['age']}
Country: {user['country']}
Field: {user_details['field']}
Role: {user_details['role']}

SCORE: {score}/{len(questions)}
BADGE EARNED: {badge}

==============================================
QUESTION REVIEW
==============================================
"""
    
    for i, question in enumerate(questions):
        q_num = i + 1
        user_answer = user_answers[i]
        correct_answer = question['answer']
        is_correct = user_answer == correct_answer
        
        q_text = question['question'].split('.', 1)[1].strip() if '.' in question['question'] else question['question']
        text += f"\nQ{q_num}. {q_text}\n"
        
        for j, opt in enumerate(question['options']):
            opt_text = opt.split('.', 1)[1].strip() if '.' in opt else opt
            option_letter = chr(65 + j)
            
            marker = ""
            if option_letter == correct_answer:
                marker = " (CORRECT ANSWER)"
            elif option_letter == user_answer and not is_correct:
                marker = " (YOUR ANSWER)"
                
            text += f"{option_letter}. {opt_text}{marker}\n"
            
        text += f"\nYour answer: {user_answer}, Correct answer: {correct_answer}\n"
        text += f"Result: {'Correct' if is_correct else 'Incorrect'}\n"
        text += "----------------------------------------------\n"
        
    return text

if __name__ == "__main__":
    main()