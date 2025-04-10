import profile
from tkinter.font import names
from xml.sax import parse

from pyexpat.errors import messages
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from gpt import *
from util import *


async def start(update, context):
    dialog.mode = "main"
    text = load_message("main")
    await send_photo(update, context, "main")
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        "start": "главное меню бота",
        "profile": "генерация Tinder-профля 😎",
        "opener": "сообщение для знакомства 🥰",
        "message": "переписка от вашего имени 😈",
        "date": "переписка со звездами 🔥",
        "gpt": "задать вопрос чату GPT 🧠"

    })


async def gpt(update, context):
    dialog.mode = "gpt"
    text = load_message("gpt")
    await send_photo(update, context, "gpt")
    await send_text(update, context, text)


async def date(update, context):
    dialog.mode = "date"
    text = load_message("date")
    await send_photo(update, context, "date")
    await send_text_buttons(update, context, text, {
        "date_grande": "Ариана Гранде",
        "date_robbie": "Марго Робби",
        "date_zendaya": "Зендея",
        "date_gosling": "Райан Гослинг",
        "date_hardy": "Том Харди"
    })


async def dateDialog(update, context):
    text = update.message.text
    my_message = await send_text(update, context, "Собеседник набирает текст...")
    answer = await chatGpt.add_message(text)
    await my_message.edit_text(answer)


async def date_buttons(update, context):
    text = update.callback_query.data
    await update.callback_query.answer()
    await send_photo(update, context, text)
    await send_text(update, context, "Отличный выбор! Теперь начните диалог")
    prompt = load_prompt(text)
    chatGpt.set_prompt(prompt)


async def message(update, context):
    dialog.mode = "message"
    text = load_message("message")
    await send_photo(update, context, "message")
    await send_text_buttons(update, context, text, {
        "message_next": "Следующее сообщение",
        "message_date": "Пригласить на свидание"
    })
    dialog.list.clear()


async def message_buttons(update, context):
    text = update.callback_query.data
    await update.callback_query.answer()
    prompt = load_prompt(text)
    user_chat_history = "\n\n".join(dialog.list)

    messageAwait = await send_text(update, context, "ChatGpt🧠 думает над вариантом ответа")
    answer = await chatGpt.send_question(prompt, user_chat_history)
    await messageAwait.edit_text(answer)


async def messageDialog(update, context):
    text = update.message.text
    dialog.list.append(text)


async def profile(update, context):
    dialog.mode = "profile"
    text = load_message("profile")
    await send_photo(update, context, "profile")
    await send_text(update, context, text)
    dialog.user.clear()
    dialog.counter = 0
    await send_text(update, context, "Сколько вам лет?")


async def profileDialog(update, context):
    text = update.message.text
    dialog.counter += 1
    match dialog.counter:
        case 1:
            dialog.user["age"] = text
            await send_text(update, context, "Кем вы работаете?")
        case 2:
            dialog.user["occupation"] = text
            await send_text(update, context, "У вас есть хобби?")
        case 3:
            dialog.user["hobby"] = text
            await send_text(update, context, "Что вам не нравится в людях?")
        case 4:
            dialog.user["annoys"] = text
            await send_text(update, context, "Цель знакомства")
        case 5:
            dialog.user["goals"] = text
            prompt = load_prompt("profile")
            profileAnswers = dialog_user_info_to_str(dialog.user)
            message = await send_text(update, context, "ChatGpt🧠 готовит profile")
            answerGpt = await chatGpt.send_question(prompt, profileAnswers)
            await message.edit_text(answerGpt)


async def opener(update, context):
    dialog.mode = "opener"
    text = load_message("opener")
    await send_photo(update, context, "opener")
    await send_text(update, context, text)
    dialog.user.clear()
    dialog.counter = 0
    await send_text(update, context, "Имя девушки?")

async def openerDialog(update, context):
    text = update.message.text
    dialog.counter += 1
    match dialog.counter:
        case 1:
            dialog.user["name"] = text
            await send_text(update, context, "Сколько ей лет?")
        case 2:
            dialog.user["age"] = text
            await send_text(update, context, "Оцените ее внешность 1-10 баллов")
        case 3:
            dialog.user["handsome"] = text
            await send_text(update, context, "Кем она работает?")
        case 4:
            dialog.user["occupation"] = text
            await send_text(update, context, "Цель знакомства")
        case 5:
            dialog.user["goals"] = text
            prompt = load_prompt("opener")
            profileAnswers = dialog_user_info_to_str(dialog.user)
            message = await send_text(update, context, "ChatGpt🧠 готовит первое сообщение")
            answerGpt = await chatGpt.send_question(prompt, profileAnswers)
            await message.edit_text(answerGpt)




async def mood_buttons(update, context):
    query = update.callback_query.data
    match (query):
        case "good":
            await send_text(update, context, "Отлично, я рад за тебя");
        case "average":
            await send_text(update, context, "Drink cup of coffee")
        case "bad":
            await send_text(update, context, "What should i do to cheer you up?")

async def gptDialog(update, context):
    text = update.message.text
    prompt = load_prompt("gpt")
    answerOfChatGpt = await chatGpt.send_question(prompt, text)
    await send_text(update, context, answerOfChatGpt)
async def hello(update, context):
    if dialog.mode == "gpt":
        await gptDialog(update, context)
    if dialog.mode == "date":
        await dateDialog(update, context)
    if dialog.mode == "message":
        await messageDialog(update, context)
    if dialog.mode == "profile":
        await profileDialog(update, context)
    if dialog.mode == "opener":
        await openerDialog(update, context)
    else:
        await send_text(update, context, "*Здарова, как сам?*")
        await send_text(update, context, "Ваше сообщение было \"_" + update.message.text + "_\"")
        await send_text_buttons(update, context, "Выберите своё настроение", {
            "good": "Хорошее",
            "average": "Среднее",
            "bad": "Плохое"
        })


dialog = Dialog()
dialog.mode = None
dialog.list = []
dialog.counter = 0
dialog.user = {}
chatGpt = ChatGptService(
    token="${token}")

print("App working")
app = ApplicationBuilder().token("8077741884:AAHqikyhHwbsFHSvYqoBNTNS7EYJQACR-0Y").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("date", date))
app.add_handler(CommandHandler("message", message))
app.add_handler(CommandHandler("profile", profile))
app.add_handler(CommandHandler("opener", opener))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))

app.add_handler(CallbackQueryHandler(date_buttons, pattern="^date_.*"))
app.add_handler(CallbackQueryHandler(message_buttons, pattern="^message_.*"))
app.add_handler(CallbackQueryHandler(mood_buttons))

app.run_polling()
