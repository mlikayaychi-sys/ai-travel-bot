import json
import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# 🔐 توکن بات (اگر روی Render هستی بهتره از ENV استفاده کنی)
BOT_TOKEN = "8200801257:AAFER11KLtTq-oSy-DaCbX90GeGxcqb9TK0"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 📂 خواندن فایل JSON
with open("places.json", "r", encoding="utf-8") as f:
    places_data = json.load(f)

# 🏙 لیست شهرها (برای تشخیص هوشمند)
IRAN_CITIES = [
    "تهران", "کرج", "اصفهان", "شیراز", "مشهد", "تبریز", "قم", "رشت",
    "اهواز", "یزد", "کیش", "قشم", "ارومیه", "زنجان", "سنندج", "همدان"
]

# 🏷 دسته‌بندی‌ها و کلمات مرتبط
CATEGORY_KEYWORDS = {
    "تاریخی": ["تاریخی", "قدیمی", "موزه", "کاخ", "قلعه"],
    "طبیعت": ["طبیعت", "پارک", "کوه", "جنگل", "دریا", "دریاچه", "باغ"],
    "تفریحی": ["تفریحی", "گردش", "بازی", "مرکز خرید", "شهربازی"]
}

@dp.message(Command(commands=["start", "help"]))
async def start_cmd(message: types.Message):
    await message.reply(
        "سلام 👋\n"
        "اسم شهر رو بفرست یا شهر + نوع مکان 🌍\n\n"
        "مثلاً:\n"
        "• تهران\n"
        "• شیراز تاریخی\n"
        "• اصفهان تفریحی"
    )

# 🧠 تشخیص هوشمند شهر و دسته‌بندی
def smart_detect(text):
    text = text.lower()
    city = None
    category = None

    for c in IRAN_CITIES:
        if c in text:
            city = c
            break

    for cat, words in CATEGORY_KEYWORDS.items():
        for w in words:
            if w in text:
                category = cat
                break
        if category:
            break

    return city, category

@dp.message()
async def handle_message(message: types.Message):
    text = (message.text or "").strip()

    city, category = smart_detect(text)

    if not city:
        await message.reply("لطفاً اسم شهر رو بنویس 🌍")
        return

    if not category:
        await message.reply(
            f"برای {city} دنبال چه نوع جایی هستی؟ 🤔\n"
            "🏛 تاریخی\n🌿 طبیعت\n🎡 تفریحی"
        )
        return

    if city not in places_data:
        await message.reply(
            f"برای {city} اطلاعات دقیق ندارم 😔\n"
            f"ولی معمولاً جاهای {category} خوبی داره!"
        )
        return

    places = places_data[city]["places"].get(category, [])

    if not places:
        await message.reply(
            f"برای {city} مکان {category} ثبت نشده."
        )
        return

    place = random.choice(places)

    caption = (
        f"📍 <b>{place['name']}</b>\n\n"
        f"{place['desc']}\n\n"
        f"🏙️ شهر: {city}\n"
        f"🏷️ نوع: {category}"
    )

    await message.reply(caption, parse_mode="HTML")

if __name__ == "__main__":
    print("Bot is running...")
    asyncio.run(dp.start_polling(bot))
