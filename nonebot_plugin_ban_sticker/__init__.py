import asyncio
from typing import Dict, Union
from nonebot import get_plugin_config, on_type
from nonebot.adapters.onebot.v11 import GroupMessageEvent, GroupRecallNoticeEvent
from nonebot.adapters.onebot.v11.bot import Bot
from .config import config

from nonebot.plugin import PluginMetadata

cfg = get_plugin_config(config)

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-ban-sticker",
    description="如果你希望在你群禁用表情包",
    usage="自动撤回表情包并禁言",
    type="application",
    homepage="https://github.com/MovFish/nonebot-plugin-ban-sticker",
    config=config,
    supported_adapters={"~onebot.v11"},
)

pending_bans: Dict[int, tuple[asyncio.Event, asyncio.Event]] = {}
pending_msg: Dict[int, list[int]] = {}
ban_lock = asyncio.Lock()


def in_group(event: Union[GroupMessageEvent, GroupRecallNoticeEvent]) -> bool:
    if (
        str(event.group_id) in cfg.ban_sticker_enable_groups
        or int(event.group_id) in cfg.ban_sticker_enable_groups
    ):
        return True
    else:
        return False


def emoticon_rule(event: GroupMessageEvent) -> bool:
    if not in_group(event):
        return False

    for msg in event.message:
        try:
            if msg.type == "mface" or msg.data["summary"] == "[动画表情]":
                return True
        except:
            continue
    return False


def recall_rule(event: GroupRecallNoticeEvent) -> bool:
    if not in_group(event):
        return False
    if (
        event.user_id in pending_bans
        and event.user_id in pending_msg
        and event.message_id in pending_msg[event.user_id]
    ):
        return True
    else:
        return False


on_emoticon = on_type(GroupMessageEvent, rule=emoticon_rule, priority=7, block=False)
on_recall = on_type(GroupRecallNoticeEvent, rule=recall_rule, priority=7, block=False)


@on_emoticon.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    async with ban_lock:
        if pending_msg.get(event.user_id, False):
            pending_msg[event.user_id].append(event.message_id)
            frist = False
        else:
            cancel_event = asyncio.Event()
            done_event = asyncio.Event()
            pending_bans[event.user_id] = (cancel_event, done_event)
            pending_msg[event.user_id] = [event.message_id]
            frist = True
    if frist:
        try:
            await asyncio.wait_for(
                pending_bans[event.user_id][0].wait(), timeout=cfg.ban_sticker_wait_time
            )
        except asyncio.TimeoutError:
            ban_count = cfg.ban_sticker_ban_time * (len(pending_msg[event.user_id])**2)
            if ban_count > 0:
                await bot.set_group_ban(
                    group_id=event.group_id,
                    user_id=event.user_id,
                    duration=ban_count,
                )
            await bot.delete_msg(message_id=event.message_id)
        finally:
            pending_bans[event.user_id][1].set()
            await asyncio.sleep(30)
            async with ban_lock:
                if event.user_id in pending_bans:
                    del pending_bans[event.user_id]
                if event.user_id in pending_msg:
                    del pending_msg[event.user_id]
    else:
        await pending_bans[event.user_id][1].wait()
        if not pending_bans[event.user_id][0].is_set():
            await bot.delete_msg(message_id=event.message_id)
    await on_emoticon.finish()


@on_recall.handle()
async def __(event: GroupRecallNoticeEvent):
    async with ban_lock:
        pending_msg[event.user_id].remove(event.message_id)
        if len(pending_msg[event.user_id]) == 0:
            pending_bans[event.user_id][0].set()
    await on_recall.finish()
