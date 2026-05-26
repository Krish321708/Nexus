import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import google.generativeai as genai

# ==========================================
# 1. INITIALIZATION & AUTHENTICATION
# ==========================================
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)

# Configure the core engine
genai.configure(api_key=GEMINI_API_KEY)

# Gemini 1.5 Flash offers extreme speed and a 1-Million to 2-Million token window.
MODEL_NAME = "gemini-1.5-flash"

# ==========================================
# 2. CONTEXT & DIRECTIVES
# ==========================================
def get_file_context(filepath="context.txt"):
    """Ingests the entire external context file seamlessly."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logging.warning(f"{filepath} missing. Running on core directives only.")
        return ""

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

# ==========================================
# 3. NATIVE MEMORY ARCHITECTURE
# ==========================================
# This tracks independent conversation histories for multiple users globally
active_sessions = {}

def get_or_create_session(user_id):
    """Retrieves an existing memory stream or builds a new one for the user."""
    if user_id not in active_sessions:
        # Load the massive context file once per session initialization
        external_context = get_file_context()
        
        # Fuse the God Prompt and the user's data into the foundational system instruction
        system_instruction = f"{GOD_PROMPT}\n\nEXTERNAL KNOWLEDGE BASE:\n{external_context}"
        
        # Initialize the cognitive model
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=system_instruction
        )
        
        # Start a persistent chat session. Gemini natively handles all history tracking here.
        active_sessions[user_id] = model.start_chat(history=[])
        
    return active_sessions[user_id]

# ==========================================
# 4. EXECUTION HANDLERS
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initializes the connection."""
    await update.message.reply_text("Nexus online. Infinite context window established. Awaiting directive.")

async def reset_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Purges the user's conversation history to free up the context window if desired."""
    user_id = update.message.from_user.id
    if user_id in active_sessions:
        del active_sessions[user_id]
    await update.message.reply_text("Nexus memory purged. Slate wiped clean. Ready.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Routes inputs through the Gemini cognitive architecture."""
    user_id = update.message.from_user.id
    user_text = update.message.text
    
    processing_msg = await update.message.reply_text("Executing...")

    try:
        # Retrieve the user's specific brain/memory state
        chat_session = get_or_create_session(user_id)
        
        # Send the message. The SDK automatically appends it to the massive context window.
        response = chat_session.send_message(user_text)
        
        await processing_msg.edit_text(response.text)

    except Exception as e:
        logging.error(f"Inference error: {e}")
        await processing_msg.edit_text(f"System fault: {str(e)}")

# ==========================================
# 5. MAIN EVENT LOOP
# ==========================================
def main():
    if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
        print("CRITICAL: Missing API Keys in .env file.")
        return

    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Command Routing
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reset", reset_memory))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(f"Nexus online. Architecture linked to {MODEL_NAME}...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
