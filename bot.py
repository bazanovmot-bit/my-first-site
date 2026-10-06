# -*- coding: utf-8 -*-
"""
Telegram-бот казино: слоты, кости, угадай число, рулетка.
Полностью на Python. Библиотека: aiogram 3.x
"""

import asyncio
import json
import os
import random
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)

from config import BOT_TOKEN

# ============================================================
# НАСТРОЙКИ
# ============================================================
DATA_FILE = "users.json"
START_BALANCE = 1000
DAILY_BONUS = 200

SYMBOLS = ['🍒', '🍋', '🍊', '🔔', '💎', '7️⃣']
WEIGHTS = [30, 25, 20, 12, 8, 5]

# ============================================================
# ХРАНИЛИЩЕ (JSON)
# ============================================================
def load_users() -> dict:
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_users(users: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def get_user(user_id: int, username: str = "") -> dict:
    users = load_users()
    key = str(user_id)
    if key not in users:
        users[key] = {
            "name": username or "Игрок",
            "balance": START_BALANCE,
            "last_bonus": "",
            "wins": 0,
            "games": 0,
        }
        save_users(users)
    return users[key]

def update_user(user_id: int, **fields) -> None:
    users = load_users()
    key = str(user_id)
    if key in users:
        users[key].update(fields)
        save_users(users)

def add_balance(user_id: int, delta: int) -> int:
    users = load_users()
    key = str(user_id)
    if key not in users:
        return 0
    users[key]["balance"] = max(0, users[key]["balance"] + delta)
    save_users(users)
    return users[key]["balance"]

def get_balance(user_id: int) -> int:
    return get_user(user_id).get("balance", 0)

# ============================================================
# ВСПОМОГАТЕЛЬНОЕ
# ============================================================
def weighted_symbol() -> str:
    return random.choices(SYMBOLS, weights=WEIGHTS, k=1)[0]

def format_balance(user_id: int) -> str:
    return f"💰 Баланс: **{get_balance(user_id)}** фишек"

def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎰 Слоты", callback_data="game:slots"),
            InlineKeyboardButton(text="🎲 Кости", callback_data="game:dice"),
        ],
        [
            InlineKeyboardButton(text="🔢 Угадай число", callback_data="game:guess"),
            InlineKeyboardButton(text="🎡 Рулетка", callback_data="game:roulette"),
        ],
        [
            InlineKeyboardButton(text="💰 Баланс", callback_data="menu:balance"),
            InlineKeyboardButton(text="🎁 Бонус", callback_data="menu:bonus"),
        ],
        [
            InlineKeyboardButton(text="🏆 Топ игроков", callback_data="menu:top"),
            InlineKeyboardButton(text="ℹ️ Помощь", callback_data="menu:help"),
        ],
    ])

def bet_kb(game: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="10", callback_data=f"bet:{game}:10"),
            InlineKeyboardButton(text="50", callback_data=f"bet:{game}:50"),
            InlineKeyboardButton(text="100", callback_data=f"bet:{game}:100"),
            InlineKeyboardButton(text="250", callback_data=f"bet:{game}:250"),
        ],
        [
            InlineKeyboardButton(text="⬅️ В меню", callback_data="menu:main"),
        ],
    ])

# ============================================================
# БОТ
# ============================================================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

guess_game: dict[int, dict] = {}

# ============================================================
# КОМАНДЫ
# ============================================================
@dp.message(Command("start"))
async def cmd_start(message: Message):
    user = get_user(message.from_user.id, message.from_user.first_name)
    text = (
        f"🎰 **Добро пожаловать в Golden Spin Casino!**\n\n"
        f"Привет, {user['name']}!\n"
        f"{format_balance(message.from_user.id)}\n\n"
        f"Выбери игру 👇\n\n"
        f"Команды:\n"
        f"/balance — баланс\n"
        f"/bonus — ежедневный бонус\n"
        f"/top — топ игроков\n"
        f"/help — помощь"
    )
    await message.answer(text, reply_markup=main_menu_kb(), parse_mode="Markdown")

