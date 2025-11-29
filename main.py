import os
import random
import time
import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ========== 基础配置 ==========
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ========== 菜单 ==========
def main_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🌤 每日开始", callback_data="menu_day")],
        [
            InlineKeyboardButton("✅ 习惯 & 小目标", callback_data="menu_habit"),
            InlineKeyboardButton("😊 情绪 & 心情", callback_data="menu_mood"),
        ],
        [
            InlineKeyboardButton("🧠 小测验 & 问答", callback_data="menu_quiz"),
            InlineKeyboardButton("📚 轻阅读 & 句子", callback_data="menu_read"),
        ],
        [
            InlineKeyboardButton("🎲 随机小功能", callback_data="menu_random"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def day_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("📅 今日一句", callback_data="day_sentence"),
            InlineKeyboardButton("📋 今日建议", callback_data="day_tip"),
        ],
        [
            InlineKeyboardButton("🧭 今日小方向", callback_data="day_direction"),
        ],
        [InlineKeyboardButton("⬅ 返回首页", callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def habit_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("✅ 小目标生成", callback_data="habit_goal"),
            InlineKeyboardButton("🔁 习惯微动作", callback_data="habit_action"),
        ],
        [
            InlineKeyboardButton("🧹 环境小整理", callback_data="habit_clean"),
            InlineKeyboardButton("🚶 微运动建议", callback_data="habit_move"),
        ],
        [InlineKeyboardButton("⬅ 返回首页", callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(habit_menu)


def mood_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("💬 心情短句", callback_data="mood_text"),
            InlineKeyboardButton("🎨 心情颜色", callback_data="mood_color"),
        ],
        [
            InlineKeyboardButton("🧘 简单放松", callback_data="mood_relax"),
            InlineKeyboardButton("❤️ 自我关怀", callback_data="mood_selfcare"),
        ],
        [InlineKeyboardButton("⬅ 返回首页", callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def quiz_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("🧠 小思考题", callback_data="quiz_think"),
            InlineKeyboardButton("🔢 数字小测试", callback_data="quiz_number"),
        ],
        [
            InlineKeyboardButton("👀 反应速度", callback_data="quiz_reaction"),
        ],
        [InlineKeyboardButton("⬅ 返回首页", callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(quiz_menu)


def read_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("📖 温柔句子", callback_data="read_soft"),
            InlineKeyboardButton("💡 想法火花", callback_data="read_idea"),
        ],
        [
            InlineKeyboardButton("📝 反思问题", callback_data="read_question"),
        ],
        [InlineKeyboardButton("⬅ 返回首页", callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(read_menu)


def random_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("🎲 随机数字", callback_data="rand_number"),
            InlineKeyboardButton("😊 随机表情", callback_data="rand_emoji"),
        ],
        [
            InlineKeyboardButton("📌 随机小任务", callback_data="rand_task"),
            InlineKeyboardButton("✨ 随机灵感", callback_data="rand_inspire"),
        ],
        [InlineKeyboardButton("⬅ 返回首页", callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(random_menu)


# ========== /start /help /about ==========
START_TEXT = (
    "👋 欢迎来到「轻享时光 · 生活小站」！\n\n"
    "这是一个专注 *日常小目标、情绪照顾、轻测验与随机灵感* 的中文机器人。\n\n"
    "你可以在这里：\n"
    "🌤 查看今日开始的小提示\n"
    "✅ 生成简单小目标和习惯微动作\n"
    "😊 用一句话或一种颜色表达心情\n"
    "🧠 做几个轻量思考题和小测试\n"
    "📚 阅读温柔句子与反思问题\n"
    "🎲 获取随机数字、表情、任务或灵感\n\n"
    "本机器人仅提供轻松、健康的文字互动，不涉及任何金钱、奖励、博彩、投资或敏感内容。\n\n"
    "👇 通过下方按钮选择你现在想体验的功能："
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            START_TEXT, reply_markup=main_menu(), parse_mode="Markdown"
        )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📝 使用说明\n\n"
        "• 发送 /start 打开主菜单\n"
        "• 通过底部按钮进入不同模块：每日开始 / 习惯小目标 / 情绪工具 / 小测验 / 轻阅读 / 随机小功能\n"
        "• 每个按钮都有对应的文字内容或互动\n"
        "• 如果界面卡住，可以重新发送 /start 回到首页\n"
    )
    await update.message.reply_text(text)


async def about_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "ℹ️ 关于「轻享时光 · 生活小站」\n\n"
        "这是一个帮你在碎片时间里轻松一下的小机器人：\n"
        "• 用小目标和微任务推动一点点改变\n"
        "• 用情绪工具照顾当下心情\n"
        "• 用小测验和轻阅读活动大脑\n"
        "所有内容均为健康、非商业、无敏感信息的文本互动。"
    )
    await update.message.reply_text(text)


# ========== 按钮总路由 ==========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    # 菜单切换
    if data == "menu_main":
        await query.edit_message_text("🏠 已返回首页：", reply_markup=main_menu())
        return
    if data == "menu_day":
        await query.edit_message_text("🌤 每日开始：", reply_markup=day_menu())
        return
    if data == "menu_habit":
        await query.edit_message_text("✅ 习惯 & 小目标：", reply_markup=habit_menu())
        return
    if data == "menu_mood":
        await query.edit_message_text("😊 情绪 & 心情：", reply_markup=mood_menu())
        return
    if data == "menu_quiz":
        await query.edit_message_text("🧠 小测验 & 问答：", reply_markup=quiz_menu())
        return
    if data == "menu_read":
        await query.edit_message_text("📚 轻阅读 & 句子：", reply_markup=read_menu())
        return
    if data == "menu_random":
        await query.edit_message_text("🎲 随机小功能：", reply_markup=random_menu())
        return

    # ===== 每日开始 =====
    if data == "day_sentence":
        sentences = [
            "今天也可以慢慢来，但别停下来。",
            "给今天定一个很小很小的目标就足够了。",
            "就算只是好好吃一顿饭，也是在认真生活。",
        ]
        await query.edit_message_text(
            "📅 今日一句：\n\n" + random.choice(sentences),
            reply_markup=day_menu(),
        )
        return

    if data == "day_tip":
        tips = [
            "可以试着今天少刷一点手机，多留一点时间给自己。",
            "挑一个你一直想整理的小角落，用 3 分钟处理一下。",
            "如果今天有点忙，试着把事情按照“必须 / 可以改天”分类。",
        ]
        await query.edit_message_text(
            "📋 今日建议：\n\n" + random.choice(tips),
            reply_markup=day_menu(),
        )
        return

    if data == "day_direction":
        directions = [
            "把今天当成“打基础”的一天，多做一点长期有用的小事。",
            "把今天当成“调整状态”的一天，允许自己放缓节奏。",
            "把今天当成“尝试新东西”的一天，试着做一个平时不会做的小动作。",
        ]
        await query.edit_message_text(
            "🧭 今日小方向：\n\n" + random.choice(directions),
            reply_markup=day_menu(),
        )
        return

    # ===== 习惯 & 小目标 =====
    if data == "habit_goal":
        goals = [
            "今天完成一个 5 分钟就能搞定的小目标。",
            "今天只专注完成一件你最在意的小事。",
            "给自己定一个“做到就行，不求完美”的目标。",
        ]
        await query.edit_message_text(
            "✅ 小目标建议：\n\n" + random.choice(goals),
            reply_markup=habit_menu(),
        )
        return

    if data == "habit_action":
        actions = [
            "喝一杯水，并在心里对自己说一句“辛苦了”。",
            "站起来伸展一下肩颈，活动 30 秒。",
            "把桌面上一样不常用的东西收起来。",
        ]
        await query.edit_message_text(
            "🔁 习惯微动作：\n\n" + random.choice(actions),
            reply_markup=habit_menu(),
        )
        return

    if data == "habit_clean":
        texts = [
            "挑一个抽屉 / 文件夹，用 2 分钟删掉或丢掉几样不再需要的东西。",
            "把桌面上散乱的东西集中摆放整齐一点，让视觉稍微清爽一点。",
        ]
        await query.edit_message_text(
            "🧹 环境小整理：\n\n" + random.choice(texts),
            reply_markup=habit_menu(),
        )
        return

    if data == "habit_move":
        moves = [
            "原地轻轻走动 30 秒，活动一下身体。",
            "做 10 下缓慢的深呼吸配合耸肩放松。",
            "站起来走到另一个房间再回来，当作一趟“迷你散步”。",
        ]
        await query.edit_message_text(
            "🚶 微运动建议：\n\n" + random.choice(moves),
            reply_markup=habit_menu(),
        )
        return

    # ===== 情绪 & 心情 =====
    if data == "mood_text":
        moods = [
            "觉得有点累也没关系，说明你一直在努力。",
            "情绪会有起伏，但你一直都值得被好好对待。",
            "可以允许自己不那么好状态的一天。",
        ]
        await query.edit_message_text(
            "💬 心情短句：\n\n" + random.choice(moods),
            reply_markup=mood_menu(),
        )
        return

    if data == "mood_color":
        colors = [
            "🔵 蓝色心情：适合安静、整理思绪。",
            "🟢 绿色心情：适合放松、听听音乐。",
            "🟡 黄色心情：适合和朋友聊聊天。",
            "🟣 紫色心情：适合写点东西或想点新点子。",
        ]
        await query.edit_message_text(
            "🎨 心情颜色提示：\n\n" + random.choice(colors),
            reply_markup=mood_menu(),
        )
        return

    if data == "mood_relax":
        text = (
            "🧘 简单放松练习：\n\n"
            "1️⃣ 找个舒服的姿势坐好\n"
            "2️⃣ 做 5 次缓慢的深呼吸\n"
            "3️⃣ 每次呼气时，想象把紧绷一点点放掉\n"
        )
        await query.edit_message_text(text, reply_markup=mood_menu())
        return

    if data == "mood_selfcare":
        texts = [
            "你可以对自己稍微宽容一点，不用每件事都做到完美。",
            "试着给今天的自己一个小小的肯定，比如“我已经很努力了”。",
        ]
        await query.edit_message_text(
            "❤️ 自我关怀：\n\n" + random.choice(texts),
            reply_markup=mood_menu(),
        )
        return

    # ===== 小测验 & 问答 =====
    if data == "quiz_think":
        qs = [
            "🧠 小思考：\n\n如果可以给今天取一个标题，你会取什么？",
            "🧠 小思考：\n\n最近有什么让你觉得“还不错”的小进步？",
        ]
        await query.edit_message_text(
            random.choice(qs),
            reply_markup=quiz_menu(),
        )
        return

    if data == "quiz_number":
        number = random.randint(10, 99)
        text = (
            f"🔢 小测试：\n\n请在心里从 {number} 开始，每次减 3，看看能走到多少？"
        )
        await query.edit_message_text(text, reply_markup=quiz_menu())
        return

    if data == "quiz_reaction":
        context.user_data["reaction_start"] = time.time()
        keyboard = [
            [InlineKeyboardButton("⚡ 现在点我！", callback_data="quiz_reaction_click")],
            [InlineKeyboardButton("⬅ 返回", callback_data="menu_quiz")],
        ]
        await query.edit_message_text(
            "看到按钮后立刻点击，测试反应速度：",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if data == "quiz_reaction_click":
        start = context.user_data.get("reaction_start")
        if not start:
            msg = "测试数据已失效，请在菜单中重新开始一次。"
        else:
            ms = int((time.time() - start) * 1000)
            msg = f"🎯 你的反应时间是：{ms} 毫秒。"
        await query.edit_message_text(msg, reply_markup=quiz_menu())
        return

    # ===== 轻阅读 & 句子 =====
    if data == "read_soft":
        sentences = [
            "你不需要一直很棒，只要偶尔记得喜欢自己就好。",
            "很多事不用一次做完，可以一点点来。",
        ]
        await query.edit_message_text(
            "📖 温柔句子：\n\n" + random.choice(sentences),
            reply_markup=read_menu(),
        )
        return

    if data == "read_idea":
        ideas = [
            "今天可以试着记录一件让你觉得“挺好的小事”。",
            "给未来一个月的自己写一行话，只写一行就够。",
        ]
        await query.edit_message_text(
            "💡 想法火花：\n\n" + random.choice(ideas),
            reply_markup=read_menu(),
        )
        return

    if data == "read_question":
        qs = [
            "📝 反思问题：\n\n如果把最近一周比作天气，你觉得像什么？",
            "📝 反思问题：\n\n有什么事情，其实你已经做得比以前好多了？",
        ]
        await query.edit_message_text(
            random.choice(qs),
            reply_markup=read_menu(),
        )
        return

    # ===== 随机小功能 =====
    if data == "rand_number":
        n = random.randint(0, 100)
        await query.edit_message_text(
            f"🎲 随机数字（0~100）：{n}",
            reply_markup=random_menu(),
        )
        return

    if data == "rand_emoji":
        emojis = ["😀", "😆", "😎", "🥳", "🤩", "🤗", "🙌", "🌈", "⭐", "✨", "🍀"]
        seq = " ".join(random.sample(emojis, 5))
        await query.edit_message_text(
            "😊 随机表情组合：\n\n" + seq,
            reply_markup=random_menu(),
        )
        return

    if data == "rand_task":
        tasks = [
            "拍一张你眼前觉得“还不错”的画面。",
            "找一件你现在就能完成的小事，并在 3 分钟内完成它。",
            "把手机放下 2 分钟，只是简单发发呆。",
        ]
        await query.edit_message_text(
            "📌 随机小任务：\n\n" + random.choice(tasks),
            reply_markup=random_menu(),
        )
        return

    if data == "rand_inspire":
        ins = [
            "也许可以为今天写一个主题词，比如：缓慢 / 调整 / 轻松。",
            "想一件可以让你在 5 分钟内感觉更舒服的小事。",
        ]
        await query.edit_message_text(
            "✨ 随机灵感：\n\n" + random.choice(ins),
            reply_markup=random_menu(),
        )
        return

    # 兜底
    await query.edit_message_text(
        "指令暂不支持，请发送 /start 回到首页。", reply_markup=main_menu()
    )


# ========== 主入口 ==========
def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN 环境变量未设置！")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("about", about_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("轻享时光 · 生活小站 Bot 已启动")
    app.run_polling()


if __name__ == "__main__":
    main()
