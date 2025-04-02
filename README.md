<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-ban-sticker
_✨ 如果你希望在你群禁用表情包 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/owner/nonebot-plugin-ban-sticker.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-ban-sticker">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-ban-sticker.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>

## 📖 介绍

本插件可以帮助群管在群内禁用表情包。当用户发送表情包时，插件会自动进行处理，测绘表情包并对用户进行禁言。

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot_plugin_ban_sticker

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot_plugin_ban_sticker
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_ban_sticker"]

</details>

## ⚙️ 配置

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| `ban_sticker_enable_groups` | 否 | `[]` |  需要启用本插件的群组ID列表，为空列表时表示在所有群组不启用。 |
| `ban_sticker_wait_time` | 否 | `120` |  等待用户撤回表情包的时间，单位为秒。在这个时间内，如果用户撤回了表情包，则不会进行禁言。 |
| `ban_sticker_ban_time` | 否 | `3600` |  禁言时长基数，单位为秒。实际禁言时长会根据用户连续发送的表情包数量的平方进行计算。 |
