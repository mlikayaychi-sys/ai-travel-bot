import json
import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

BOT_TOKEN = "8200801257:AAEGbq3yTEqwOt-ab9dxGKZuVJ_wlTiw3vk"

# حافظه FSM
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

# خواندن JSON مکان‌ها
with open("places.json", "r", encoding="utf-8") as f:
    places_data = json.load(f)

IRAN_CITIES = [
    "تهران", "کرج", "اصفهان", "شیراز", "مشهد", "تبریز", "قم", "رشت",
    "اهواز", "یزد", "کیش", "قشم", "ارومیه", "زنجان", "سنندج", "همدان"
]

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

# وضعیت FSM
class PlaceStates(StatesGroup):
    waiting_for_category = State()

# استارت بات
@dp.message(Command(commands=["start", "help"]))
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    await message.reply(
        "سلام 👋\n"
        "اسم شهر رو بفرست یا شهر + نوع مکان 🌍\n\n"
        "مثلاً:\n"
        "• تهران\n"
        "• شیراز تاریخی\n"
        "• اصفهان تفریحی"
    )

# تشخیص شهر و دسته‌بندی
def smart_detect(text):
    text = text.strip()
    city = None
    category = None
    for c in IRAN_CITIES:
        if c in text:
            city = c
            break
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                category = CATEGORY_MAP.get(cat, cat)
                break
        if category:
            break
    return city, category

# هندل پیام‌ها
@dp.message()
async def handle_message(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    current_state = await state.get_state()

    # اگر در انتظار دسته‌بندی هستیم
    if current_state == PlaceStates.waiting_for_category.state:
        category_text = message.text.strip()
        category = CATEGORY_MAP.get(category_text)
        city = state_data.get("city")
        if city and category:
            await show_place(message, city, category)
        else:
            await message.reply(
                "دسته‌بندی معتبر نیست. لطفاً یکی از گزینه‌ها را انتخاب کن:\n"
                "تاریخی، تفریحی، طبیعت، مرکز خرید"
            )
        await state.clear()
        return

    # حالت معمولی → تشخیص شهر و دسته‌بندی از پیام
    text = message.text.strip()
    city, category = smart_detect(text)

    if city and category:
        await show_place(message, city, category)
        await state.clear()
        return

    if city and not category:
        await state.update_data(city=city)
        await state.set_state(PlaceStates.waiting_for_category)
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
        await message.reply(f"برای {city} دنبال چه نوع جایی هستی؟ 🤔", reply_markup=keyboard)
        return

    await message.reply("لطفاً ابتدا شهر یا شهر + دسته‌بندی را بنویسید 🌍")

# نمایش مکان
async def show_place(message: types.Message, city, category):
    category_mapped = CATEGORY_MAP.get(category, category)

    if city not in places_data:
        await message.reply(f"برای {city} اطلاعاتی ندارم 😔")
        return

    places_list = places_data[city].get(category_mapped, [])
    if not places_list:
        await message.reply(f"برای {city} مکان {category} ثبت نشده 😔")
        return

    place = random.choice(places_list)

    # ساخت کیبورد صحیح با inline_keyboard=[]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[])

    if "map_url" in place:
        keyboard.add(types.InlineKeyboardButton(text="مشاهده در نقشه", url=place["map_url"]))
    keyboard.add(types.InlineKeyboardButton(
        text="مکان بعدی 🔄", callback_data=f"next|{city}|{category}"
    ))

    caption = f"📍 <b>{place['name']}</b>\n\n{place['description']}\n\n🏙️ شهر: {city}\n🏷️ نوع: {category}"
    await message.reply(caption, parse_mode="HTML", reply_markup=keyboard)

# هندل دکمه مکان بعدی
@dp.callback_query()
async def handle_callback(call: types.CallbackQuery):
    data = call.data
    if data.startswith("next|"):
        _, city, category = data.split("|")
        category_mapped = CATEGORY_MAP.get(category, category)
        places_list = places_data[city].get(category_mapped, [])
        if not places_list:
            await call.message.answer(f"برای {city} مکان {category} ثبت نشده 😔")
            return
        place = random.choice(places_list)

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[])
        if "map_url" in place:
            keyboard.add(types.InlineKeyboardButton(text="مشاهده در نقشه", url=place["map_url"]))
        keyboard.add(types.InlineKeyboardButton(
            text="مکان بعدی 🔄", callback_data=f"next|{city}|{category}"
        ))

        caption = f"📍 <b>{place['name']}</b>\n\n{place['description']}\n\n🏙️ شهر: {city}\n🏷️ نوع: {category}"
        await call.message.edit_text(caption, parse_mode="HTML", reply_markup=keyboard)

# اجرای بات
if __name__ == "__main__":
    print("Bot is running...")
    asyncio.run(dp.start_polling(bot))
