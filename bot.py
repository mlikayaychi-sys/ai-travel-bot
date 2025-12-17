import json
import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

BOT_TOKEN = "8200801257:AAEGbq3yTEqwOt-ab9dxGKZuVJ_wlTiw3vk"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 📂 خواندن JSON مکان‌ها
with open("places.json", "r", encoding="utf-8") as f:
    places_data = json.load(f)

# 🏙 لیست شهرها
IRAN_CITIES = [
    "تهران", "کرج", "اصفهان", "شیراز", "مشهد", "تبریز", "قم", "رشت",
    "اهواز", "یزد", "کیش", "قشم", "ارومیه", "زنجان", "سنندج", "همدان"
]

# 🏷 کلیدواژه‌ها و نگاشت دسته‌بندی
CATEGORY_KEYWORDS = {
    "تاریخی": ["تاریخی", "قدیمی", "موزه", "کاخ", "قلعه"],
    "طبیعت": ["طبیعت", "پارک", "کوه", "جنگل", "دریا", "دریاچه", "باغ"],
    "تفریحی": ["تفریحی", "گردش", "بازی", "شهربازی"],
    "مرکز خرید": ["مرکز خرید", "بازار", "مال"]
}

CATEGORY_MAP = {
    "تاریخی": "تاریخی_فرهنگی",
    "طبیعت": "طبیعت",
    "تفریحی": "تفریحی",
    "مرکز خرید": "مرکز_خرید"
}

# 💬 استارت و راهنمایی
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

# 🧠 تشخیص شهر و دسته‌بندی از متن
def smart_detect(text):
    text = text.strip()
    city = None
    category = None

    # تشخیص شهر
    for c in IRAN_CITIES:
        if c in text:
            city = c
            break

    # تشخیص دسته‌بندی
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                category = CATEGORY_MAP.get(cat, cat)
                break
        if category:
            break

    return city, category

# 📨 هندل پیام‌ها
@dp.message()
async def handle_message(message: types.Message):
    text = (message.text or "").strip()
    city, category = smart_detect(text)

    if not city:
        await message.reply("لطفاً اسم شهر رو بنویس 🌍")
        return

    # اگر فقط شهر بود، از کاربر نوع مکان را بپرس
    if not category:
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="تاریخی")],
                [types.KeyboardButton(text="طبیعت")],
                [types.KeyboardButton(text="تفریحی")],
                [types.KeyboardButton(text="مرکز خرید")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.reply(
            f"برای {city} دنبال چه نوع جایی هستی؟ 🤔",
            reply_markup=keyboard
        )
        return

    # بررسی وجود شهر در JSON
    if city not in places_data:
        await message.reply(f"برای {city} اطلاعاتی ندارم 😔")
        return

    # گرفتن لیست مکان‌ها بر اساس دسته‌بندی
    places_list = places_data[city].get(category, [])
    if not places_list:
        await message.reply(f"برای {city} مکان {category} ثبت نشده 😔")
        return

    # انتخاب مکان تصادفی
    place = random.choice(places_list)

    caption = (
        f"📍 <b>{place['name']}</b>\n\n"
        f"{place['description']}\n\n"
        f"🏙️ شهر: {city}\n"
        f"🏷️ نوع: {category}"
    )
    await message.reply(caption, parse_mode="HTML")

# 🏃‍♂️ اجرای بات
if __name__ == "__main__":
    print("Bot is running...")
    asyncio.run(dp.start_polling(bot))
