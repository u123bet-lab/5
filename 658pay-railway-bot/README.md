# 658pay Telegram Bot — Railway 版本

## Railway Variables

在 Railway → Service → Variables 添加：

- `BOT_TOKEN` = BotFather 提供的完整 Token
- `WEBHOOK_SECRET` = 32～256 位英文字母、数字、下划线或短横线随机字符串
- `WEBSITE_URL` = `https://jianzhi.jianzhi710731.workers.dev/`

不要把真实 Token 或 Secret 提交到 GitHub。

## 部署

1. 将本项目上传到 GitHub。
2. Railway → New Project → Deploy from GitHub Repo。
3. 选择这个仓库。
4. 在 Variables 添加上面三个变量。
5. 等部署成功。
6. Railway → Settings → Networking → Generate Domain。
7. 得到 HTTPS 域名后，打开：
   `https://你的域名/setup`
8. 输入与 Railway `BOT_TOKEN` 完全相同的 BotFather Token。
9. 点击“绑定 Telegram 机器人”。
10. 页面返回“绑定成功”后，去 Telegram 给机器人发送 `/start`。

## Webhook

绑定成功后自动设置为：

`https://你的Railway域名/webhook`

不需要手动运行 setup.ps1。

## 功能

- `/start`、`/menu`：显示三个入口
- `/website`：网站
- `/channel`：TG 频道
- `/support`：客服
- `/help`：帮助
- 仅处理私聊消息
- 网站：jianzhi.jianzhi710731.workers.dev
- 频道：@dnyxw006
- 客服：@ID658pay
