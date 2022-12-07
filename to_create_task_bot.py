from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, Dispatcher, executor, types
import re
import sqlite3 as sq
from aiogram.types.web_app_info import WebAppInfo
import config

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

conntt = 0

buttons_menu = [InlineKeyboardButton('Опубликовать ещё задачу', callback_data='create_task'),
                InlineKeyboardButton('Профиль', callback_data='profile'
                )
                ]
inline_kb2 = InlineKeyboardMarkup()
for i in buttons_menu:
    inline_kb2.add(i)


tags_raw = {r'(^| )(python)(\'?s)?($| )':'python',
            r'(^| )(java)(\'?s)?($| )':'java',
            r'(^| )(javascript)(\'?s)?($| )':'javascript',
            r'(^| )(binance)(\'?s)?($| )':'binance',
            r'(^| )(js)(\'?s)?($| )':'js',
            r'(^| )(c\+\+)(\'?s)?($| )':'c++',
            r'(^| )(c)(\'?s)?($| )':'c',
            r'(^| )(ruby)(\'?s)?($| )':'ruby',
            r'(^| )(swift)(\'?s)?($| )':'swift',
            r'(^| )(p2p)(\'?s)?($| )':'p2p',
            r'(^| )(php)(\'?s)?($| )':'php',
            r'(^| )(c#)(\'?s)?($| )':'c#',
            r'(^| )(flutter)(\'?s)?($| )':'flutter',
            r'(^| )(dart)(\'?s)?($| )':'dart'}
tags = ['python', 'java', 'javascript', 'js', 'ruby', 'swift', 'binance', 'p2p', 'php', 'c++','c#', 'c', 'dart', 'flutter']


def sql_start():
    global base, cur
    base = sq.connect('./cool.db')
    cur = base.cursor()
    base.execute("CREATE TABLE IF NOT EXISTS main ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'name' TEXT, 'description' TEXT, 'tg_id' TEXT, 'tags' TEXT, 'checked' BIT, 'to_1' BIT, 'to_2' BIT, 'link' TEXT , 'message_id' INTEGER)")
    base.commit()


def sql_create_users():
    global base, cur
    base = sq.connect('./cool.db')
    cur = base.cursor()
    base.execute("CREATE TABLE IF NOT EXISTS customers ('name' TEXT, 'phone' TEXT, 'tg_id' TEXT, 'email' TEXT, 'task_count' TEXT)")
    base.execute("CREATE TABLE IF NOT EXISTS performers ('name' TEXT, 'phone' TEXT, 'tg_id' TEXT, 'email' TEXT, )")
    base.commit()


def sql_start_completed():
    global base, cur
    base = sq.connect('./cool.db')
    cur = base.cursor()
    base.execute("CREATE TABLE IF NOT EXISTS completed ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'name' TEXT, 'description' TEXT, 'tg_id' TEXT, 'tags' TEXT, 'checked' BIT, 'to_1' BIT, 'to_2' BIT, 'link' TEXT, 'message_id' INTEGER)")
    base.execute("CREATE TABLE IF NOT EXISTS to_delete_pool ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'name' TEXT, 'description' TEXT, 'tg_id' TEXT, 'tags' TEXT, 'checked' BIT, 'to_1' BIT, 'to_2' BIT, 'link' TEXT, 'message_id' INTEGER)")
    base.commit()


