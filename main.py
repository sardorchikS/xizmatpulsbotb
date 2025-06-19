import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

API_TOKEN = "7768655077:AAE7b8cAHmu67gOk_FSbwTHZ2SdQ3kAmHxY"
ADMIN_ID = 7752032178
CHANNEL_LINK = "https://t.me/zeoforge"
ADMIN_PASSWORD = "admin123"

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

class OrderStates(StatesGroup):
    choosing_menu = State()
    entering_quantity = State()
    confirm_more = State()
    waiting_phone = State()
    confirming = State()

class AdminStates(StatesGroup):
    password_check = State()
    managing = State()
    adding = State()
    deleting = State()
    editing = State()
    confirming_admin = State()

menu_items = {
    "🤖 Telegram bot yasash": "loyihaga qarab narx",
    "🌐 Web sayt yaratish": "loyihaga qarab narx",
    "🎨 Logo yasash": 5000,
    "🖼 Banner yasash": 15000,
    "🎮 Animatsiya tayyorlash": 20000,
    "🎩 Slayd tayyorlash": 12000,
    "🎓 Diploma & Rezyume": 17000,
    "💌 Taklifnoma tayyorlash": 20000,
    "🎂 Tug‘ilgan kunga tabrik": 40000,
    "🎧 Video/audio montaj": "loyihaga qarab narx",
    "📄 PDF qilish": 10000,
    "🔤 Telegram nickname yaratish": 2000,
    "🖌 Ismga rasm/video tayyorlash": 7000,
    "📝 Word ishlari": 35000,
    "👤 Avatar tayyorlash": 15000,
    "📈 Nakrutka urish": 10000,
    "📲 Telegram akkaunt olish": 15000,
    "📦 3D ko‘rinishdagi loyihalar": 40000
}

user_orders = {}

@dp.message(F.text == "/start")
async def start_handler(message: Message, state: FSMContext):
    user_orders[message.chat.id] = []
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Men menyim", callback_data="menu"),
             InlineKeyboardButton(text="🛒 Buyurtma berish", callback_data="order")],
            [InlineKeyboardButton(text="🔐 Admin uchun", callback_data="admin")]
        ]
    )
    await message.answer("<b>👋 Assalomu alaykum!</b>\nBu bot orqali siz arzon, sifatli va ishonchli IT xizmatlariga buyurtma bera olasiz. Quyidagilardan birini tanlang:", reply_markup=keyboard)

@dp.callback_query(F.data == "menu")
async def show_menu(callback: CallbackQuery, state: FSMContext):
    buttons = []
    for i, item in enumerate(menu_items):
        narx = menu_items[item]
        narx_str = f"{narx:,} so'm" if isinstance(narx, int) else narx
        buttons.append([InlineKeyboardButton(text=f"{item} - {narx_str}", callback_data=f"item_{i}")])
    buttons.append([InlineKeyboardButton(text="➕ Va boshqa xizmatlar", url=CHANNEL_LINK)])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.answer("<b>📋 Xizmatlar ro'yxati:</b>", reply_markup=keyboard)
    await state.set_state(OrderStates.choosing_menu)

@dp.callback_query(F.data.startswith("item_"))
async def choose_quantity(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.split("_")[1])
    item = list(menu_items.keys())[index]
    await state.update_data(selected_item=item)
    await state.set_state(OrderStates.entering_quantity)
    await callback.message.answer(f"📦 Nechta '{item}' olmoqchisiz?")

@dp.message(OrderStates.entering_quantity)
async def quantity_received(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❗️ Iltimos, son kiriting")
        return
    data = await state.get_data()
    item = data['selected_item']
    user_orders.setdefault(message.from_user.id, []).append((item, int(message.text)))
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Ha, davom etaman", callback_data="continue")],
            [InlineKeyboardButton(text="❌ Yo‘q, yakunlash", callback_data="finish")]
        ]
    )
    await message.answer("Yana biror narsa tanlaysizmi?", reply_markup=keyboard)
    await state.set_state(OrderStates.confirm_more)

@dp.callback_query(F.data == "continue")
async def continue_menu(callback: CallbackQuery, state: FSMContext):
    await show_menu(callback, state)

@dp.callback_query(F.data == "finish")
async def ask_phone(callback: CallbackQuery, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True
    )
    await callback.message.answer("📲 Iltimos, telefon raqamingizni yuboring:", reply_markup=keyboard)
    await state.set_state(OrderStates.waiting_phone)

@dp.message(OrderStates.waiting_phone)
async def get_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    orders = user_orders.get(message.chat.id, [])
    order_texts = []
    total = 0
    for item, qty in orders:
        price = menu_items[item]
        if isinstance(price, int):
            total += price * qty
            order_texts.append(f"{item} x {qty} = {price * qty:,} so'm")
        else:
            order_texts.append(f"{item} x {qty} = {price}")
    order_text = "\n".join(order_texts)
    confirm_text = f"<b>🛍 Siz tanlagan xizmatlar:</b>\n{order_text}\n<b>💵 Umumiy narx:</b> {total:,} so'm\n<b>📞 Telefon:</b> {phone}"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_order")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_order")]
        ]
    )
    await state.update_data(phone=phone, orders=orders)
    await message.answer(confirm_text, reply_markup=keyboard)
    await state.set_state(OrderStates.confirming)

