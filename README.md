# 658pay Telegram 客服机器人

这是一个 Python Long Polling 机器人，适合部署到 Railway。客户私聊机器人后，消息会复制到指定管理员的私人 Telegram；管理员只需**直接 Reply** 客户资料提示或客户消息副本，机器人就会把回复（文字、图片、视频、文件等）发回该客户。管理员真实账号不会暴露给客户。

## 功能

- 客户文字、图片、视频、语音、文件等消息复制到 `ADMIN_ID` 私聊。
- 将管理员侧的“客户资料提示”与“客户消息副本”的 `message_id → customer_id` 映射写入 SQLite；重启/重新部署后，映射仍可用于直接回复。
- 客户资料：Telegram ID、用户名、姓名、首次/最后联系时间、屏蔽状态。
- 管理员命令：`/users`、`/block <id>`、`/unblock <id>`、`/broadcast`。
- `/broadcast <文字>` 群发文字；或**回复一条媒体消息**后发送 `/broadcast [可选新说明]`，即可群发该媒体。
- 6 项 FAQ 和二级问题菜单；客户普通消息自动确认已收到。

> Telegram 限制：机器人只能主动联系曾经点过 Start 或给机器人发过消息的用户。请勿要求客户发送密码、OTP 或其他敏感登录凭证。

## 目录

```text
bot.py              启动入口和 Telegram 逻辑
database.py         SQLite 客户与回复映射
requirements.txt    Python 依赖
railway.json        Railway 启动配置
.env.example        环境变量样例
```

## 1. 用 BotFather 创建机器人

1. 在 Telegram 搜索并打开 `@BotFather`。
2. 输入 `/newbot`，按提示设置机器人名称和用户名。
3. BotFather 会给出一串 Token；复制后妥善保存，**不要**发到群聊、截图或提交到 GitHub。
4. 打开刚创建的机器人并点一次 **Start**。

## 2. 获取 ADMIN_ID

1. 在 Telegram 搜索 `@userinfobot`（或其他可信的 ID 查询机器人）。
2. 点 Start，复制它显示的数字 User ID。
3. 先给你的新机器人发 `/start`，否则机器人无法主动把客户消息发到你的私聊。

`ADMIN_ID` 必须是管理员的**数字用户 ID**，不是用户名，也不是机器人 ID。

## 3. 本地启动（可选）

要求 Python 3.10+。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:BOT_TOKEN="从 BotFather 得到的 Token"
$env:ADMIN_ID="你的数字 Telegram ID"
$env:DATABASE_PATH="./data/658pay.db"
python bot.py
```

启动日志出现 `Starting 658pay support bot` 后，用另一个 Telegram 账号向机器人发送文字和媒体进行测试。

## 4. 上传 GitHub

1. 在 GitHub 新建一个**私有**仓库，例如 `658pay-telegram-support-bot`。
2. 上传此目录内的文件：`bot.py`、`database.py`、`requirements.txt`、`railway.json`、`.env.example`、`.gitignore`、`README.md`。
3. 不要上传 `.env`、`data/` 或任何 `.db` 文件；`.gitignore` 已排除这些内容。

## 5. Railway 部署

1. 登录 Railway，选择 **New Project → Deploy from GitHub repo**，选择刚才的仓库。
2. 在服务的 **Variables** 添加：

```text
BOT_TOKEN=你的真实 BotFather Token
ADMIN_ID=你的 Telegram 数字用户 ID
DATABASE_PATH=/app/data/658pay.db
LOG_LEVEL=INFO
```

3. 在该服务添加 **Volume**，挂载路径填写 `/app/data`。
4. 重新部署。`railway.json` 会使用 `python bot.py` 启动 Long Polling。
5. 不需要设置 Web URL 或端口；此项目不使用 Webhook。

如果暂时未创建 Volume，机器人仍可运行，但 Railway 重建或重新部署后，客户记录和回复映射可能丢失。

## 6. 测试清单

1. 管理员账号先对机器人发送 `/start`。
2. 用另一账号发送文字、图片、视频和文件；管理员应收到资料提示和原消息副本。
3. 管理员分别回复资料提示、消息副本；客户应收到回复内容。
4. 管理员发送 `/users` 查看记录数；使用 `/block <客户ID>` 后再让该客户发消息，确认其不能继续联系支持；`/unblock <客户ID>` 后恢复。
5. 以管理员身份发送 `/broadcast Test notice`；再回复一条媒体消息并发送 `/broadcast Optional caption`。
6. 重启服务后，再回复一条重启前收到的客户资料提示或副本，确认 SQLite 映射仍然有效。

## 管理员命令参考

```text
/users
/block 123456789
/unblock 123456789
/broadcast Service notice: maintenance starts at 10:00.
```

媒体群发：先在管理员私聊中发送一张图片/视频/文件，再对该媒体使用 Telegram 的「回复」，发送：

```text
/broadcast Optional new caption
```

## 数据库与备份

默认路径为 `/app/data/658pay.db`，可用 `DATABASE_PATH` 覆盖。Railway Volume 是持久化目录；如需备份，请通过 Railway 的 Volume 工具导出数据库文件，并安全保管。数据库包含客户 Telegram ID 和联系资料，应限制访问权限。
