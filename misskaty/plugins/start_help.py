import contextlib
import re

from pyrogram import Client, filters
from pyrogram.errors import ChatSendPhotosForbidden, ChatWriteForbidden, QueryIdInvalid
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from misskaty import BOT_NAME, BOT_USERNAME, HELPABLE, app
from misskaty.helper import bot_sys_stats, paginate_modules
from misskaty.helper.localization import use_chat_lang
from misskaty.vars import COMMAND_HANDLER

ANIME_START_PHOTO = "https://files.catbox.moe/6inxw1.jpg"

home_keyboard_pm = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Commands ✨", callback_data="bot_commands"),
            InlineKeyboardButton("System Stats 💻", callback_data="stats_callback"),
        ],
        [
            InlineKeyboardButton("Add Me To Your Group 🎉", url=f"http://t.me/{BOT_USERNAME}?startgroup=true")
        ],
    ]
)

home_text_pm = f"Kon'nichiwa~! 🌸 I'm {BOT_NAME}, your cute and helpful assistant!\n\nClick the buttons below to explore my powers~ ✨\n\nNeed help? Use `/help` or press the buttons~"

keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Help 📖", url=f"t.me/{BOT_USERNAME}?start=help"),
            InlineKeyboardButton("Status 💫", callback_data="stats_callback"),
        ]
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
                photo=ANIME_START_PHOTO,
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
                    message_effect_id=5104841245755180586,
                )
            return await ctx.reply(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Back", callback_data="help_back")]]
                ),
                disable_web_page_preview=True,
                message_effect_id=5104841245755180586,
            )
        elif name == "help":
            text, keyb = await help_parser(ctx.from_user.first_name)
            await ctx.reply_msg(
                text, reply_markup=keyb, message_effect_id=5104841245755180586
            )
    else:
        await self.send_photo(
            ctx.chat.id,
            photo=ANIME_START_PHOTO,
            caption=home_text_pm,
            reply_markup=home_keyboard_pm,
            reply_to_message_id=ctx.id,
            message_effect_id=5104841245755180586,
        )


@app.on_callback_query(filters.regex("bot_commands"))
async def commands_callbacc(_, cb: CallbackQuery):
    text, keyb = await help_parser(cb.from_user.mention)
    await app.send_message(
        cb.message.chat.id,
        text=text,
        reply_markup=keyb,
        message_effect_id=5104841245755180586,
    )
    await cb.message.delete_msg()


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
                                url=f"t.me/{BOT_USERNAME}?start=help_{name}",
                            )
                        ],
                    ]
                )
                await ctx.reply_msg(strings("click_btn").format(nm=name), reply_markup=key)
            else:
                await ctx.reply_msg(strings("pm_detail"), reply_markup=keyboard)
        else:
            await ctx.reply_msg(strings("pm_detail"), reply_markup=keyboard)
    elif len(ctx.command) >= 2:
        name = (ctx.text.split(None, 1)[1]).replace(" ", "_").lower()
        if str(name) in HELPABLE:
            text = (
                strings("help_name").format(mod=HELPABLE[name].__MODULE__)
                + HELPABLE[name].__HELP__
            )
            await ctx.reply_msg(
                text,
                disable_web_page_preview=True,
                message_effect_id=5104841245755180586,
            )
        else:
            text, help_keyboard = await help_parser(ctx.from_user.first_name)
            await ctx.reply_msg(
                text,
                reply_markup=help_keyboard,
                disable_web_page_preview=True,
                message_effect_id=5104841245755180586,
            )
    else:
        text, help_keyboard = await help_parser(ctx.from_user.first_name)
        await ctx.reply_msg(
            text,
            reply_markup=help_keyboard,
            disable_web_page_preview=True,
            message_effect_id=5104841245755180586,
        )


async def help_parser(name, keyb=None):
    if not keyb:
        keyb = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    return (
        f"""Kon'nichiwa {name}~ 🌸

I'm your assistant bot **{BOT_NAME}** here to help you ✨

Use the buttons below or `/help <module>` to explore my commands.

💬 Tip: Use `/setlang` to set your language (Beta)
🍵 Wanna support me? Send /donate for coffee ☕
""",
        keyb,
    )
