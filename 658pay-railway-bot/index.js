import express from 'express';

const app = express();
app.use(express.urlencoded({ extended: false }));
app.use(express.json({ limit: '64kb' }));

const CHANNEL = 'https://t.me/dnyxw006';
const SUPPORT = 'https://t.me/ID658pay';
const DEFAULT_WEBSITE = 'https://jianzhi.jianzhi710731.workers.dev/';

function getConfig() {
  const BOT_TOKEN = process.env.BOT_TOKEN || '';
  const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET || '';
  const WEBSITE_URL = process.env.WEBSITE_URL || DEFAULT_WEBSITE;

  if (!BOT_TOKEN || !/^[A-Za-z0-9_-]{32,256}$/.test(WEBHOOK_SECRET)) {
    throw new Error('Missing bot configuration');
  }

  const url = new URL(WEBSITE_URL);
  if (url.protocol !== 'https:' || url.username || url.password) {
    throw new Error('WEBSITE_URL must be a public HTTPS URL');
  }

  return { BOT_TOKEN, WEBHOOK_SECRET, WEBSITE_URL: url.href };
}

async function telegramCall(method, payload = {}) {
  const { BOT_TOKEN } = getConfig();
  const response = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/${method}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(10000),
  });

  const data = await response.json();
  if (!response.ok || !data.ok) {
    throw new Error('Telegram API failed');
  }
  return data.result;
}

function setupPage(message = '') {
  const safeMessage = String(message)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;');

  return new Response(`<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>658pay 机器人绑定</title>
<style>
body{font:16px system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;max-width:560px;margin:60px auto;padding:24px;color:#14254a}
input,button{box-sizing:border-box;width:100%;padding:14px;margin:12px 0;font:inherit}
button{background:#2457dd;color:white;border:0;border-radius:8px;cursor:pointer}
.notice{padding:12px;background:#f4f6fa;border-radius:8px}
</style>
</head>
<body>
<h1>658pay 机器人绑定</h1>
<p>仅管理员操作：输入与 Railway Secret 相同的 BOT_TOKEN，点击后将此服务绑定到你的 Telegram 机器人，并设置命令菜单。如有旧 webhook，会被替换。</p>
<p>Token 只通过 HTTPS 提交到本服务，不写入页面、URL 或日志。</p>
${safeMessage ? `<p class="notice">${safeMessage}</p>` : ''}
<form method="post" action="/setup">
<label for="token">BOT_TOKEN</label>
<input id="token" name="token" type="password" autocomplete="off" required>
<button type="submit">绑定 Telegram 机器人</button>
</form>
</body>
</html>`, {
    status: 200,
    headers: {
      'Content-Type': 'text/html; charset=utf-8',
      'Cache-Control': 'no-store',
      'Content-Security-Policy': "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'",
      'Referrer-Policy': 'no-referrer',
    },
  });
}

async function handleSetup(req, res) {
  if (req.method === 'GET') {
    return res.status(200).send(await setupPage().then(r => r.text()));
  }

  const origin = `${req.protocol}://${req.get('host')}`;
  const requestOrigin = req.get('origin');
  if (requestOrigin && requestOrigin !== origin) {
    return res.status(403).send('Forbidden');
  }

  let config;
  try {
    config = getConfig();
  } catch {
    return res.status(503).send(await setupPage('请先在 Railway 配置 BOT_TOKEN 和 WEBHOOK_SECRET，并重新部署。').then(r => r.text()));
  }

  const token = typeof req.body?.token === 'string' ? req.body.token : '';
  if (token !== config.BOT_TOKEN) {
    return res.status(403).send('Token 不匹配，请返回重试。');
  }

  try {
    const me = await telegramCall('getMe');
    const hook = `${origin}/webhook`;

    await telegramCall('setWebhook', {
      url: hook,
      secret_token: config.WEBHOOK_SECRET,
      allowed_updates: ['message'],
      drop_pending_updates: false,
    });

    await telegramCall('setMyCommands', {
      commands: [
        { command: 'start', description: 'Open 658pay menu' },
        { command: 'menu', description: 'Website, channel and support' },
        { command: 'website', description: 'Open website' },
        { command: 'channel', description: 'Telegram channel' },
        { command: 'support', description: 'Contact support' },
        { command: 'help', description: 'Help' },
      ],
    });

    const info = await telegramCall('getWebhookInfo');
    if (info.url !== hook) throw new Error('Webhook mismatch');

    return res.status(200).json({
      status: '绑定成功，请打开机器人并发送 /start',
      bot_url: `https://t.me/${me.username}`,
      webhook: info.url,
      pending_updates: info.pending_update_count,
    });
  } catch {
    return res.status(502).send(await setupPage('绑定未完成或仅部分完成，请检查 Token、Secret、Railway 网络和 Telegram API 后重试。').then(r => r.text()));
  }
}

