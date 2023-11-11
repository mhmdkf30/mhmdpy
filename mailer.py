import telebot
import json
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

API_KEY = "6734006910:AAHrXzHiKI-1e-TbrcdYHK03SviTR0NxOKo"
bot = telebot.TeleBot(API_KEY)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"mode": None, "mails": []}

    bot.send_message(chat_id, """
    اهلا بك في بوت ارسال الرسائل الإلكترونية التلقائي
    """)
    show_keyboard(chat_id)

def show_keyboard(chat_id):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row("أضف بريدات", "حذف البريدات")
    markup.row("عرض البريدات المضافة", "ارسال رسالة")
    bot.send_message(chat_id, "اختر الإجراء الذي ترغب في تنفيذه:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "أضف بريدات")
def add_email_step1(message):
    chat_id = message.chat.id
    user_data[chat_id]["mode"] = "addmail"
    bot.send_message(chat_id, "ارسل الآن البريد الإلكتروني الذي تريد إضافته:")

@bot.message_handler(func=lambda message: user_data[message.chat.id]["mode"] == "addmail")
def add_email_step2(message):
    chat_id = message.chat.id
    email = message.text

    if email not in user_data[chat_id]["mails"]:
        user_data[chat_id]["mails"].append(email)
        bot.send_message(chat_id, "تم الحفظ والإضافة ✅")
    else:
        bot.send_message(chat_id, "البريد الإلكتروني موجود بالفعل.")

    user_data[chat_id]["mode"] = None
    show_keyboard(chat_id)

@bot.message_handler(func=lambda message: message.text == "حذف البريدات")
def delete_emails(message):
    chat_id = message.chat.id
    user_data[chat_id]["mode"] = "delmail"
    keyboard = telebot.types.InlineKeyboardMarkup()
    for i, email in enumerate(user_data[chat_id]["mails"]):
        callback_data = f"delt_{i}"
        keyboard.add(telebot.types.InlineKeyboardButton(email, callback_data=callback_data))
    bot.send_message(chat_id, "اختر البريد الإلكتروني الذي تريد حذفه:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith("delt_"))
def delete_email_callback(call):
    chat_id = call.message.chat.id
    email_index = int(call.data.split("_")[1])

    if email_index < len(user_data[chat_id]["mails"]):
        deleted_email = user_data[chat_id]["mails"].pop(email_index)
        bot.send_message(chat_id, f"تم حذف البريد الإلكتروني: {deleted_email} ✅")

    user_data[chat_id]["mode"] = None
    show_keyboard(chat_id)

@bot.message_handler(func=lambda message: message.text == "عرض البريدات المضافة")
def view_emails(message):
    chat_id = message.chat.id
    if not user_data[chat_id]["mails"]:
        bot.send_message(chat_id, "لم تقم بإضافة أي بريد إلكتروني بعد.")
    else:
        email_list = "\n".join(user_data[chat_id]["mails"])
        bot.send_message(chat_id, f"البريدات المضافة:\n{email_list}")
    show_keyboard(chat_id)

@bot.message_handler(func=lambda message: message.text == "ارسال رسالة")
def send_email_step1(message):
    chat_id = message.chat.id
    user_data[chat_id]["mode"] = "sendms"
    bot.send_message(chat_id, "ارسل البريد الإلكتروني الذي تريد إرسال الرسالة إليه:")

@bot.message_handler(func=lambda message: user_data[message.chat.id]["mode"] == "sendms")
def send_email_step2(message):
    chat_id = message.chat.id
    email = message.text
    if "@" not in email:
        bot.send_message(chat_id, "بريد إلكتروني غير صالح. الرجاء إعادة المحاولة.")
        return

    user_data[chat_id]["mode"] = "s2"
    user_data[chat_id]["to"] = email
    bot.send_message(chat_id, "ارسل لي الموضوع الخاص بالرسالة:")

@bot.message_handler(func=lambda message: user_data[message.chat.id]["mode"] == "s2")
def send_email_step3(message):
    chat_id = message.chat.id
    subject = message.text

    user_data[chat_id]["mode"] = "s3"
    user_data[chat_id]["sub"] = subject
    bot.send_message(chat_id, "ارسل النص الذي ترغب في إرساله:")

@bot.message_handler(func=lambda message: user_data[message.chat.id]["mode"] == "s3")
def send_email_step4(message):
    chat_id = message.chat.id
    text = message.text

    user_data[chat_id]["mode"] = "s4"
    user_data[chat_id]["msg"] = text
    bot.send_message(chat_id, "كم مرة تريد إرسال هذه الرسالة:")

@bot.message_handler(func=lambda message: user_data[message.chat.id]["mode"] == "s4")
def send_email_step5(message):
    chat_id = message.chat.id
    count = message.text

    if not count.isnumeric():
        bot.send_message(chat_id, "برجاء إدخال رقم صحيح.")
        return

    user_data[chat_id]["mode"] = "s5"
    user_data[chat_id]["msgs"] = count

    email = user_data[chat_id]["to"]
    subject = user_data[chat_id]["sub"]
    text = user_data[chat_id]["msg"]
    count = int(count)


    send_email(chat_id, email, subject, text, count)

def send_email(chat_id, email, subject, text, count):

##اصنع حساب بداخل مايكروسوفت وخلي معلوماتك باسورد وايميل حطه بلفراغات
    smtp_server = "smtp.office365.com"
    smtp_port = 587  
    smtp_username = "mhmdkf30@outlook.com"
    smtp_password = "12345mm67"


    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)

    for _ in range(count):
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(text, 'plain'))

        server.sendmail(smtp_username, email, msg.as_string())

    server.quit()

    bot.send_message(chat_id, f"تم إرسال الرسالة إلى {email} {count} مرة.")

    user_data[chat_id]["mode"] = None
    show_keyboard(chat_id)

if __name__ == "__main__":
    bot.polling(none_stop=True)
