from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import date
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import json

TOKEN = "8660752399:AAG_q-PahDldxY6faIe9BgafnqRW5a0Iw00"

ADMIN_USERNAME = "cowboy0330"

GROUP_ID = -5123266102


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "딜러 스케줄 봇\n\n"
        "/today\n"
        "/schedule\n"
        "/vacation 2026-06-15\n"
        "/vacations\n"
        "/edit 2026-06-10 성민 윤용\n"
        "/groupid"
    )


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("schedule.json", "r", encoding="utf-8") as f:
            schedule = json.load(f)

        today_date = date.today().strftime("%Y-%m-%d")

        if today_date in schedule:
            dealers = schedule[today_date]

            await update.message.reply_text(
                f"📅 오늘 근무\n\n"
                f"{dealers[0]}\n"
                f"{dealers[1]}"
            )
        else:
            await update.message.reply_text(
                "오늘 등록된 스케줄이 없습니다."
            )

    except Exception as e:
        await update.message.reply_text(
            f"오류: {e}"
        )


async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("schedule.json", "r", encoding="utf-8") as f:
            schedule_data = json.load(f)

        text = "📅 전체 스케줄\n\n"

        for day, dealers in schedule_data.items():
            text += f"{day} : {dealers[0]} / {dealers[1]}\n"

        await update.message.reply_text(text)

    except Exception as e:
        await update.message.reply_text(
            f"오류: {e}"
        )


async def vacation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name

    if not context.args:
        await update.message.reply_text(
            "사용법:\n/vacation 2026-06-15"
        )
        return

    vacation_date = context.args[0]

    try:
        with open("vacations.json", "r", encoding="utf-8") as f:
            vacations = json.load(f)

        if user not in vacations:
            vacations[user] = []

        vacations[user].append(vacation_date)

        with open("vacations.json", "w", encoding="utf-8") as f:
            json.dump(
                vacations,
                f,
                ensure_ascii=False,
                indent=4
            )

        await update.message.reply_text(
            f"🏖 휴무 신청 완료\n\n"
            f"신청자 : {user}\n"
            f"날짜 : {vacation_date}"
        )

    except Exception as e:
        await update.message.reply_text(
            f"오류: {e}"
        )


async def vacations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("vacations.json", "r", encoding="utf-8") as f:
            vacations_data = json.load(f)

        if not vacations_data:
            await update.message.reply_text(
                "등록된 휴무가 없습니다."
            )
            return

        text = "🏖 휴무 신청 목록\n\n"

        for name, dates in vacations_data.items():
            text += f"{name}\n"

            for d in dates:
                text += f" - {d}\n"

            text += "\n"

        await update.message.reply_text(text)

    except Exception as e:
        await update.message.reply_text(
            f"오류: {e}"
        )


async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username

    if username != ADMIN_USERNAME:
        await update.message.reply_text(
            "관리자만 사용할 수 있습니다."
        )
        return

    if len(context.args) != 3:
        await update.message.reply_text(
            "사용법:\n/edit 2026-06-10 성민 윤용"
        )
        return

    work_date = context.args[0]
    dealer1 = context.args[1]
    dealer2 = context.args[2]

    try:
        with open("schedule.json", "r", encoding="utf-8") as f:
            schedule = json.load(f)

        schedule[work_date] = [dealer1, dealer2]

        with open("schedule.json", "w", encoding="utf-8") as f:
            json.dump(
                schedule,
                f,
                ensure_ascii=False,
                indent=4
            )

        await update.message.reply_text(
            f"✅ 수정 완료\n\n"
            f"{work_date}\n"
            f"{dealer1} / {dealer2}"
        )

    except Exception as e:
        await update.message.reply_text(
            f"오류: {e}"
        )


async def groupid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"그룹 ID\n\n{update.effective_chat.id}"
    )


async def send_daily_schedule(app):
    try:
        with open("schedule.json", "r", encoding="utf-8") as f:
            schedule = json.load(f)

        today_date = date.today().strftime("%Y-%m-%d")

        if today_date not in schedule:
            return

        dealers = schedule[today_date]

        await app.bot.send_message(
            chat_id=GROUP_ID,
            text=(
                f"📅 오늘 근무\n\n"
                f"{dealers[0]}\n"
                f"{dealers[1]}\n\n"
                f"출근 확인 부탁드립니다."
            )
        )

    except Exception as e:
        print(e)


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("today", today))
app.add_handler(CommandHandler("schedule", schedule))
app.add_handler(CommandHandler("vacation", vacation))
app.add_handler(CommandHandler("vacations", vacations))
app.add_handler(CommandHandler("edit", edit))
app.add_handler(CommandHandler("groupid", groupid))

# scheduler = AsyncIOScheduler()

# scheduler.add_job(
#     send_daily_schedule,
#     CronTrigger(hour=12, minute=0),
#     args=[app]
# )

# scheduler.start()

import asyncio

print("봇 실행 중...")
app.run_polling()
