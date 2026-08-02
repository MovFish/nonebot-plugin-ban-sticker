import asyncio
from dataclasses import dataclass, field
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


@dataclass
class PendingBan:
    message_ids: set[int] = field(default_factory=set)
    all_recalled: asyncio.Event = field(default_factory=asyncio.Event)


PendingKey = tuple[int, int]
pending_bans: Dict[PendingKey, PendingBan] = {}
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
            if (
                msg.type == "mface"
                or msg.data["summary"] == "[动画表情]"
                or "emoji_id" in msg.data
            ):
                return True
        except:
            continue
    return False


def recall_rule(event: GroupRecallNoticeEvent) -> bool:
    return in_group(event)


on_emoticon = on_type(GroupMessageEvent, rule=emoticon_rule, priority=7, block=False)
on_recall = on_type(GroupRecallNoticeEvent, rule=recall_rule, priority=7, block=False)


@on_emoticon.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    key = (event.group_id, event.user_id)
    async with ban_lock:
        batch = pending_bans.get(key)
        if batch is not None:
            batch.message_ids.add(event.message_id)
            is_first = False
        else:
            batch = PendingBan({event.message_id})
            pending_bans[key] = batch
            is_first = True

    if not is_first:
        return

    try:
        try:
            await asyncio.wait_for(
                batch.all_recalled.wait(), timeout=cfg.ban_sticker_wait_time
            )
            return
        except asyncio.TimeoutError:
            async with ban_lock:
                if pending_bans.get(key) is not batch:
                    return
                pending_bans.pop(key)
                remaining_message_ids = set(batch.message_ids)

            if not remaining_message_ids:
                return

            ban_count = cfg.ban_sticker_ban_time * (len(remaining_message_ids) ** 2)
            if ban_count > 0:
                await bot.set_group_ban(
                    group_id=event.group_id,
                    user_id=event.user_id,
                    duration=ban_count,
                )
            for message_id in remaining_message_ids:
                await bot.delete_msg(message_id=message_id)
    finally:
        async with ban_lock:
            if pending_bans.get(key) is batch:
                pending_bans.pop(key)
    await on_emoticon.finish()


@on_recall.handle()
async def __(event: GroupRecallNoticeEvent):
    key = (event.group_id, event.user_id)
    async with ban_lock:
        batch = pending_bans.get(key)
        if batch is None or event.message_id not in batch.message_ids:
            return
        batch.message_ids.discard(event.message_id)
        if not batch.message_ids:
            pending_bans.pop(key)
            batch.all_recalled.set()
    await on_recall.finish()
