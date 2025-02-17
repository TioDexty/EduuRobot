import asyncio
import html
import io
import os
import re
import sys
import traceback
from contextlib import redirect_stdout

import speedtest
from meval import meval
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import RPCError

from config import sudofilter
from localization import use_chat_lang
from utils import set_restarted

prefix = "!"


@Client.on_message(filters.command("sudos", prefix) & sudofilter)
async def sudos(c: Client, m: Message):
    await m.reply_text("Test")


@Client.on_message(filters.command("cmd", prefix) & sudofilter)
@use_chat_lang()
async def run_cmd(c: Client, m: Message, strings):
    cmd = m.text.split(maxsplit=1)[1]
    if re.match("(?i)poweroff|halt|shutdown|reboot", cmd):
        res = strings("forbidden_command")
    else:
        proc = await asyncio.create_subprocess_shell(cmd,
                                                     stdout=asyncio.subprocess.PIPE,
                                                     stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        res = ("<b>Output:</b>\n<code>{}</code>".format(html.escape(stdout.decode().strip())) if stdout else "") + \
              ("\n<b>Errors:</b>\n<code>{}</code>".format(html.escape(stderr.decode().strip())) if stderr else "")
    await m.reply_text(res)


@Client.on_message(filters.command("upgrade", prefix) & sudofilter)
@use_chat_lang()
async def upgrade(c: Client, m: Message, strings):
    sm = await m.reply_text("Upgrading sources...")
    proc = await asyncio.create_subprocess_shell("git pull --no-edit",
                                                 stdout=asyncio.subprocess.PIPE,
                                                 stderr=asyncio.subprocess.STDOUT)
    stdout = (await proc.communicate())[0]
    if proc.returncode == 0:
        if "Already up to date." in stdout.decode():
            await sm.edit_text("There's nothing to upgrade.")
        else:
            await sm.edit_text(strings("restarting"))
            set_restarted(sm.chat.id, sm.message_id)
            os.execl(sys.executable, sys.executable, *sys.argv)  # skipcq: BAN-B606
    else:
        await sm.edit_text(f"Upgrade failed (process exited with {proc.returncode}):\n{stdout.decode()}")
        proc = await asyncio.create_subprocess_shell("git merge --abort")
        await proc.communicate()


@Client.on_message(filters.command("eval", prefix) & sudofilter)
async def evals(c: Client, m: Message):
    text = m.text.split(maxsplit=1)[1]
    try:
        res = await meval(text, globals(), **locals())
    except:  # skipcq
        ev = traceback.format_exc()
        await m.reply_text(f"<code>{html.escape(ev)}</code>")
    else:
        try:
            await m.reply_text(f"<code>{html.escape(str(res))}</code>")
        except Exception as e:  # skipcq
            await m.reply_text(str(e))


@Client.on_message(filters.command("exec", prefix) & sudofilter)
async def execs(c: Client, m: Message):
    strio = io.StringIO()
    code = m.text.split(maxsplit=1)[1]
    exec("async def __ex(c, m): " + " ".join("\n " + l for l in code.split("\n")))  # skipcq: PYL-W0122
    with redirect_stdout(strio):
        try:
            await locals()["__ex"](c, m)
        except:  # skipcq
            return await m.reply_text(html.escape(traceback.format_exc()))

    if strio.getvalue().strip():
        out = f"<code>{html.escape(strio.getvalue())}</code>"
    else:
        out = "Command executed."
    await m.reply_text(out)


@Client.on_message(filters.command("speedtest", prefix) & sudofilter)
@use_chat_lang()
async def test_speed(c: Client, m: Message, strings):
    string = strings("speedtest")
    sent = await m.reply_text(string.format(host="", ping="", download="", upload=""))
    s = speedtest.Speedtest()
    bs = s.get_best_server()
    await sent.edit_text(string.format(host=bs["sponsor"], ping=int(bs["latency"]), download="", upload=""))
    dl = round(s.download() / 1024 / 1024, 2)
    await sent.edit_text(string.format(host=bs["sponsor"], ping=int(bs["latency"]), download=dl, upload=""))
    ul = round(s.upload() / 1024 / 1024, 2)
    await sent.edit_text(string.format(host=bs["sponsor"], ping=int(bs["latency"]), download=dl, upload=ul))


@Client.on_message(filters.command("restart", prefix) & sudofilter)
@use_chat_lang()
async def restart(c: Client, m: Message, strings):
    sent = await m.reply_text(strings("restarting"))
    set_restarted(sent.chat.id, sent.message_id)
    os.execl(sys.executable, sys.executable, *sys.argv)  # skipcq: BAN-B606


@Client.on_message(filters.command("leave", prefix) & sudofilter)
async def leave_chat(c: Client, m: Message):
    if len(m.command) == 1:
        try:
            await c.leave_chat(m.chat.id)
        except RPCError as e:
            print(e)
    else:
        chat_id = m.text.split(maxsplit=1)[1]
        try:
            await c.leave_chat(int(chat_id))
        except RPCError as e:
            print(e)


@Client.on_message(filters.command("del", prefix) & sudofilter)
async def del_message(c: Client, m: Message):
    try:
        await c.delete_messages(
            m.chat.id,
            m.reply_to_message.message_id
        )
    except RPCError as e:
        print(e)
    try:
        await c.delete_messages(
            m.chat.id,
            m.message_id
        )
    except RPCError as e:
        print(e)
