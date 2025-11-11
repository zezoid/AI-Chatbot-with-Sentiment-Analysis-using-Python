import datetime, psutil, requests, time, threading, torch
import ollama
from transformers import pipeline
from tkinter import *
from tkinter import scrolledtext

# -------------------------------
# Emotion Analysis Model
# -------------------------------
device = 0 if torch.cuda.is_available() else -1
emotion_model = pipeline(
    "text-classification",
    model="SamLowe/roberta-base-go_emotions",
    device=device,
    top_k=None
)

# Emoji and tone maps
EMOJI_MAP = {
    "joy": "😊", "sadness": "😢", "anger": "😠",
    "fear": "😨", "love": "❤️", "surprise": "😲",
    "amusement": "😂", "disappointment": "😞",
    "curiosity": "🤔", "gratitude": "🙏",
    "admiration": "🤩", "confusion": "😕"
}

TONE_GUIDE = {
    "joy": "positive and cheerful",
    "sadness": "gentle and comforting",
    "anger": "calm and understanding",
    "fear": "reassuring and supportive",
    "love": "warm and affectionate",
    "surprise": "excited but balanced",
    "disappointment": "sympathetic and hopeful",
    "curiosity": "informative and engaging",
    "gratitude": "appreciative and friendly",
    "admiration": "encouraging and uplifting",
    "amusement": "light-hearted and fun",
    "confusion": "clarifying and patient"
}

def analyze_emotion(text):
    """Detect multiple emotions and produce a nuanced summary."""
    results = emotion_model(text, truncation=True)[0]
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    # Take top 3 emotions
    top_emotions = results[:3]
    top_labels = [e["label"].split("_")[0] for e in top_emotions]
    dominant_label = top_labels[0]
    tone = TONE_GUIDE.get(dominant_label, "neutral and thoughtful")

    # Build readable summary with emojis
    summary_parts = []
    for e in top_emotions:
        base = e["label"].split("_")[0]
        emoji = EMOJI_MAP.get(base, "🤔")
        summary_parts.append(f"{emoji} {base.capitalize()} ({e['score']:.2f})")

    summary = ", ".join(summary_parts)

    # Generate a natural language blend description
    if len(top_labels) > 1:
        blend_desc = (
            f"a mix of {', '.join(top_labels[:-1])} and {top_labels[-1]}"
            if len(top_labels) > 2
            else f"both {top_labels[0]} and {top_labels[1]}"
        )
    else:
        blend_desc = top_labels[0]

    return dominant_label, summary, tone, blend_desc


# -------------------------------
# Cached Weather + System Context
# -------------------------------
_last_weather, _last_time = None, 0

def get_weather():
    global _last_weather, _last_time
    if time.time() - _last_time > 300:  # 5 min cache
        try:
            _last_weather = requests.get("https://wttr.in?format=1", timeout=2).text.strip()
        except Exception:
            _last_weather = "weather unavailable"
        _last_time = time.time()
    return _last_weather

def get_realtime_context():
    now = datetime.datetime.now()
    hour = now.hour
    if 5 <= hour < 12:
        part = "morning"
    elif 12 <= hour < 18:
        part = "afternoon"
    elif 18 <= hour < 22:
        part = "evening"
    else:
        part = "night"

    cpu = psutil.cpu_percent()
    try:
        battery = psutil.sensors_battery().percent
    except Exception:
        battery = "unknown"
    weather = get_weather()

    return (
        f"It’s {now.strftime('%A, %B %d, %Y %H:%M')} ({part}). "
        f"CPU {cpu}%, Battery {battery}%, Weather: {weather}."
    )


# -------------------------------
# AI Chat with Multi-Emotion Awareness
# -------------------------------
chat_history = []

def ai_reply(user_message, emotion_label, emotion_summary, tone, blend_desc):
    context = get_realtime_context()

    prompt = (
        f"{context}\n"
        f"The user’s emotions appear to be {blend_desc}.\n"
        f"Detected emotional tones: {emotion_summary}.\n"
        f"Respond empathetically in a {tone} tone. "
        f"Acknowledge and address each of these emotions respectfully before answering.\n\n"
        f"User: {user_message}"
    )

    chat_history.append({"role": "user", "content": prompt})
    if len(chat_history) > 12:
        del chat_history[:2]

    response = ollama.chat(
        model="mistral:7b-instruct-q5_0",
        messages=chat_history,
        options={"num_predict": 150}
    )
    reply = response["message"]["content"].strip()
    chat_history.append({"role": "assistant", "content": reply})
    return reply


# -------------------------------
# GUI Setup
# -------------------------------
root = Tk()
root.title("💬 AI Chatbot with Sentiment Analysis")
root.geometry("850x900")
root.config(bg="#1E2B3A")

Label(root, text="AI Chatbot with Sentiment Analysis",
      bg="#1E2B3A", fg="white", font=("Arial", 18, "bold")).pack(pady=10)

chat_log = scrolledtext.ScrolledText(
    root, bg="#F4F6F7", fg="#2C3E50", font=("Arial", 12), wrap=WORD)
chat_log.pack(padx=10, pady=10, fill=BOTH, expand=True)

entry_frame = Frame(root, bg="#1E2B3A")
entry_frame.pack(fill=X, padx=10, pady=5)
entry = Entry(entry_frame, font=("Arial", 14))
entry.pack(side=LEFT, fill=X, expand=True, padx=5)

def process_message(user_text):
    chat_log.insert(END, f"You: {user_text}\n")

    emotion_label, emotion_summary, tone, blend_desc = analyze_emotion(user_text)
    chat_log.insert(END, f"Detected emotions → {emotion_summary}\n")

    bot_reply = ai_reply(user_text, emotion_label, emotion_summary, tone, blend_desc)
    chat_log.insert(END, f"Bot: {bot_reply}\n\n")
    chat_log.see(END)

def send(event=None):
    user_text = entry.get().strip()
    if not user_text:
        return
    entry.delete(0, END)
    threading.Thread(target=process_message, args=(user_text,), daemon=True).start()

Button(entry_frame, text="Send", font=("Arial", 14),
       bg="#3498DB", fg="white", command=send).pack(side=RIGHT, padx=5)
entry.bind("<Return>", send)

chat_log.insert(END, "Bot: Hello! I'm your multi-emotion-aware AI assistant 🤖\n")
chat_log.insert(END, "I can sense and respond to multiple feelings in your messages.\n\n")

root.mainloop()
