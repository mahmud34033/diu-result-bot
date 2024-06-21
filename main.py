import requests as ree
import json
import asyncio
from datetime import datetime
from pytz import timezone
from aiogram import Bot, Dispatcher, executor, types
import os

from keep_alive import keep_alive
keep_alive()

bot = Bot(token=os.environ.get('token'))
dp = Dispatcher(bot)

user_list = {}
message_count = {}
blocked_users = set()

def get_current_time():
    return datetime.now().astimezone(timezone('Asia/Dhaka')).strftime("%d/%m/%Y %H:%M:%S")

def add_user(id, first_name, last_name):
    current_time = get_current_time()
    if id not in user_list:
        user_list[id] = {"first_name": first_name, "last_name": last_name, "join_time": current_time}
        message_count[id] = 0
        return True
    return False

def record_message(id):
    if id in message_count:
        message_count[id] += 1

def block_user(user_id):
    blocked_users.add(user_id)

def unblock_user(user_id):
    blocked_users.discard(user_id)

@dp.message_handler(commands=['users'])
async def count_user(message: types.Message):
    if message.from_user.id == ADMIN_ID:  # Replace with your admin user ID
        cnt = len(user_list)
        myuser = f'_Total users: {cnt}_'
        await message.reply(myuser, parse_mode="Markdown")
    else:
        await message.reply("You are not authorized to use this command.")

@dp.message_handler(commands=['stats'])
async def statistics(message: types.Message):
    if message.from_user.id == ADMIN_ID:  # Replace with your admin user ID
        stats = "*User Statistics:*\n\n"
        for user_id, user_info in user_list.items():
            stats += (f'ID: `{user_id}`\nName: {user_info["first_name"]} {user_info["last_name"]}\n'
                      f'Messages sent: {message_count[user_id]}\nJoined: {user_info["join_time"]}\n\n')
        await message.reply(stats, parse_mode="Markdown")
    else:
        await message.reply("You are not authorized to use this command.")

@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    idu = message.from_user.id
    current_time = get_current_time()
    if message.chat.type == 'private':
        if add_user(idu, message.from_user.first_name, message.from_user.last_name):
            nw = (f'*🚀 New Joined !!! [{current_time}]\nID: *`{idu}`\n'
                  f'*First name: {message.from_user.first_name}\nLast name: {message.from_user.last_name}*')
            await bot.send_message(5482855863, text=nw, parse_mode="Markdown")
    
    txt = (f'_==> id:_ \"`{message.from_user.id}`\"_, text: \"{message.text}\", '
           f'[date-time: {current_time}]_')
    await bot.send_message(5482855863, text=txt, parse_mode="Markdown")
    
    msg_start = (f"Hi, {message.from_user.first_name}\n\n"
                 f"Welcome to \"Fall'23 Result bot - DIU.\" 💐\n\n"
                 f"To see your result, enter your Student ID.\n\nExample: 222-15-6000")
    await message.reply(msg_start)

@dp.message_handler(commands=['block'])
async def handle_block(message: types.Message):
    if message.from_user.id == ADMIN_ID:  # Replace with your admin user ID
        try:
            user_id_to_block = int(message.text.split()[1])
            block_user(user_id_to_block)
            await message.reply(f"User {user_id_to_block} has been blocked.")
        except (IndexError, ValueError):
            await message.reply("Usage: /block <user_id>")
    else:
        await message.reply("You are not authorized to use this command.")

@dp.message_handler(commands=['unblock'])
async def handle_unblock(message: types.Message):
    if message.from_user.id == ADMIN_ID:  # Replace with your admin user ID
        try:
            user_id_to_unblock = int(message.text.split()[1])
            unblock_user(user_id_to_unblock)
            await message.reply(f"User {user_id_to_unblock} has been unblocked.")
        except (IndexError, ValueError):
            await message.reply("Usage: /unblock <user_id>")
    else:
        await message.reply("You are not authorized to use this command.")

@dp.message_handler(commands=['blocklist'])
async def handle_blocked(message: types.Message):
    if message.from_user.id == ADMIN_ID:  # Replace with your admin user ID
        if blocked_users:
            blocked_list = "\n".join([str(user_id) for user_id in blocked_users])
            await message.reply(f"Blocked users:\n{blocked_list}")
        else:
            await message.reply("No users are currently blocked.")
    else:
        await message.reply("You are not authorized to use this command.")

async def send_processing_message(chat_id, progress):
    message = await bot.send_message(chat_id, f"_⏳ Processing: {progress}%_", parse_mode="Markdown")
    return message