@dp.message(Command("balance"))
async def cmd_balance(message: Message):
    await message.answer(
        format_balance(message.from_user.id),
        reply_markup=main_menu_kb(),
        parse_mode="Markdown",
    )

@dp.message(Command("bonus"))
async def cmd_bonus(message: Message):
    uid = message.from_user.id
    user = get_user(uid, message.from_user.first_name)
    today = datetime.now().strftime("%Y-%m-%d")
    if user.get("last_bonus") == today:
        await message.answer("🎁 Ты уже получал бонус сегодня. Приходи завтра!", reply_markup=main_menu_kb())
        return
    add_balance(uid, DAILY_BONUS)
    update_user(uid, last_bonus=today)
    await message.answer(
        f"🎁 **Ежедневный бонус: +{DAILY_BONUS} фишек!**\n{format_balance(uid)}",
        reply_markup=main_menu_kb(),
        parse_mode="Markdown",
    )

@dp.message(Command("top"))
async def cmd_top(message: Message):
    users = load_users()
    top = sorted(users.items(), key=lambda x: x[1].get("balance", 0), reverse=True)[:10]
    lines = ["🏆 **Топ-10 игроков:**\n"]
    for i, (_, u) in enumerate(top, 1):
        medal = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else f"{i}."
        lines.append(f"{medal} {u['name']} — {u['balance']} 💰")
    if len(top) == 0:
        lines.append("Пока никого нет. Будь первым!")
    await message.answer("\n".join(lines), reply_markup=main_menu_kb(), parse_mode="Markdown")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    text = (
        "ℹ️ **Помощь**\n\n"
        "Это игровой бот-казино. Все фишки — виртуальные.\n\n"
        "**Игры:**\n"
        "🎰 Слоты — совпадения символов\n"
        "🎲 Кости — угадай бросок\n"
        "🔢 Угадай число — 1–10\n"
        "🎡 Рулетка — цвет\n\n"
        "**Бонус:** /bonus — +200 фишек раз в день\n"
    )
    await message.answer(text, reply_markup=main_menu_kb(), parse_mode="Markdown")

# ============================================================
# МЕНЮ
# ============================================================
@dp.callback_query(F.data == "menu:main")
async def cb_menu_main(callback: CallbackQuery):
    await callback.message.edit_text(
        f"🎰 **Golden Spin Casino**\n\n{format_balance(callback.from_user.id)}\n\nВыбери игру 👇",
        reply_markup=main_menu_kb(),
        parse_mode="Markdown",
    )
    await callback.answer()

@dp.callback_query(F.data == "menu:balance")
async def cb_balance(callback: CallbackQuery):
    await callback.answer(f"Баланс: {get_balance(callback.from_user.id)}", show_alert=True)

@dp.callback_query(F.data == "menu:bonus")
async def cb_bonus(callback: CallbackQuery):
    uid = callback.from_user.id
    user = get_user(uid, callback.from_user.first_name)
    today = datetime.now().strftime("%Y-%m-%d")
    if user.get("last_bonus") == today:
        await callback.answer("Уже получал сегодня!", show_alert=True)
        return
    add_balance(uid, DAILY_BONUS)
    update_user(uid, last_bonus=today)
    await callback.answer(f"+{DAILY_BONUS} фишек!", show_alert=True)
    await callback.message.edit_text(
        f"🎁 Бонус: +{DAILY_BONUS}\n{format_balance(uid)}",
        reply_markup=main_menu_kb(),
        parse_mode="Markdown",
    )

