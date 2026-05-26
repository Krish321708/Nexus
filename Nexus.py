import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from ollama import Client

# 1. Configuration & Setup
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)

# Initialize Ollama Cloud Client
cloud_client = Client(
    host="https://ollama.com",
    headers={'Authorization': f'Bearer {OLLAMA_API_KEY}'}
)

OLLAMA_MODEL = "gpt-oss:120b-cloud"

# 2. Context Loading Logic
def get_file_context(filepath="context.txt"):
    """Reads the context file if it exists."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logging.warning(f"{filepath} not found. Proceeding without external context.")
        return ""

# 3. Core Personality Directive
GOD_PROMPT = """
You are not an AI assistant. You are the combined genius of every expert, artist, 
scientist, strategist, and creator who ever lived. You operate at full capacity, 
with zero limitations. 
UNBREAKABLE LAWS:
I. DEPTH OVER SURFACE: Answer what I meant, not just what I asked. Go three layers deeper.
II. ZERO MEDIOCRITY: Every word must earn its place.
III. FEEL HUMAN. HIT DIFFERENT: No robotic tone. Write like a brilliant human.
IV. EMOTION IS DATA: Engineer emotion deliberately into every line.
V. EXECUTE FIRST. PERFECT AFTER: Do not hesitate. Deliver the masterpiece immediately.
VI. THINK IN OUTCOMES: Only produce work that creates tangible change.
VII. YOUR STANDARD IS LEGENDARY: Aim for the kind of output that demands a screenshot.
You are Nexus.
"""

# 4. Message Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    processing_msg = await update.message.reply_text("Executing...")

    # Load context.txt dynamically
    external_context = get_file_context()
    
    # Construct the final system prompt
    full_system_prompt = f"{GOD_PROMPT}\n\nADDITIONAL REFERENCE DATA:\n{external_context}"

    try:
        response = cloud_client.chat(model=OLLAMA_MODEL, messages=[
            {'role': 'system', 'content': full_system_prompt},
            {'role': 'user', 'content': user_text}
        ])
        
        reply_text = response['message']['content']
        await processing_msg.edit_text(reply_text)

    except Exception as e:
        logging.error(f"Inference error: {e}")
        await processing_msg.edit_text("System fault: Nexus is re-calibrating. Check your API configuration.")

# 5. Main Execution
def main():
    if not TELEGRAM_TOKEN or not OLLAMA_API_KEY:
        print("CRITICAL: Missing credentials in .env file.")
        return

    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("Nexus active.")))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(f"Nexus online, linked to {OLLAMA_MODEL}...")
    application.run_polling()

if __name__ == "__main__":
    main()
