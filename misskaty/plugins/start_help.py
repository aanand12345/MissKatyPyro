from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import ChatSendPhotosForbidden

from misskaty import BOT_NAME, BOT_USERNAME, HELPABLE, app
from misskaty.helper import bot_sys_stats, paginate_modules
from misskaty.helper.localization import use_chat_lang
from misskaty.vars import COMMAND_HANDLER

# 🦋 Custom Butterfly Anime Image
START_IMG = "https://files.catbox.moe/6inxw1.jpg"

HOME_TEXT_PM = f"""
🦋 **Konichiwa!** I'm **{BOT_NAME}**, your anime-themed Telegram assistant.

I can manage your groups, control spam, and bring many cool features to your chat!

➥ Use the buttons below to explore my features.
"""

HOME_KEYBOARD_PM = InlineKeyboardMarkup([
    [InlineKeyboardButton("📚 Commands", callback_data="bot_commands")],
    [InlineKeyboardButton("💻 System Stats", callback_data="stats_callback")],
    [InlineKeyboardButton("👨‍💻 Dev", url="https://t.me/Sarkar_Terminal")],
    [InlineKeyboardButton("➕ Add Me To Group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")]
])


@app.on_message(filters.command("start", COMMAND_HANDLER))
@use_chat_lang()
async def start(_, m: Message, strings):
    if m.chat.type != "private":
        try:
            return await m.reply_photo(
                photo=START_IMG,
                caption="🦋 I'm online and ready to help! Use /help for full command list.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📚 Help", url=f"https://t.me/{BOT_USERNAME}?start=help")],
                    [InlineKeyboardButton("💻 System Stats", callback_data="stats_callback")],
                    [InlineKeyboardButton("👨‍💻 Dev", url="https://t.me/Sarkar_Terminal")]
                ])
            )
        except ChatSendPhotosForbidden:
            return await m.chat.leave()

    if len(m.command) > 1:
        param = m.text.split(None, 1)[1].lower()
        if "_" in param:
            mod = param.split("_", 1)[1]
            if mod in HELPABLE:
                return await m.reply(
                    f"**{HELPABLE[mod].__MODULE__}**\n{HELPABLE[mod].__HELP__}",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⬅️ Back", callback_data="help_back")]
                    ])
                )
        elif param == "help":
            txt, btn = await help_parser(m.from_user.first_name)
            return await m.reply(txt, reply_markup=btn)

    await m.reply_photo(photo=START_IMG, caption=HOME_TEXT_PM, reply_markup=HOME_KEYBOARD_PM)


@app.on_message(filters.command("help", COMMAND_HANDLER))
async def help(_, m: Message):
    if m.chat.type != "private":
        return await m.reply(
            "🦋 Click below to get help in PM.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📚 Open Help", url=f"https://t.me/{BOT_USERNAME}?start=help")]
            ])
        )
    txt, btn = await help_parser(m.from_user.first_name)
    await m.reply(txt, reply_markup=btn)


@app.on_callback_query(filters.regex("bot_commands"))
async def commands_cb(_, cb: CallbackQuery):
    txt, btn = await help_parser(cb.from_user.first_name)
    await cb.message.edit_text(txt, reply_markup=btn)


@app.on_callback_query(filters.regex("stats_callback"))
async def stats_cb(_, cb: CallbackQuery):
    stats = await bot_sys_stats()
    await cb.answer(stats, show_alert=True)


async def help_parser(name):
    buttons = paginate_modules(0, HELPABLE, "help")
    return f"**{BOT_NAME} Help Menu for {name}**\nChoose a module below:", InlineKeyboardMarkup(buttons)
