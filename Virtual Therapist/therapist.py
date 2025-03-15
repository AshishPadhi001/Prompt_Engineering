import torch
import datetime
import os
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline


MODEL_NAME = "t5-small"  # Alternative lightweight model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)


# **Sentiment Analysis & Toxicity Filter**
sentiment_analyzer = pipeline("sentiment-analysis")
toxicity_classifier = pipeline("text-classification", model="facebook/roberta-hate-speech-dynabench-r4-target")

# **Session Log (For Memory Retention)**
session_log = []
conversation_memory = []
user_details = {}


def ask_user_details():
    """Collects user details to personalize therapy sessions."""
    print("\n👤 Let's personalize your therapy session.")
    name = input("What's your name? ").strip() or "Friend"
    age = input("How old are you? ").strip() or "Unknown"
    location = input("Where are you from? ").strip() or "Somewhere"
    reason = input("What brings you here today? (e.g., stress, anxiety, personal growth) ").strip()

    global user_details
    user_details = {"name": name, "age": age, "location": location, "reason": reason}

    print(f"\n👋 Hello {name} from {location}! I'm here to support you. Let's talk.")


def analyze_sentiment(user_input):
    """Uses a sentiment analysis model to detect user emotions."""
    result = sentiment_analyzer(user_input)[0]
    return result["label"], result["score"]


def detect_toxicity(user_input):
    """Detects if a response is toxic, offensive, or inappropriate."""
    toxicity_result = toxicity_classifier(user_input)[0]
    return toxicity_result["label"] == "hate_speech", toxicity_result["score"]


def generate_emotional_prompt(user_input):
    """Adjusts response tone based on detected sentiment."""
    sentiment, confidence = analyze_sentiment(user_input)

    emotion_responses = {
        "POSITIVE": f"I'm happy to hear that, {user_details.get('name', 'Friend')}! What’s been making you feel this way?",
        "NEGATIVE": f"I'm really sorry you're feeling this way, {user_details.get('name', 'Friend')}. You're not alone. 💙 Want to talk more?",
        "NEUTRAL": f"I'm here to listen, {user_details.get('name', 'Friend')}. Tell me more about it."
    }

    return emotion_responses.get(sentiment, "I'm here to listen and support you.")


def save_conversation():
    """Saves the conversation log to a file."""
    if not os.path.exists("therapy_sessions"):
        os.makedirs("therapy_sessions")

    filename = f"therapy_sessions/therapy_session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        for line in session_log:
            file.write(line + "\n")
    print(f"\n💾 Your session has been saved as `{filename}`.")


def chat_with_therapist():
    """Runs an AI-powered therapist chatbot with context retention."""
    ask_user_details()
    print("\n🤖 **Serenity AI** – I'm here to listen and help. Type 'exit' to end the session.")

    global conversation_memory
    conversation_memory = []

    while True:
        # **User Input**
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\n🧘‍♂️ Take care! If you ever need to talk, I'm here. 💙")
            save_choice = input("💾 Do you want to save this conversation? (yes/no): ").strip().lower()
            if save_choice in ["yes", "y"]:
                save_conversation()
            break

        # **Detect Toxic or Harmful Speech**
        is_toxic, toxicity_score = detect_toxicity(user_input)
        if is_toxic:
            print("\n⚠️ AI detected harmful language. Let's focus on positive healing. 💙")
            session_log.append(f"You: [REDACTED TOXIC CONTENT]")
            continue

        # **Generate Emotionally Intelligent Prompt**
        emotional_prompt = generate_emotional_prompt(user_input)

        # **Store Conversation History**
        conversation_memory.append(f"You: {user_input}")
        session_log.append(f"You: {user_input}")

        # **Ensure Context Retains Last 6 Messages**
        conversation_memory = conversation_memory[-6:]

        # **Tokenize Input & Add Emotional Prompt**
        input_text = " ".join(conversation_memory) + f" {emotional_prompt} {user_input}"
        input_ids = tokenizer(input_text, return_tensors="pt")

        # **Generate AI Response with Context Awareness**
        with torch.no_grad():
            response_ids = model.generate(
                input_ids["input_ids"],
                max_length=150,  # Prevents overly long responses
                temperature=0.7,  # Encourages variety in responses
                top_p=0.92,  # Uses nucleus sampling for natural replies
                do_sample=True  # Enables better randomness
            )

        # **Decode AI Response**
        response = tokenizer.decode(response_ids[0], skip_special_tokens=True)

        # **Check for Toxicity in AI Response**
        is_toxic, toxicity_score = detect_toxicity(response)
        if is_toxic:
            response = "I'm here to help in a supportive and respectful way. Let's focus on healing. 💙"

        # **Enhance Response to Sound More Empathetic**
        response = response.replace("I am", "I'm").replace("do not", "don't").replace("you are", "you're")

        print(f"\n🧑‍⚕️ Therapist: {response}")

        # **Update Chat Memory & Log**
        conversation_memory.append(f"Therapist: {response}")
        session_log.append(f"Therapist: {response}")

        # **Limit to Last 6 Messages**
        conversation_memory = conversation_memory[-6:]


if __name__ == "__main__":
    chat_with_therapist()