function buildReply(message, website) {
  if (
    message?.chat?.type !== 'private' ||
    message.from?.is_bot ||
    typeof message.text !== 'string' ||
    !Number.isSafeInteger(message.chat.id)
  ) {
    return null;
  }

  const zh = (message.from?.language_code || '').startsWith('zh');
  const command = message.text.trim().split(/\s+/)[0].split('@')[0].toLowerCase();

  let text = zh
    ? '欢迎使用 658pay\n\n请选择下方入口：\n🌐 网站：查看介绍和任务演示\n📢 TG 频道：@dnyxw006\n💬 联系客服：@ID658pay'
    : 'Welcome to 658pay\n\nChoose an option below:\n🌐 Website: information and task demo\n📢 Telegram channel: @dnyxw006\n💬 Customer support: @ID658pay';

  if (command === '/help') {
    text = zh
      ? '658pay 使用帮助\n\n/start 或 /menu：显示入口\n/website：网站\n/channel：频道\n/support：客服\n\n点击按钮即可打开相应页面。此机器人不会代办付款，也不会索取密码、PIN 或验证码。'
      : '658pay help\n\n/start or /menu: show links\n/website: website\n/channel: channel\n/support: customer support\n\nTap a button to open its destination. This bot does not process payments or request passwords, PINs or verification codes.';
  } else if (command === '/support') {
    text = zh
      ? '客服账号：@ID658pay\n点击下方“联系客服”进入聊天。'
      : 'Customer support: @ID658pay\nTap Contact support below to open the chat.';
  } else if (command === '/channel') {
    text = zh
      ? 'TG 频道：@dnyxw006\n点击下方按钮打开频道。'
      : 'Telegram channel: @dnyxw006\nTap the channel button below.';
  } else if (command === '/website') {
    text = zh
      ? '点击下方“打开网站”查看 658pay 网站。'
      : 'Tap Open website below to visit 658pay website.';
  }

  return {
    chat_id: message.chat.id,
    text,
    link_preview_options: { is_disabled: true },
    reply_markup: {
      inline_keyboard: [
        [{ text: zh ? '🌐 打开网站' : '🌐 Open website', url: website }],
        [{ text: zh ? '📢 进入 TG 频道' : '📢 Telegram channel', url: CHANNEL }],
        [{ text: zh ? '💬 联系客服 @ID658pay' : '💬 Contact support @ID658pay', url: SUPPORT }],
      ],
    },
  };
}

app.get('/', (_req, res) => {
  res.type('text/plain').send('658pay bot endpoint. Open the bot in Telegram.');
});

app.all('/setup', async (req, res) => {
  await handleSetup(req, res);
});

app.post('/webhook', async (req, res) => {
  let config;
  try {
    config = getConfig();
  } catch {
    return res.status(503).send('Not configured');
  }

  if (req.get('X-Telegram-Bot-Api-Secret-Token') !== config.WEBHOOK_SECRET) {
    return res.status(403).send('Forbidden');
  }

  const update = req.body;
  const reply = buildReply(update?.message, config.WEBSITE_URL);

  if (!reply) return res.status(200).send('OK');

  try {
    const response = await fetch(`https://api.telegram.org/bot${config.BOT_TOKEN}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reply),
      signal: AbortSignal.timeout(10000),
    });

    const result = await response.json();

    if (response.ok && result.ok === true) {
      return res.status(200).send('OK');
    }

    if ([400, 403].includes(result.error_code)) {
      return res.status(200).send('OK');
    }

    return res.status(503).send('Telegram unavailable');
  } catch {
    return res.status(503).send('Telegram unavailable');
  }
});

app.use((_req, res) => {
  res.status(404).send('Not found');
});

const PORT = Number(process.env.PORT) || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`658pay bot server listening on port ${PORT}`);
});