async def update_processing_message(message, progress):
    if progress == 1:     p = "⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪"
    elif progress == 11:  p = "🟢⚪⚪⚪⚪⚪⚪⚪⚪⚪"
    elif progress == 21:  p = "🟢🟢⚪⚪⚪⚪⚪⚪⚪⚪"
    elif progress == 31:  p = "🟢🟢🟢⚪⚪⚪⚪⚪⚪⚪"
    elif progress == 41:  p = "🟢🟢🟢🟢⚪⚪⚪⚪⚪⚪"
    elif progress == 51:  p = "🟢🟢🟢🟢🟢⚪⚪⚪⚪⚪"
    elif progress == 61:  p = "🟢🟢🟢🟢🟢🟢⚪⚪⚪⚪"
    elif progress == 71:  p = "🟢🟢🟢🟢🟢🟢🟢⚪⚪⚪"
    elif progress == 81:  p = "🟢🟢🟢🟢🟢🟢🟢🟢⚪⚪"
    elif progress == 91:  p = "🟢🟢🟢🟢🟢🟢🟢🟢🟢⚪"
    elif progress == 100: p = "🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢"
    
    await message.edit_text(f"_⏳ Processing: {progress}%_\n{p}", parse_mode="Markdown")

async def delete_message(message):
    await message.delete()

@dp.message_handler()
async def echo(message: types.Message):
    user_id = message.from_user.id
    if user_id in blocked_users:
        await message.reply("You are blocked from using this bot.")
        return

    try:
        record_message(user_id)
        current_time = get_current_time()
        txt = f'_==> id:_ \"`{user_id}`\"_, text: \"{message.text}\", [date-time: {current_time}]_'
        await bot.send_message(5482855863, text=txt, parse_mode="Markdown")
        
        stu_id = message.text

        # Sending the initial processing message
        processing_message = await send_processing_message(message.chat.id, 0)

        # Simulating the progress
        for i in range(1, 41, 10):
            await asyncio.sleep(0.5)
            await update_processing_message(processing_message, i)

        # Fetching the result after the progress bar simulation
        url_result = ree.get(f'API_KEY')
        res = url_result.text

        res = res.replace("[", "").replace("]", "").replace("},", "}},").replace("null", "\"null\"").split("},")

        # Simulating the progress 2
        for i in range(41, 81, 10):
            await asyncio.sleep(0.5)
            await update_processing_message(processing_message, i)
        
        url_info = ree.get(f'API_KEY')
        info = url_info.text
        info = json.loads(info)

        for_print = (f"*Student ID : {info['studentId']}\n"
                     f"Name : {info['studentName']}\n"
                     f"Program : {info['progShortName']}\n"
                     f"Batch : {info['batchNo']}*\n\n")

        t = 0
        for x in res:
            x = json.loads(x)
            t += x["totalCredit"]

        lst = []
        cnt = 0
        mycgpa = ""
        for x in res:
            x = json.loads(x)
            lst.append(x["cgpa"])
            if str(x["cgpa"]) != "null":
                mycgpa = str(x["cgpa"])
                cnt += 1

        if cnt != len(lst):
            mycgpa = "null"

        for x in range(len(res)):
            res[x] = json.loads(res[x])
            if x == 0:
                for_print += (f"Semester : {res[x]['semesterName']} {res[x]['semesterYear']}\n"
                              f"SGPA : {mycgpa}\nTotal Credits : {int(t)}")
            
            for_print += f"\n[[+]] {res[x]['customCourseId']} - {res[x]['courseTitle']} - {res[x]['pointEquivalent']}"

        if mycgpa == "null":
            nb = "\n\n_⚠️ N.B. : If you see \"null\" in any course. That means \"Teaching Evaluation\" is not yet complete._"
            for_print += nb

        # Simulating the progress 3
        for i in range(81, 101, 10):
            await asyncio.sleep(0.5)
            await update_processing_message(processing_message, i)
            if i == 91:
                await asyncio.sleep(0.5)
                await update_processing_message(processing_message, 100)

        # Deleting the processing message once fetching is complete
        await delete_message(processing_message)

        await message.reply(for_print, parse_mode="Markdown")
        
    except Exception as e:
        # Deleting the processing message once fetching is complete
        await delete_message(processing_message)
        
        msg = "Wrong input.\nPlease enter valid Student ID"
        await message.reply(msg)

if __name__ == '__main__':
    print("Running...")
    executor.start_polling(dp)
