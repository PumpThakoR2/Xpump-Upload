import telebot
import requests
import os

BOT_TOKEN = "8554286668:AAHI84SfVPsvfUkzy7K2JBB-R6hZBOMBFqo"
API_KEY = "sk_TdWwigBfXATT_vrEKCruoQkp6z2_PQ5D"

bot = telebot.TeleBot(BOT_TOKEN)

# start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🤖 Hello!\n📥 Video ပို့လိုက်ပါ Upload လုပ်ပေးမယ်")

# video handler
@bot.message_handler(content_types=['video'])
def handle_video(message):
    msg = bot.reply_to(message, "⏳ Uploading... Please wait")

    try:
        # Step 1: get file
        file_id = message.video.file_id
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"

        # Step 2: download
        file_data = requests.get(file_url).content

        # Step 3: upload
        files = {
            "file": ("video.mp4", file_data)
        }
        data = {
            "title": message.caption if message.caption else "Telegram Upload"
        }
        headers = {
            "x-api-key": API_KEY
        }

        response = requests.post(
            "https://upload.zerostorage.net/api/upload/universal",
            headers=headers,
            files=files,
            data=data
        )

        res = response.json()

        # Step 4: extract stream link
        if response.status_code == 200 and "fileId" in res:
            file_id = res["fileId"]

            stream_link = f"https://zerostorage.net/api/files/{file_id}/stream"

            text = f"""
✅ Upload Complete!

🎬 Title: {data['title']}
🔗 Stream Link:
{stream_link}

🚀 Powered by PumpThako
"""
            bot.edit_message_text(text, message.chat.id, msg.message_id)

        else:
            bot.edit_message_text("❌ Upload Failed!", message.chat.id, msg.message_id)

    except Exception as e:
        print(e)
        bot.edit_message_text(f"⚠️ Error:\n{str(e)}", message.chat.id, msg.message_id)

# keep bot running
print("🤖 Bot Running...")
bot.infinity_polling()