def sql_add_command(state):
    cur.execute('INSERT INTO main ("name", "description", "tg_id", "tags", "checked", "to_1", "to_2", "link", "message_id") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (state['name'], state['description'], state['tg_id'], state['tags'], 0, 0, 0, None, None))
    base.commit()


@dp.message_handler(commands=['start', 'create_task', 'my_tasks', 'profile'])
async def create_task_start(message: types.Message):
    global msg1
    global conntt, future_task, msgs
    future_task = {}
    conntt = 0
    # msg1 = message
    if "msgs" in globals():
        for k, v in msgs.items():
            try:
                await v.delete()
            except:
                pass
    if message.text == '/start':
        await bot.send_message(message.chat.id, """Добрый день!
На связи <b>FreeX</b> бот для заказчиков, я помогу составить и выложить задачу в сервис, которым уже пользуются <b>более 3410 клиентов</b>.
Ежедневно мы подбираем <b>лучших</b> исполнителей для выполнения Ваших задач!
Скорее создавай новую задачу!""", parse_mode="HTML")
        await bot.send_message(message.chat.id, """<b>Навигация по сервису</b>

/create_task - создать задачу

/my_tasks - выложенные задачи
""", parse_mode="HTML")
    elif message.text == '/create_task':
        msg1 = await message.answer(text="Напишите заголовок задачи: (желательно, до 30 символов)")
    elif message.text == '/my_tasks':
        base = sq.connect('./cool.db')
        cur = base.cursor()
        try:
            await msg8.delete()
            if msgs:
                for y in msgs:
                    await y.delete()
            else:
                await msg7.delete()
        except:
            pass
        cur.execute("SELECT * FROM main WHERE tg_id = ?", (str(message.chat.id),))
        data = cur.fetchall()
        if data:
            msgs = {}
            for d in data:
                keke = InlineKeyboardMarkup().add(InlineKeyboardButton('Удалить ❌', callback_data=f'delete_{d[0]}')).add(
                                                        InlineKeyboardButton('Нашли исполнителя ✅', callback_data=f'done_{d[0]}'))

                msg7 = await bot.send_message(message.chat.id, f"Заголовок:<b>\n{d[1]}</b>\n\nОписание:\n{d[2]}\n\n{'Задача проверена ✔️' if d[5] == 1 else 'На стадии проверки ⌛'}", parse_mode="HTML", reply_markup=keke)
                msgs[str(d[0])] = msg7
        else:
            msg7 = await bot.send_message(message.chat.id, "У вас нет активных объявлений")
        # msg8 = await bot.send_message(message.chat.id, "Главное меню", reply_markup=inline_kb2)
    elif message.text == '/help':
        await bot.send_message(message.chat.id, """<b>Навигация по сервису</b>

/create_task - создать задачу

/my_tasks - выложенные задачи
""", parse_mode="HTML")


@dp.message_handler()
async def test(message: types.Message):
    global conntt, inline_kb1, mess, future_task
    global msg2, msg3, tagigs ,msg5, msg4
    conntt += 1
    if conntt == 1:
        global msg1
        try:
            await msg1.delete()
        except:
            pass
        msg3 = await bot.send_message(message.chat.id, f"<b>{message.text}</b>", parse_mode='HTML')
        future_task['name'] = message.text
        try:
            await message.delete()
        except:
            pass
        msg2 = await bot.send_message(message.chat.id, "Теперь напишите суть задачи:")
        return
    elif conntt == 2:
        try:
            await msg2.delete()
        except:
            pass
        inline_kb1 = InlineKeyboardMarkup()
        inline_kb1.add(InlineKeyboardButton("Разместить задачу", callback_data='push_job'))
        future_task['description'] = message.text
        msg5 = await bot.send_message(message.chat.id, f"""<b>{msg3.text}</b>\n\n{message.text}""", parse_mode='HTML', reply_markup=inline_kb1)
        try:
            await msg3.delete()
        except:
            pass
        tagigs = ''
        for tag_r, tag_name in tags_raw.items():
            if re.search(tag_r, future_task['name']+' '+message.text.lower()):
                if tagigs == '':
                    tagigs+="#"+tag_name
                else:
                    tagigs+=' #'+tag_name
        future_task['tags'] = tagigs
        return
    await bot.send_message(message.chat.id, "Чтобы создать задачу, отправьте - /create_task, узнать все команды - /help")






@dp.callback_query_handler(lambda call:call.data in tags)
async def process_callback_button1(callback_query: types.CallbackQuery):
    global msg4, msg5, tagigs, inline_kb1, message, msg6
    # print(callback_query.data)
    try:
        await msg5.delete()
    except:
        pass
    try:
        msg5=msg6
    except:
        pass
    if '#' in msg5.text:
        if "#"+callback_query.data not in msg5.text:
            kk = msg5.text.split('\n')[0]
            msg6 = await bot.send_message(msg4.chat.id, text = f"<b>{kk}</b>\n"+'\n'.join(msg5.text.split('\n')[1:])+f' #{callback_query.data}', reply_markup=inline_kb1, parse_mode='HTML')
            await msg5.delete()
        else:
            kk = msg5.text.split('\n')[0]
            msg6 = await bot.send_message(msg4.chat.id, text = f"<b>{kk}</b>\n"+'\n'.join(msg5.text.split('\n')[1:]).replace(f' #{callback_query.data}', ''), reply_markup=inline_kb1, parse_mode='HTML')
            await msg5.delete()
    else:
        kk = msg5.text.split('\n')[0]
        msg6 = await bot.send_message(msg4.chat.id, text = f"<b>{kk}</b>\n"+'\n'.join(msg5.text.split('\n')[1:])+f'\n #{callback_query.data}', reply_markup=inline_kb1, parse_mode='HTML')
        await msg5.delete()

@dp.callback_query_handler(lambda call:call.data == 'create_task')
async def create_task(callback_query: types.CallbackQuery):
    global msg1
    global conntt, future_task 
    future_task = {}
    conntt = 0
    # msg1 = message
    try:
        global msg7, msg8
        await msg8.delete()
        await msg7.delete()
    except:
        pass
    msg1 = await bot.send_message(callback_query.message.chat.id, "Напишите название задачи:")


@dp.callback_query_handler(lambda call:call.data == 'profile')
async def profile(callback_query: types.CallbackQuery):
    pass



# DONE
@dp.callback_query_handler(lambda call:call.data == 'my_tasks')
async def my_tasks(callback_query: types.CallbackQuery):
    global msg7, msg8
    global base, cur, msgs
    base = sq.connect('./cool.db')
    cur = base.cursor()
    try:
        await msg8.delete()
        if msgs:
            for y in msgs:
                await y.delete()
        else:
            await msg7.delete()
    except:
        pass
    cur.execute("SELECT * FROM main WHERE tg_id = ?", (str(callback_query.message.chat.id),))
    data = cur.fetchall()
    if data:
        msgs = {}
        for d in data:
            keke = InlineKeyboardMarkup().row(InlineKeyboardButton('❌', callback_data=f'delete_{d[0]}'),
                                                    InlineKeyboardButton('✅', callback_data=f'done_{d[0]}'))

            msg7 = await bot.send_message(callback_query.message.chat.id, f"Заголовок:<b>\n{d[1]}</b>\n\nОписание:\n{d[2]}\n\n{'Задача проверена ✔️' if d[5] == 1 else 'На стадии проверки ⌛'}", parse_mode="HTML", reply_markup=keke)
            msgs[str(d[0])] = msg7
    else:
        msg7 = await bot.send_message(callback_query.message.chat.id, "У вас нет активных объявлений")
    # msg8 = await bot.send_message(callback_query.message.chat.id, "Главное меню", reply_markup=inline_kb2)


# DONE
@dp.callback_query_handler(lambda call: 'delete_' in call.data)
async def delete_custom_message(callback_query: types.CallbackQuery):
    global msgs
    task_id = callback_query.data.replace("delete_", '')
    base = sq.connect('./cool.db')
    cur = base.cursor()
    data_to_done = cur.execute("SELECT * FROM main WHERE id = ?;", (task_id,)).fetchone()
    cur.execute('INSERT INTO to_delete_pool ("name", "description", "tg_id", "tags", "checked", "to_1", "to_2", "link", "message_id") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', data_to_done[1:])
    cur.execute("DELETE FROM main WHERE id = ?;", (task_id,))
    base.commit()
    base.close()
    await msgs.get(task_id).delete()

# DONE
@dp.callback_query_handler(lambda call: 'done_' in call.data)
async def done_custom_message(callback_query: types.CallbackQuery):
    global msgs
    task_id = callback_query.data.replace("done_", '')
    base = sq.connect('./cool.db')
    cur = base.cursor()
    data_to_done = cur.execute("SELECT * FROM main WHERE id = ?;", (task_id,)).fetchone()
    cur.execute('INSERT INTO completed ("name", "description", "tg_id", "tags", "checked", "to_1", "to_2", "link", "message_id") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', data_to_done[1:])
    cur.execute('INSERT INTO to_delete_pool ("name", "description", "tg_id", "tags", "checked", "to_1", "to_2", "link", "message_id") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', data_to_done[1:])
    cur.execute("DELETE FROM main WHERE id = ?;", (task_id,))
    base.commit()
    base.close()
    await msgs.get(task_id).delete()




@dp.callback_query_handler(lambda call:call.data == 'push_job')
async def process_callback_button_verif(callback_query: types.CallbackQuery):
    global msg5, msg7, msg8, future_task
    try:
        await msg5.delete()
    except:
        await create_offer_start()
    msg7 = await bot.send_message(callback_query.message.chat.id, "Спасибо! Ваша задача будет размещена после проверки менеджером")
    # try:
    #     await msg5.delete()
    # except:
    #     pass
    sql_start()
    future_task['tg_id'] = str(callback_query.message.chat.id)
    sql_add_command(future_task)
   
    await bot.send_message(callback_query.message.chat.id, """<b>Навигация по сервису</b>

/create_task - создать задачу

/my_tasks - выложенные задачи
""", parse_mode="HTML")

if __name__ == '__main__':
    sql_start_completed()
    executor.start_polling(dp, skip_updates=True)
