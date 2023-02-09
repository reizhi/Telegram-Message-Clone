import asyncio
import time
from pyrogram import Client
from pyrogram.client import Cache
from pyrogram import filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
uvloop.install()

api_id = 114514
api_hash = "qwe123zxc000"
app = Client("tmc", api_id=api_id, api_hash=api_hash)
app.message_cache = Cache(1000000)
jobs = {-1005555555: [-10066666666, -100777777777]}

#以下无需改动
gm = {}
for i in jobs:
    gm[i] = {"gid": "", "mid" : ""}
last_msg = 0
#媒体组复制
async def copy_group(sid, mid):
    for cp in jobs[sid]:
        await app.copy_media_group(chat_id = cp, from_chat_id = sid, message_id = mid)
        time.sleep(0.8)
#独立消息复制
async def copy_msg(message):
    for cp in jobs[message.chat.id]:
        await app.copy_message(chat_id = cp, from_chat_id = message.chat.id, message_id = message.id)
        time.sleep(0.8)


@app.on_message(filters.group)
async def message_cp(client, message):
    global gm
    if (message.chat.id in jobs):
        last_msg = time.time()
        print(gm)
        tmp_sid = message.chat.id
        tmp_mid = gm[message.chat.id]["mid"]
        #媒体组
        if (message.media_group_id):
            if (gm[message.chat.id]["gid"] != "" and gm[message.chat.id]["gid"] != message.media_group_id):
                gm[message.chat.id]["gid"] = ""
                gm[message.chat.id]["mid"] = ""
                await copy_group(tmp_sid, tmp_mid)
            gm[message.chat.id]["gid"] = message.media_group_id
            gm[message.chat.id]["mid"] = message.id
        #一般消息
        else:
            if (gm[message.chat.id]["gid"] == ""):
                await copy_msg(message)
            else:
                gm[message.chat.id]["gid"] = ""
                gm[message.chat.id]["mid"] = ""
                await copy_group(tmp_sid, tmp_mid)
                await copy_msg(message)
#清空未发媒体组
async def cleanjob():
    if (time.time() - last_msg > 5):
        for cp in jobs:
            if (gm[cp]["gid"] != ""):
                for msg in jobs[cp]:
                    await app.copy_media_group(chat_id = msg, from_chat_id = cp, message_id = gm[cp]["mid"])
                gm[cp]["gid"] = ""
                gm[cp]["mid"] = ""
#定时运行清空
scheduler = AsyncIOScheduler()
scheduler.add_job(cleanjob, "interval", seconds = 5)

scheduler.start()
app.run()