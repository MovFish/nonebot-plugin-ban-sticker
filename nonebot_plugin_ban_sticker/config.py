from pydantic import BaseModel


class config(BaseModel):
    ban_sticker_enable_groups: list = []
    ban_sticker_wait_time: int = 120
    ban_sticker_ban_time: int = 3600
