import asyncio
from typing import Dict, Union
from nonebot import get_plugin_config, on_type
from nonebot.adapters.onebot.v11 import GroupMessageEvent, GroupRecallNoticeEvent
from nonebot.adapters.onebot.v11.bot import Bot
from .config import config

cfg = get_plugin_config(config)


def sticker_rule(event: GroupMessageEvent) -> bool:
    if not in_group(event):
        return False
    
    for msg in event.message:
        try:
            if msg.type == "mface" or msg.data["summary"] == "[动画表情]":
                return True
        except:
            continue
    return False


def in_group(event: Union[GroupMessageEvent, GroupRecallNoticeEvent]) -> bool:
    if (
        str(event.group_id) in cfg.ban_sticker_enable_groups
        or int(event.group_id) in cfg.ban_sticker_enable_groups
    ):
        return True
    else:
        return False


on_sticker = on_type(GroupMessageEvent, rule=sticker_rule, priority=7, block=False)
on_recall = on_type(GroupRecallNoticeEvent, rule=in_group, priority=7, block=False)

pending_bans: Dict[int, asyncio.Event] = {}
ban_lock = asyncio.Lock()

@on_sticker.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    cancel_event = asyncio.Event()
    async with ban_lock:
        pending_bans[event.message_id] = cancel_event
    try:
        await asyncio.wait_for(cancel_event.wait(), timeout=cfg.ban_sticker_wait_time)
    except asyncio.TimeoutError:
        if not cancel_event.is_set():
            await bot.delete_msg(message_id=event.message_id)
            await bot.set_group_ban(
                group_id=event.group_id, user_id=event.user_id, duration=cfg.ban_sticker_ban_time
            )
    finally:
        async with ban_lock:
            if event.message_id in pending_bans:
                del pending_bans[event.message_id]
        await on_sticker.finish()

@on_recall.handle()
async def __(event: GroupRecallNoticeEvent):
    if event.message_id in pending_bans:
        async with ban_lock:
            cancel_event = pending_bans[event.message_id]
            cancel_event.set()
    await on_recall.finish()