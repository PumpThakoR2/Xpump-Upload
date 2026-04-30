import requests, base64
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

from PIL import Image
from io import BytesIO

TOKEN = "8571875767:AAHzXaegBaSsn2LLpDOFP7jqORv0mrzr5d8"
IMGBB_KEY = "60c0039b57d57698791a17a47286c303"
SHEET_URL = "https://script.google.com/macros/s/AKfycby7jTMzACsjdrmR9-3cUvUQfcfQd7kHvvwq9DV7cyZxwloJBzEm9gylF_JDCSfOS8u8/exec"

DEFAULT_PROFILE = "https://telegramic.org/media/avatars/users/5444613045.jpg"

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.message.from_user
        post_name = user.first_name
        post_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 📝 Caption REQUIRED
        post_txt = update.message.caption
        if not post_txt or post_txt.strip() == "":
            await update.message.reply_text("❌ Caption မရှိရင် Upload မလုပ်ပါဘူး!")
            return

        # 📷 Get Photo
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        img_data = requests.get(file.file_path).content

        # 📐 Check Image Ratio
        img = Image.open(BytesIO(img_data))
        width, height = img.size
        ratio = width / height

        if not (abs(ratio - 1.0) < 0.05 or abs(ratio - (16/9)) < 0.05):
            await update.message.reply_text("❌ Image ratio က 1:1 သို့မဟုတ် 16:9 ပဲဖြစ်ရမယ်!")
            return

        post_size = len(img_data) // 1024  # KB

        # 🔥 Upload Post Image
        encoded = base64.b64encode(img_data)
        res = requests.post(
            f"https://api.imgbb.com/1/upload?key={IMGBB_KEY}",
            data={"image": encoded}
        ).json()

        post_img = res["data"]["url"]

        # 👤 Profile Image
        try:
            photos = await context.bot.get_user_profile_photos(user.id, limit=1)
            if photos.total_count > 0:
                pfile = await context.bot.get_file(photos.photos[0][-1].file_id)
                pdata = requests.get(pfile.file_path).content
                pencoded = base64.b64encode(pdata)

                pres = requests.post(
                    f"https://api.imgbb.com/1/upload?key={IMGBB_KEY}",
                    data={"image": pencoded}
                ).json()

                profile_img = pres["data"]["url"]
            else:
                profile_img = DEFAULT_PROFILE
        except:
            profile_img = DEFAULT_PROFILE

        # 📤 Send to Google Sheet
        requests.post(SHEET_URL, json={
            "profile_img": profile_img,
            "post_name": post_name,
            "post_date": post_date,
            "post_img": post_img,
            "post_txt": post_txt,
            "post_size": post_size
        })

        # ✅ Reply with preview
        await update.message.reply_photo(
            photo=post_img,
            caption=f"""✅ Upload Done!

👤 {post_name}
📝 {post_txt}
📦 {post_size} KB
📅 {post_date}
"""
        )

    except Exception as e:
        print(e)
        await update.message.reply_text("❌ Error!")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.PHOTO, handle))

print("🚀 Bot Running...")
app.run_polling()
      
