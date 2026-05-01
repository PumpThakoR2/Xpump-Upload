import telebot
import requests

BOT_TOKEN = "8554286668:AAHI84SfVPsvfUkzy7K2JBB-R6hZBOMBFqo"
API_KEY = "sk_TdWwigBfXATT_vrEKCruoQkp6z2_PQ5D"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        # Step 1: Get file info
        file_id = message.video.file_id
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"

        # Step 2: Download video from Telegram
        file_data = requests.get(file_url).content

        # Step 3: Upload to ZeroStorage
        files = {
            "file": ("video.mp4", file_data)
        }
        data = {
            "title": "Uploaded from Telegram Bot"
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

        result = response.json()

        # Step 4: Send result back
        if response.status_code == 200:
            bot.reply_to(message, f"✅ Upload Success!\n\n{result}")
        else:
            bot.reply_to(message, f"❌ Upload Failed\n{result}")

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

bot.polling()
