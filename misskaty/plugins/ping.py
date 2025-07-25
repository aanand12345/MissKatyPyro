import platform
import time
from asyncio import Lock
from pyrogram import filters, __version__ as pyrover
from pyrogram.types import Message

from misskaty import app, botStartTime, misskaty_version as anu_version
from misskaty.helper.human_read import get_readable_time
from misskaty.vars import COMMAND_HANDLER

PING_LOCK = Lock()


@app.on_message(filters.command(["ping"], COMMAND_HANDLER))
async def anime_ping(_, ctx: Message):
    uptime = get_readable_time(time.time() - botStartTime)
    start = time.time()
    msg = await ctx.reply("⌛ Starting ping...")

    await msg.edit("🦋 Initializing <b>AnuCore Protocol...</b>")
    await msg.edit("⚡ Charging up <b>Chakra</b>...")
    await msg.edit("💫 Summoning <b>Spirit Network Link</b>...")
    await msg.edit("🔗 Establishing 🧿 <b>Connection</b>...")

    end = time.time()
    latency = round(end - start, 2)

    await msg.edit(
        f"✨ <b>Pong!</b>\n"
        f"⚡ <b>Response:</b> <code>{latency}s</code>\n"
        f"🕰️ <b>Uptime:</b> <code>{uptime}</code>\n"
        f"🐍 <b>Python:</b> <code>{platform.python_version()}</code>\n"
        f"📦 <b>Pyrogram:</b> <code>{pyrover}</code>\n"
        f"🦋 <b>Powered by:</b> <i>Anu Management Bot {anu_version}</i>"
    )