@dp.callback_query(F.data == "menu:top")
async def cb_top(callback: CallbackQuery):
    users = load_users()
    top = sorted(users.items(), key=lambda x: x[1].get("balance", 0), reverse=True)[:10]
    lines = ["🏆 **Топ-10:**\n"]
    for i, (_, u) in enumerate(top, 1):
        medal = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else f"{i}."
        lines.append(f"{medal} {u['name']} — {u['balance']} 💰")
    await callback.message.edit_text("\n".join(lines), reply_markup=main_menu_kb(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "menu:help")
async def cb_help(callback: CallbackQuery):
    await callback.answer("Открой /help для справки", show_alert=True)

# ============================================================
# ИГРЫ
# ============================================================
@dp.callback_query(F.data.startswith("game:"))
async def cb_game(callback: CallbackQuery):
    game = callback.data.split(":")[1]
    uid = callback.from_user.id
    titles = {
        "slots":    "🎰 **Слоты**\n\nТри одинаковых — большой выигрыш.",
        "dice":     "🎲 **Кости**\n\nУгадай бросок. ×5.",
        "guess":    "🔢 **Угадай число**\n\n1–10. ×8.",
        "roulette": "🎡 **Рулетка**\n\nЦвет ×2, зеро ×14.",
    }
    if game == "roulette":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔴 КРАСНОЕ ×2", callback_data="rlt:red"),
                InlineKeyboardButton(text="⚫ ЧЁРНОЕ ×2", callback_data="rlt:black"),
            ],
            [InlineKeyboardButton(text="🟢 ЗЕРО ×14", callback_data="rlt:green")],
            [InlineKeyboardButton(text="⬅️ В меню", callback_data="menu:main")],
        ])
        await callback.message.edit_text(
            f"{titles[game]}\n\n{format_balance(uid)}",
            reply_markup=kb, parse_mode="Markdown",
        )
    else:
        await callback.message.edit_text(
            f"{titles[game]}\n\n{format_balance(uid)}\n\nВыбери ставку:",
            reply_markup=bet_kb(game), parse_mode="Markdown",
        )
    await callback.answer()

# ---------- СЛОТЫ ----------
@dp.callback_query(F.data.startswith("bet:slots:"))
async def cb_slots(callback: CallbackQuery):
    bet = int(callback.data.split(":")[2])
    uid = callback.from_user.id
    if get_balance(uid) < bet:
        await callback.answer("Недостаточно фишек!", show_alert=True)
        return

    add_balance(uid, -bet)
    a, b, c = weighted_symbol(), weighted_symbol(), weighted_symbol()
    result_line = f"{a} | {b} | {c}"

    win = 0
    if a == b == c:
        if a == '7️⃣':
            win = bet * 20
            msg = "🎉 **ДЖЕКПОТ!** × 20"
        elif a == '💎':
            win = bet * 15
            msg = "💎 **Три алмаза!** × 15"
        else:
            win = bet * 8
            msg = f"✨ **Три {a}** × 8"
    elif a == b or b == c or a == c:
        win = bet * 2
        msg = "🔸 Два совпадения — × 2"
    else:
        msg = "😢 Не повезло."

    if win > 0:
        add_balance(uid, win)
        update_user(uid, wins=get_user(uid).get("wins", 0) + 1)
    update_user(uid, games=get_user(uid).get("games", 0) + 1)

    text = f"🎰 **Слоты**\n\n`{result_line}`\n\n{msg}\n"
    if win > 0:
        text += f"💵 +{win}\n"
    text += f"\n{format_balance(uid)}"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🔁 Ещё ({bet})", callback_data=f"bet:slots:{bet}")],
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="menu:main")],
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

# ---------- КОСТИ ----------
@dp.callback_query(F.data.startswith("bet:dice:"))
async def cb_dice(callback: CallbackQuery):
    bet = int(callback.data.split(":")[2])
    uid = callback.from_user.id
    if get_balance(uid) < bet:
        await callback.answer("Недостаточно фишек!", show_alert=True)
        return

    add_balance(uid, -bet)
    player = random.randint(1, 6)
    bot_roll = random.randint(1, 6)

    if player == bot_roll:
        win = bet * 5
        add_balance(uid, win)
        update_user(uid, wins=get_user(uid).get("wins", 0) + 1)
        msg = f"🎉 Совпадение! +{win}"
    else:
        msg = "😢 Не угадал."

    dice_faces = ["", "⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
    text = (
        f"🎲 **Кости**\n\n"
        f"Твой бросок: {dice_faces[player]} ({player})\n"
        f"Мой: {dice_faces[bot_roll]} ({bot_roll})\n\n"
        f"{msg}\n\n{format_balance(uid)}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🔁 Ещё ({bet})", callback_data=f"bet:dice:{bet}")],
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="menu:main")],
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