@dp.callback_query(F.data == "confirm_order")
async def final_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = callback.from_user
    username = f"@{user.username}" if user.username else f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
    order_texts = []
    total = 0
    for item, qty in data['orders']:
        price = menu_items[item]
        if isinstance(price, int):
            total += price * qty
            order_texts.append(f"{item} x {qty} = {price * qty:,} so'm")
        else:
            order_texts.append(f"{item} x {qty} = {price}")
    order_list = "\n".join(order_texts)
    text = f"<b>📥 Yangi buyurtma:</b>\n👤 {username}\n📞 <b>Tel:</b> {data['phone']}\n📋 <b>Xizmatlar:</b>\n{order_list}\n💰 <b>Umumiy:</b> {total:,} so'm"
    await bot.send_message(chat_id=ADMIN_ID, text=text)
    await callback.message.answer("✅ Buyurtma tasdiqlandi! Tez orada siz bilan bog'lanamiz. 😊")
    await bot.send_message(chat_id=callback.from_user.id, text="📩 Sizning buyurtmangiz admin tomonidan ko‘rib chiqildi va tez orada siz bilan bog‘laniladi.")
    await state.clear()

@dp.callback_query(F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("❌ Buyurtma bekor qilindi.")
    await state.clear()

@dp.callback_query(F.data == "admin")
async def admin_panel(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🔑 Parolni kiriting:")
    await state.set_state(AdminStates.password_check)

@dp.message(AdminStates.password_check)
async def check_password(message: Message, state: FSMContext):
    if message.text == ADMIN_PASSWORD:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="➕ Xizmat qo‘shish", callback_data="add_item")],
                [InlineKeyboardButton(text="➖ Xizmatni o‘chirish", callback_data="remove_item")],
                [InlineKeyboardButton(text="✏️ Narxni tahrirlash", callback_data="edit_item")]
            ]
        )
        await message.answer("✅ Admin panelga xush kelibsiz:", reply_markup=kb)
        await state.set_state(AdminStates.managing)
    else:
        await message.answer("❌ Noto‘g‘ri parol!")

@dp.callback_query(F.data == "add_item")
async def add_item(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🆕 Yangi xizmatni kiriting (Masalan: 📌 Test - 123000):")
    await state.set_state(AdminStates.adding)

@dp.message(AdminStates.adding)
async def save_new_item(message: Message, state: FSMContext):
    try:
        name, price = message.text.rsplit("-", 1)
        menu_items[name.strip()] = int(price.strip())
        await message.answer("✅ Xizmat qo‘shildi")
    except:
        await message.answer("❗️ Xatolik. Masalan: 📌 Test - 123000")
    await state.set_state(AdminStates.managing)

@dp.callback_query(F.data == "remove_item")
async def list_items_to_delete(callback: CallbackQuery, state: FSMContext):
    buttons = [[InlineKeyboardButton(text=item, callback_data=f"del_{i}")] for i, item in enumerate(menu_items)]
    await callback.message.answer("🗑 O‘chirish uchun xizmatni tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await state.set_state(AdminStates.deleting)

@dp.callback_query(F.data.startswith("del_"))
async def delete_selected_item(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.split("_")[1])
    item = list(menu_items.keys())[index]
    menu_items.pop(item)
    await callback.message.answer(f"❌ {item} o‘chirildi")
    await state.set_state(AdminStates.managing)

@dp.callback_query(F.data == "edit_item")
async def edit_item_prompt(callback: CallbackQuery, state: FSMContext):
    buttons = [[InlineKeyboardButton(text=item, callback_data=f"edit_{i}")] for i, item in enumerate(menu_items)]
    await callback.message.answer("✏️ Narxini o‘zgartirmoqchi bo‘lgan xizmatni tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await state.set_state(AdminStates.editing)

@dp.callback_query(F.data.startswith("edit_"))
async def edit_item_input(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.split("_")[1])
    item = list(menu_items.keys())[index]
    await state.update_data(edit_item=item)
    await callback.message.answer(f"✏️ {item} uchun yangi narxni kiriting:")

@dp.message(AdminStates.editing)
async def save_edited_price(message: Message, state: FSMContext):
    data = await state.get_data()
    item = data.get("edit_item")
    try:
        price = int(message.text.strip())
        menu_items[item] = price
        await message.answer(f"✅ {item} narxi {price:,} so‘m qilib o‘zgartirildi.")
    except:
        await message.answer("❗️ Raqamli narx kiriting.")
    await state.set_state(AdminStates.managing)

@dp.callback_query(F.data == "order")
async def order_entry(callback: CallbackQuery, state: FSMContext):
    await show_menu(callback, state)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
