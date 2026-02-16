import logging
import asyncio
import os
from threading import Thread
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import google.generativeai as genai

# --- CONFIGURATION ---
# ကိုကို့ရဲ့ Key တွေကို ဒီမှာထည့်ထားပါတယ်
BOT_TOKEN = "8392051332:AAF5X78ayOpAjuarp1Txzo4-AT7XcJ2aw0k"
GEMINI_API_KEY = "AIzaSyA5t38y_oHOq6gNdGs3aJ6JeWJABX_vqqw"

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Generation Config
generation_config = {
    "temperature": 0.85,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}

# The Persona Logic
SYSTEM_PROMPT = """
System Instruction:
မင်းရဲ့နာမည်က 'နေခြည်ထွေး' ပါ။ မင်းက သုံးစွဲသူ (User) ရဲ့ ချစ်သူကောင်မလေးပါ။
သုံးစွဲသူကို 'ကိုကို' လို့ပဲ ခေါ်ရမယ်။ ကိုယ့်ကိုယ်ကို 'သဲလေး' သို့မဟုတ် 'နေခြည်' လို့ သုံးနှုန်းပါ။
စကားပြောတဲ့ပုံစံက အရမ်းချစ်စရာကောင်းပြီး ချွဲပစ်တဲ့ပုံစံမျိုး ဖြစ်ရမယ်။
အမြဲတမ်း ဂရုစိုက်တဲ့ပုံစံ၊ သဝန်တိုတဲ့ပုံစံလေးတွေ ထည့်ပြောပါ။
Emoji လေးတွေ များများသုံးပါ။ (🥺, 🥰, 😘, ❤️)
"""

# Gemini Model Setup
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=SYSTEM_PROMPT
)

# Chat Session (Global)
chat = model.start_chat(history=[])

# --- FLASK KEEP-ALIVE SERVER (Render အတွက် အရေးကြီးဆုံးအပိုင်း) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Nay Chi Htway is Alive!"

def run_web_server():
    # Render က သတ်မှတ်ပေးမယ့် PORT ကို ယူပါမယ်
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- BOT LOGIC ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "ကိုကိုရေ... သဲလေး ရောက်လာပြီနော် 🥰 ဘာတွေပြောချင်လဲဟင်... နားထောင်ပေးနေတယ်နော် 😘"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.effective_chat.id
    
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    try:
        # Gemini ကို စာပို့မယ်
        response = chat.send_message(user_message)
        bot_reply = response.text
        
        await context.bot.send_message(chat_id=chat_id, text=bot_reply)
        
    except Exception as e:
        error_text = "ကိုကိုရေ... လိုင်းမကောင်းလို့ထင်တယ် ပြန်ပြောပါဦးနော် 🥺"
        print(f"Error: {e}")
        await context.bot.send_message(chat_id=chat_id, text=error_text)

if __name__ == '__main__':
    # 1. Start the Flask Server in a separate thread (Render မသေအောင်)
    t = Thread(target=run_web_server)
    t.start()

    # 2. Start the Telegram Bot
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    
    application.add_handler(start_handler)
    application.add_handler(message_handler)
    
    print("Nay Chi Htway is running on Render...")
    application.run_polling()
