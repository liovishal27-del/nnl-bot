import os
import asyncio
import subprocess
import aiofiles
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.environ.get("API_ID", "26754022"))
API_HASH = os.environ.get("API_HASH", "1a0b65e7a4d48e08687c732bdc0f2cc4")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8657555427:AAHfQ_nliOVuF4-Idcgnm9OrFIDW8G4pzEI")
TARGET_CHAT_ID = os.environ.get("TARGET_CHAT_ID", "-1003796501870")

app = Client(
    "nnl_batch_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start_handler(client: Client, message: Message):
    await message.reply_text(
        "🔥 **NNL Downloader Bot** Active!\n\n"
        "Mujhe `.txt` file bhej, main ise `nnl_aio.exe` tool ke through process karke channel par bhej dunga."
    )

@app.on_message(filters.document)
async def handle_document(client: Client, message: Message):
    if not message.document.file_name.endswith(".txt"):
        await message.reply_text("❌ Bhai, sirf valid `.txt` file bhej!")
        return

    status_msg = await message.reply_text("📥 Text file download ho rahi hai...")
    file_path = await message.download()
    
    await status_msg.edit_text("⚙️ Tool run ho raha hai, batch extraction shuru hai...")

    try:
        # Yahan hum tumhari exe file ya batch script ko subprocess ke zariye call karenge
        # Jaise ki tool file_path ko input leta ho:
        # command = f"nnl_aio.exe {file_path}"
        
        # Agar Linux/Railway par run kar rahe ho toh wine ya direct execution jo bhi tool support kare:
        process = await asyncio.create_subprocess_shell(
            f"wine nnl_aio.exe {file_path}" if os.name != "nt" else f"nnl_aio.exe {file_path}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            await status_msg.edit_text(f"❌ Tool execution error:\n`{stderr.decode()[:300]}`")
            return

        await status_msg.edit_text("✅ Extraction complete! Files upload ki ja rahi hain...")

        # Downloader ke baad jo output files bani hongi unhe upload karne ka logic
        # Maan lo output directory me files save hoti hain:
        output_dir = "downloads" # Apne tool ke output folder ke hisab se change kar lena
        if os.path.exists(output_dir):
            files = os.listdir(output_dir)
            for file in files:
                f_path = os.path.join(output_dir, file)
                if os.path.isfile(f_path):
                    chat_id = TARGET_CHAT_ID if TARGET_CHAT_ID else message.chat.id
                    if file.endswith((".mp4", ".mkv")):
                        await client.send_video(chat_id=chat_id, video=f_path, caption=f"📁 {file}")
                    else:
                        await client.send_document(chat_id=chat_id, document=f_path, caption=f"📄 {file}")
                    os.remove(f_path)

        await status_msg.edit_text("🎉 Sabhi lectures aur PDFs successfully upload ho gaye!")

    except Exception as e:
        await status_msg.edit_text(f"❌ Error: `{str(e)}`")
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    app.run()
