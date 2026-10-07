import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

# Logging setup
logging.basicConfig(level=logging.INFO)

# Railway environment variables se credentials uthane ke liye
API_ID = int(os.getenv("API_ID", "26754022"))
API_HASH = os.getenv("API_HASH", "1a0b65e7a4d48e08687c732bdc0f2cc4")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8657555427:AAHfQ_nliOVuF4-Idcgnm9OrFIDW8G4pzEI")

# Pyrogram Client Initialize
app = Client(
    "dragon_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# User states ko track karne ke liye dictionary
user_states = {}

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    welcome_text = (
        "🔥 **DRAGON BOT ACTIVATED** 🔥\n\n"
        "Welcome bhai! Main tera personal automation bot hoon.\n\n"
        "📜 **Available Commands:**\n"
        "• `/start` - Bot ko start karein aur menu dekhein\n"
        "• `/extract` - Token se login karke batches extract karein\n"
        "• `/upload` - TXT file bhej kar upload process start karein"
    )
    await message.reply_text(welcome_text)

@app.on_message(filters.command("extract"))
async def extract_command(client, message: Message):
    user_states[message.from_user.id] = {"step": "waiting_for_token"}
    await message.reply_text("🔑 Apne account ka token ya session string yahan bhejein:")

@app.on_message(filters.command("upload"))
async def upload_command(client, message: Message):
    user_states[message.from_user.id] = {"step": "waiting_for_txt"}
    await message.reply_text("📁 Ab apni `.txt` file yahan bhejein jisse upload process start ho sake:")

@app.on_message(filters.text & ~filters.command(["start", "extract", "upload"]))
async def handle_text_inputs(client, message: Message):
    user_id = message.from_user.id
    state = user_states.get(user_id, {})
    
    # Step 1: Token milne ke baad batches ki list dikhana
    if state.get("step") == "waiting_for_token":
        token = message.text
        user_states[user_id] = {"step": "waiting_for_batch_choice", "token": token}
        
        batches_list = (
            "✅ **Login Successful!**\n\n"
            "Yeh rahe available batches:\n"
            "1. Batch A - Python Automation\n"
            "2. Batch B - Video Processing\n"
            "3. Batch C - Advanced Bot Development\n\n"
            "👉 Jo batch chahiye uska serial number (jaise `1`, `2` ya `3`) yahan reply karein:"
        )
        await message.reply_text(batches_list)
        
    # Step 2: Batch ka serial number milne par TXT file generate karke bhejna
    elif state.get("step") == "waiting_for_batch_choice":
        choice = message.text.strip()
        file_name = f"batch_{choice}_links.txt"
        
        # Sample TXT file content create kar rahe hain
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(f"https://example.com/video_stream_1_batch_{choice}\n")
            f.write(f"https://example.com/video_stream_2_batch_{choice}\n")
        
        await message.reply_document(
            document=file_name, 
            caption=f"📄 Yeh lo bhai batch {choice} ki TXT file!"
        )
        
        # Cleanup local file
        if os.path.exists(file_name):
            os.remove(file_name)
            
        user_states.pop(user_id, None)

@app.on_message(filters.document)
async def handle_documents(client, message: Message):
    user_id = message.from_user.id
    state = user_states.get(user_id, {})
    
    if state.get("step") == "waiting_for_txt" or (message.document.file_name and message.document.file_name.endswith(".txt")):
        file_path = await message.download()
        await message.reply_text("🚀 TXT file successfully mil gayi hai! Upload process background mein start kar diya gaya hai...")
        
        # File read karke upload operations yahan perform kiye ja sakte hain
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Yahan apna upload logic add kar sakta hai
        
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
            
        user_states.pop(user_id, None)
    else:
        await message.reply_text("⚠️ Pehle `/upload` command type karein, uske baad `.txt` file bhejein.")

if __name__ == "__main__":
    print("Dragon Bot is starting...")
    app.run()
