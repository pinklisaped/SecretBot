import os
import bot_settings
import bot_localization
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor


bot = Bot(token=bot_settings.TOKEN)
dispatcher = Dispatcher(bot)


@dispatcher.message_handler(commands=['start', 'help'])
async def send_welcome(msg: types.Message):
    '''Handle start and help commands'''
    # Get command name
    if msg.entities and msg.entities[0].type == 'bot_command':
        command = msg.text[msg.entities[0].offset+1:msg.entities[0].length]
    
    # Handling text by simple template
    text = bot_localization.get_localization_file(command, msg.from_user.language_code)
    text = replace_engine(text, msg)
    await msg.bot.send_message(msg.chat.id, text, 
            parse_mode='HTML', disable_web_page_preview=True)


@dispatcher.message_handler(commands=['send'])
async def send_welcome(msg: types.Message):
    pass



def replace_engine(text: str, msg: types.Message):
    replaces = {
        '%username%':  str(msg.from_user.username or ''),
        '%firstname%': str(msg.from_user.first_name or ''),
        '%lastname%': str(msg.from_user.last_name or '')
    }

    for alias, field in replaces.items():
        text = text.replace(alias, field)
    
    # escapes = ['(',')','.','-', '#']
    # for escape in escapes:
    #     text = text.replace(escape, '\\'+escape)

    return text


if __name__ == '__main__':
    executor.start_polling(dispatcher)
