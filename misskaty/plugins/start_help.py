import contextlib
import re

from pyrogram import Client, filters
from pyrogram.errors import ChatSendPhotosForbidden, ChatWriteForbidden, QueryIdInvalid
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from misskaty import BOT_NAME, BOT_USERNAME, HELPABLE, app
from misskaty.helper import bot_sys_stats, paginate_modules
from misskaty.helper.localization import use_chat_lang
from misskaty.vars import COMMAND_HANDLER


home_keyboard_pm = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="Commands ❓", callback_data="bot_commands"),
        ],
        [
            InlineKeyboardButton(text="System Stats 💻", callback_data="stats_callback"),
            InlineKeyboardButton(text="Dev 👨‍💻", url="https://t.me/Sarkar_Terminal"),
        ],
        [
            InlineKeyboardButton(
                text="Add Me To Your Group 🧩",
                url=f"http://t.me/{BOT_USERNAME}?startgroup=true",
            )
        ],
    ]
)

home_text_pm = f"""
Hey there! I’m {BOT_NAME} ✨

An anime-themed Telegram bot with awesome powers for your groups.

Click below to see what I can do or add me to your group to get started!
"""


keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="Help ❓", url=f"http://t.me/{BOT_USERNAME}?start=help"),
        ],
        [
            InlineKeyboardButton(text="System Stats 💻", callback_data="stats_callback"),
            InlineKeyboardButton(text="Dev 👨‍💻", url="https://t.me/Sarkar_Terminal"),
        ],
    ]
)

FED_MARKUP = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Fed Owner Commands", callback_data="fed_owner"),
            InlineKeyboardButton("Fed Admin Commands", callback_data="fed_admin"),
        ],
        [
            InlineKeyboardButton("User Commands", callback_data="fed_user"),
        ],
        [
            InlineKeyboardButton("Back", callback_data="help_back"),
        ],
    ]
)


@app.on_message(filters.command("start", COMMAND_HANDLER))
@use_chat_lang()
async def start(self, ctx: Message, strings):
    if ctx.chat.type.value != "private":
        nama = ctx.from_user.mention if ctx.from_user else ctx.sender_chat.title
        try:
            return await ctx.reply_photo(
                photo="https://img.yasirweb.eu.org/file/90e9a448bc2f8b055b762.jpg",
                caption=strings("start_msg").format(kamuh=nama),
                reply_markup=keyboard,
            )
        except (ChatSendPhotosForbidden, ChatWriteForbidden):
            return await ctx.chat.leave()

    if len(ctx.text.split()) > 1:
        name = (ctx.text.split(None, 1)[1]).lower()
        if "_" in name:
            module = name.split("_", 1)[1]
            text = (
                strings("help_name").format(mod=HELPABLE[module].__MODULE__)
                + HELPABLE[module].__HELP__
            )
            if module == "federation":
                return await ctx.reply(
                    text=text,
                    reply_markup=FED_MARKUP,
                    disable_web_page_preview=True,
                )
            await ctx.reply(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Back", callback_data="help_back")]]
                ),
                disable_web_page_preview=True,
            )
        elif name == "help":
            text, keyb = await help_parser(ctx.from_user.first_name)
            await ctx.reply_msg(text, reply_markup=keyb)
    else:
        await self.send_photo(
            ctx.chat.id,
            photo="https://img.yasirweb.eu.org/file/90e9a448bc2f8b055b762.jpg",
            caption=home_text_pm,
            reply_markup=home_keyboard_pm,
            reply_to_message_id=ctx.id,
        )


@app.on_callback_query(filters.regex("bot_commands"))
async def commands_callbacc(_, cb: CallbackQuery):
    text, keyb = await help_parser(cb.from_user.mention)
    await app.send_message(cb.message.chat.id, text=text, reply_markup=keyb)
    await cb.message.delete()


@app.on_callback_query(filters.regex("stats_callback"))
async def stats_callbacc(_, cb: CallbackQuery):
    text = await bot_sys_stats()
    with contextlib.suppress(QueryIdInvalid):
        await app.answer_callback_query(cb.id, text, show_alert=True)


@app.on_message(filters.command("help", COMMAND_HANDLER))
@use_chat_lang()
async def help_command(_, ctx: Message, strings):
    if ctx.chat.type.value != "private":
        if len(ctx.command) >= 2:
            name = (ctx.text.split(None, 1)[1]).replace(" ", "_").lower()
            if str(name) in HELPABLE:
                key = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=strings("click_me"),
                                url=f"http://t.me/{BOT_USERNAME}?start=help_{name}",
                            )
                        ]
                    ]
                )
                await ctx.reply(strings("pm_cmd_msg"), reply_markup=key)
                return

        key = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=strings("click_me"),
                        url=f"http://t.me/{BOT_USERNAME}?start=help",
                    )
                ]
            ]
        )
        await ctx.reply(strings("pm_cmd_msg"), reply_markup=key)
        return

    text, keyb = await help_parser(ctx.from_user.first_name)
    await ctx.reply(text=text, reply_markup=keyb)


# Helper for help_parser
async def help_parser(name):
    buttons = paginate_modules(0, HELPABLE, "help")
    return (
        f"**{BOT_NAME} Help Panel for {name}**\nChoose a category below:",
        InlineKeyboardMarkup(buttons),
                        )