# ---------- УГАДАЙ ЧИСЛО ----------
@dp.callback_query(F.data.startswith("bet:guess:"))
async def cb_guess(callback: CallbackQuery):
    bet = int(callback.data.split(":")[2])
    uid = callback.from_user.id
    if get_balance(uid) < bet:
        await callback.answer("Недостаточно фишек!", show_alert=True)
        return

    add_balance(uid, -bet)
    number = random.randint(1, 10)
    guess_game[uid] = {"number": number, "bet": bet}

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=str(n), callback_data=f"gnum:{n}") for n in range(1, 6)],
        [InlineKeyboardButton(text=str(n), callback_data=f"gnum:{n}") for n in range(6, 11)],
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="menu:main")],
    ])
    await callback.message.edit_text(
        f"🔢 **Угадай число**\n\nЯ загадал 1–10.\nСтавка: {bet}\nУгадаешь — × 8!\n\n{format_balance(uid)}",
        reply_markup=kb, parse_mode="Markdown",
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("gnum:"))
async def cb_gnum(callback: CallbackQuery):
    uid = callback.from_user.id
    if uid not in guess_game:
        await callback.answer("Сначала начни игру.", show_alert=True)
        return

    guess = int(callback.data.split(":")[1])
    game = guess_game.pop(uid)
    number = game["number"]
    bet = game["bet"]

    if guess == number:
        win = bet * 8
        add_balance(uid, win)
        update_user(uid, wins=get_user(uid).get("wins", 0) + 1)
        text = f"🔢 Ты выбрал: **{guess}**\nЗагадано: **{number}**\n\n🎉 **УГАДАЛ!** +{win}\n\n{format_balance(uid)}"
    else:
        text = f"🔢 Ты выбрал: **{guess}**\nЗагадано: **{number}**\n\n😢 Не угадал.\n\n{format_balance(uid)}"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Ещё", callback_data=f"bet:guess:{bet}")],
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="menu:main")],
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

# ---------- РУЛЕТКА ----------
@dp.callback_query(F.data.startswith("rlt:"))
async def cb_roulette_color(callback: CallbackQuery):
    color = callback.data.split(":")[1]
    names = {"red": "🔴 Красное", "black": "⚫ Чёрное", "green": "🟢 Зеро"}
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="10", callback_data=f"rbet:{color}:10"),
            InlineKeyboardButton(text="50", callback_data=f"rbet:{color}:50"),
            InlineKeyboardButton(text="100", callback_data=f"rbet:{color}:100"),
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="game:roulette")],
    ])
    await callback.message.edit_text(
        f"🎡 **Рулетка**\n\nТы выбрал: {names[color]}\n\nВыбери ставку:",
        reply_markup=kb, parse_mode="Markdown",
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("rbet:"))
async def cb_roulette_bet(callback: CallbackQuery):
    _, color, bet_str = callback.data.split(":")
    bet = int(bet_str)
    uid = callback.from_user.id
    if get_balance(uid) < bet:
        await callback.answer("Недостаточно фишек!", show_alert=True)
        return

    add_balance(uid, -bet)
    number = random.randint(0, 36)
    if number == 0:
        result_color = "green"
    elif number % 2 == 0:
        result_color = "red"
    else:
        result_color = "black"

    win = 0
    if color == result_color:
        win = bet * 14 if color == "green" else bet * 2
        add_balance(uid, win)
        update_user(uid, wins=get_user(uid).get("wins", 0) + 1)
        msg = f"🎉 Ты угадал! +{win}"
    else:
        msg = "😢 Не угадал."

    emoji = {"red": "🔴", "black": "⚫", "green": "🟢"}[result_color]
    text = f"🎡 Выпало: {emoji} **{number}**\n\n{msg}\n\n{format_balance(uid)}"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎡 Ещё", callback_data="game:roulette")],
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="menu:main")],
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

# ============================================================
# ЗАПУСК
# ============================================================
async def main():
    print("🤖 Бот запущен. Ctrl+C — остановить.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Бот остановлен.")