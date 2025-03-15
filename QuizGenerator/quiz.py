import re
from transformers import pipeline

# **Load a Better Model for Quiz Generation**
try:
    quiz_generator = pipeline("text-generation", model="gpt2-medium")
except Exception as e:
    print(f"Error loading model: {str(e)}")
    exit(1)

# **Badge hierarchy based on quiz score**
BADGES = [
    {"name": "Beginner", "min_score": 0},
    {"name": "Intermediate", "min_score": 4},
    {"name": "Advanced", "min_score": 7},
    {"name": "Expert", "min_score": 9},
    {"name": "Master", "min_score": 10}
]

def get_badge(score):
    """Assigns a badge based on the user's quiz score."""
    for badge in reversed(BADGES):
        if score >= badge["min_score"]:
            return badge["name"]
    return "Beginner"

def ask_personal_details():
    """Collects user details to personalize the quiz."""
    print("\n👤 Let's personalize your quiz experience!")
    name = input("What's your name? ").strip() or "Learner"
    
    # Validate age input
    while True:
        age = input("How old are you? ").strip()
        if not age:
            age = "25"  # Default age
            break
        if age.isdigit():
            break
        print("Please enter a valid number for age.")
    
    country = input("Where are you from? ").strip() or "Global"
    return {"name": name, "age": age, "country": country}

def get_user_field():
    """Asks the user for their field of interest."""
    while True:
        field = input("\n🌟 Enter your field of expertise (e.g., IT, Medicine, Finance, Sports): ").strip()
        if field:
            return field
        print("Please enter a field of expertise to continue.")

def get_user_role(field):
    """Asks the user for their specific role within the chosen field."""
    role = input(f"\n🎭 What is your role in {field}? (e.g., Software Developer, Doctor, Data Analyst): ").strip()
    if not role:
        return f"Professional in {field}"
    return role

def generate_quiz(user, field, role):
    """Generates a 10-question quiz using AI, considering personal details."""
    prompt = (
        f"Generate a 10-question multiple-choice quiz for {user['name']}, a {user['age']}-year-old from {user['country']}. "
        f"{user['name']} is a {role} in the {field} field. "
        f"Make the questions engaging and technically relevant to their profession. "
        f"Format each question as:\n"
        f"1. Question text?\n"
        f"A. Option A\n"
        f"B. Option B\n"
        f"C. Option C\n"
        f"D. Option D\n"
        f"Answer: Letter of correct option\n\n"
        f"Always provide exactly 4 options (A, B, C, D) for each question."
    )

    try:
        response = quiz_generator(prompt, max_length=600, temperature=0.7, top_p=0.9, do_sample=True)
        quiz_text = response[0]["generated_text"]
        questions = parse_quiz(quiz_text)
        
        if len(questions) < 5:
            fallback_questions = generate_fallback_questions(field, role)
            questions.extend(fallback_questions)
            questions = questions[:10]  # Limit to 10 questions maximum
            
        return questions
    except Exception as e:
        print(f"❌ Error generating quiz: {str(e)}")
        return generate_fallback_questions(field, role)

def parse_quiz(quiz_text):
    """Extracts structured questions from AI-generated text."""
    questions = []
    pattern = re.compile(r"(\d+\.\s*.*?\?)\s*(A\..*?)\s*(B\..*?)\s*(C\..*?)\s*(D\..*?)\s*Answer:\s*([A-D])", re.DOTALL)
    
    matches = pattern.findall(quiz_text)
    
    for match in matches:
        question = match[0].strip()
        options = [match[i].strip() for i in range(1, 5)]
        correct_answer = match[5].strip()
        questions.append({"question": question, "options": options, "answer": correct_answer})
    
    return questions

def generate_fallback_questions(field, role):
    """Generates fallback questions if the main generation fails."""
    fallback_questions = [
        {
            "question": f"1. Which of these skills is most important for a {role} in {field}?",
            "options": ["Technical knowledge", "Communication skills", "Problem-solving abilities", "Project management"],
            "answer": "C"
        },
        {
            "question": f"2. What technology trend is most likely to impact {field} in the next 5 years?",
            "options": ["Artificial Intelligence", "Blockchain", "Virtual Reality", "Quantum Computing"],
            "answer": "A"
        },
    ]
    return fallback_questions

def run_quiz(questions):
    """Runs the quiz, evaluates responses, and provides feedback."""
    if not questions:
        print("❌ No quiz questions available. Please try again.")
        return 0
        
    print("\n🧠 Starting your personalized quiz! Answer carefully.")
    score = 0

    for idx, q in enumerate(questions, 1):
        print(f"\n{q['question']}")
        for i, option in enumerate(q["options"]):
            print(f"{chr(65+i)}. {option}")

        while True:
            user_answer = input("\nEnter your answer (A/B/C/D): ").strip().upper()
            if user_answer in ["A", "B", "C", "D"]:
                break
            print("❌ Invalid input. Please enter A, B, C, or D.")

        if user_answer == q["answer"]:
            print("✅ Correct!")
            score += 1
        else:
            print(f"❌ Incorrect! The correct answer was: {q['answer']}")

    return score

def main():
    """Main function to run the Interactive AI Quiz Bot."""
    print("\n🤖 Welcome to the AI Quiz Bot!")

    user = ask_personal_details()
    field = get_user_field()
    role = get_user_role(field)

    print(f"\n👋 Hello {user['name']} from {user['country']}! Let's test your knowledge in {role} ({field}).")

    while True:
        print("\n⏳ Generating your personalized quiz...")
        questions = generate_quiz(user, field, role)

        if not questions:
            print("❌ Failed to generate a quiz. Let's try again.")
            continue

        print("\n✨ Quiz generated successfully!")
        score = run_quiz(questions)

        badge = get_badge(score)
        print(f"\n🏆 Your final score: {score}/10")
        print(f"🎖 You have earned the **{badge}** badge!")

        regenerate_choice = input("\n🔄 Do you want to retake the quiz? (yes/no): ").strip().lower()
        if regenerate_choice != "yes":
            print("\n🚀 Thank you for playing! Have a great day!")
            break

if __name__ == "__main__":
    main()
