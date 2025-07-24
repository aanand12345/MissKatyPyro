import contextlib
import re

from pyrogram import Client, filters
from pyrogram.errors import ChatSendPhotosForbidden, ChatWriteForbidden, QueryIdInvalid
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from misskaty import BOT_NAME, BOT_USERNAME, HELPABLE, app
from misskaty.helper import bot_sys_stats, paginate_modules
from misskaty.helper.localization import use_chat_lang
from misskaty.vars import COMMAND_HANDLER

ANIME_BANNER = "https://img.anupics.eu.org/file/anime-banner.jpg"  # Change if needed

home_keyboard_pm = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("🌸 Commands", callback_data="bot_commands"),
            InlineKeyboardButton("💻 System Stats", callback_data="stats_callback"),
        ],
        [
            InlineKeyboardButton("👤 Developer", url="https://t.me/Sarkar_Terminal"),
            InlineKeyboardButton("➕ Add AnuBot", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"),
        ],
    ]
)

home_text_pm = f"""
**𓆩 𝘈𝘯𝘶 ✘ 𝘉𝘰𝘵 𓆪** — Your Personal Assistant 🦋

Hey there, Senpai~ ✨  
I’m here to **protect**, **manage**, and **style** your groups with elegance.  
Invite me to your group and let’s start the magic together~ 🌸

➤ Click the **Commands** button below to explore what I can do!  
➤ Add me to your group and watch the magic happen 🦋
"""

keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("🎀 Help", url=f"https://t.me/{BOT_USERNAME}?start=help"),
            InlineKeyboardButton("💻 Stats", callback_data="stats_callback"),
        ],
        [
            InlineKeyboardButton("👤 Developer", url="https://t.me/Sarkar_Terminal"),
        ],
    ]
)

FED_MARKUP = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("⚔️ Fed Owner", callback_data="fed_owner"),
            InlineKeyboardButton("🛡 Fed Admin", callback_data="fed_admin"),
        ],
        [
            InlineKeyboardButton("👥 User Commands", callback_data="fed_user"),
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="help_back"),
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
                photo=ANIME_BANNER,
                caption=strings("start_msg").format(kamuh=nama),
                reply_markup=keyboard,
            )
        except (ChatSendPhotosForbidden, ChatWriteForbidden):
            return await ctx.chat.leave()

    if len(ctx.text.split()) > 1:
        name = (ctx.text.split(None, 1)[1]).lower()
        if "_" in name:
            module = name.split("_", 1)[1]
            text = strings("help_name").format(mod=HELPABLE[module].__MODULE__) + HELPABLE[module].__HELP__
            if module == "federation":
                return await ctx.reply(
                    text=text,
                    reply_markup=FED_MARKUP,
                    disable_web_page_preview=True,
                    message_effect_id=5104841245755180586,
                )
            await ctx.reply(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔙 Back", callback_data="help_back")]]
                ),
                disable_web_page_preview=True,
                message_effect_id=5104841245755180586,
            )
        elif name == "help":
            text, keyb = await help_parser(ctx.from_user.first_name)
            await ctx.reply_msg(text, reply_markup=keyb, message_effect_id=5104841245755180586)
    else:
        await self.send_photo(
            ctx.chat.id,
            photo=ANIME_BANNER,
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
                                url=f"https://t.me/{BOT_USERNAME}?start=help_{name}",
                            )
                        ],
                    ]
                )
                await ctx.reply_msg(
                    strings("click_btn").format(nm=name),
                    reply_markup=key,
                )
            else:
                await ctx.reply_msg(strings("pm_detail"), reply_markup=keyboard)
        else:
            await ctx.reply_msg(strings("pm_detail"), reply_markup=keyboard)
    elif len(ctx.command) >= 2:
        name = (ctx.text.split(None, 1)[1]).replace(" ", "_").lower()
        if str(name) in HELPABLE:
            text = strings("help_name").format(mod=HELPABLE[name].__MODULE__) + HELPABLE[name].__HELP__
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
        f"Hey {name}, here’s a list of things I can do for you 🦋\nClick on any module below to explore!",
        keyb,
    )


@app.on_callback_query(filters.regex(r"help_(.*?)"))
@use_chat_lang()
async def help_button(self: Client, query: CallbackQuery, strings):
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    top_text = strings("help_txt").format(
        kamuh=query.from_user.first_name, bot=self.me.first_name
    )

    if mod_match:
        module = mod_match[1].replace(" ", "_")
        text = strings("help_name").format(mod=HELPABLE[module].__MODULE__) + HELPABLE[module].__HELP__
        if module == "federation":
            return await query.message.edit(
                text=text,
                reply_markup=FED_MARKUP,
                disable_web_page_preview=True,
            )
        await query.message.edit_msg(
            text=text,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(strings("back_btn"), callback_data="help_back")]]
            ),
            disable_web_page_preview=True,
        )

    elif prev_match:
        curr_page = int(prev_match[1])
        await query.message.edit_msg(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(paginate_modules(curr_page - 1, HELPABLE, "help")),
            disable_web_page_preview=True,
        )

    elif next_match:
        next_page = int(next_match[1])
        await query.message.edit_msg(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(paginate_modules(next_page + 1, HELPABLE, "help")),
            disable_web_page_preview=True,
        )

    elif back_match:
        await query.message.edit_msg(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help")),
            disable_web_page_preview=True,
        )

    with contextlib.suppress(Exception):
        await self.answer_callback_query(query.id)
