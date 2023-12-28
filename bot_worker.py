'''
Main process telegram bot
'''
import re
from datetime import datetime, timedelta
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from sqlalchemy.orm import Session
from bot_models import db_engine, Secret, Message
import bot_settings
import bot_localization
import bot_secret


bot = Bot(token=bot_settings.TELEGRAM_API_KEY)
dispatcher = Dispatcher(bot)


@dispatcher.message_handler(commands=['start', 'help'])
async def command_service(msg: types.Message):
    '''Handle start and help commands'''
    # Get command name
    if msg.entities and msg.entities[0].type == 'bot_command':
        command = msg.text[msg.entities[0].offset+1:msg.entities[0].length]

    # Handling text by simple template
    text = bot_localization.get_localization_file(
        command, msg.from_user.language_code)
    text = replace_engine(text, msg, username=msg.from_user.username,
                          firstname=msg.from_user.first_name, lastname=msg.from_user.last_name)
    result = await msg.bot.send_message(msg.chat.id, text,
                                        parse_mode='HTML', disable_web_page_preview=True)
    await result.delete()


msg_send_regex = r'(?P<key>user|expired|service|secret):\s*(?P<val>(?:(?!user\b)(?!expired\b)(?!service\b)(?!secret\b)[\s\S])*)'


@dispatcher.message_handler(commands=['send'])
async def command_send(msg: types.Message):
    '''Send secret'''
    text = msg.text.split('/send ', 1)[1]
    matches = re.findall(msg_send_regex, text)
    if not matches:
        msg.answer('Text not matched')
        return

    user_id_to = None
    expired = datetime.now() + timedelta(hours=1)
    service = None
    secret = None
    user_id_from = msg.from_user.id

    # Check request params
    try:
        for mc in matches:
            key = mc[0].strip()
            value = mc[1].strip()
            match key:
                case 'user':
                    if value.isdigit():
                        user_id_to = int(value)
                    else:
                        raise SyntaxError(bot_localization.get_answer(
                            'cmd_send_error_user', msg.from_user.language_code))
                case 'expired':
                    time_id = value[-1]
                    time_val = value[0:-1]
                    time_remove = datetime.now()
                    if not time_val.isdigit():
                        raise SyntaxError(bot_localization.get_answer(
                            'cmd_send_error_expired', msg.from_user.language_code))

                    match time_id:
                        case 'm':
                            time_remove = time_remove + \
                                timedelta(minutes=int(time_val))
                        case 'h':
                            time_remove = time_remove + \
                                timedelta(hours=int(time_val))
                        case 'd':
                            time_remove = time_remove + \
                                timedelta(days=int(time_val))
                        case 'w':
                            time_remove = time_remove + \
                                timedelta(weeks=int(time_val))

                case 'service':
                    service = value
                case 'secret':
                    secret = value

        # Check required args
        if not service or not secret:
            raise ValueError(bot_localization.get_answer(
                'cmd_send_error_args', msg.from_user.language_code))

        secret_hash = bot_secret.generate_hash()
        with Session(autoflush=False, bind=db_engine) as session:
            user_secrets_count = session.query(Secret).filter(
                Secret.user_id_from == user_id_from).count()

            if user_secrets_count > bot_settings.USER_SECRETS_MAX:
                raise PermissionError(bot_localization.get_answer(
                    'cmd_send_error_db_count', msg.from_user.language_code))

            session.add(Secret(user_id_from=user_id_from, user_id_to=user_id_to,
                        expired=expired, service_name=service, service_secret=secret, secret_hash=secret_hash))
            session.commit()
            await msg.delete()

            try:
                # Send secret to user
                msg_text = replace_engine(bot_localization.get_answer(
                    'cmd_send_user_success', msg.from_user.language_code), secret_hash=secret_hash)
                new_msg = await bot.send_message(user_id_to, msg_text, parse_mode='HTML', disable_web_page_preview=True)
                session.add(Message(user_id_chat=user_id_to,
                            message_id=new_msg.message_id))
                session.commit()

                msg_text = replace_engine(bot_localization.get_answer(
                    'cmd_send_user_delivered', msg.from_user.language_code), secret_hash=secret_hash)
                new_msg = await bot.send_message(user_id_from, msg_text, disable_web_page_preview=True)
                session.add(Message(user_id_chat=user_id_to,
                            message_id=new_msg.message_id))
                session.commit()

            except Exception:
                # Send hash to this chat
                msg_text = replace_engine(bot_localization.get_answer(
                    'cmd_send_user_unreach', msg.from_user.language_code), secret_hash=secret_hash)
                new_msg = await bot.send_message(user_id_from, msg_text, parse_mode='HTML', disable_web_page_preview=True)
                session.add(Message(user_id_chat=user_id_from,
                            message_id=new_msg.message_id))
                session.commit()

    except Exception as ex:
        msg.answer(str(ex), parse_mode='HTML')


msg_hash_regex = r'/get\s*(?P<hash>\S+)'


@dispatcher.message_handler(commands=['get'])
async def command_get(msg: types.Message):
    mc = re.search(msg_hash_regex, msg.text)
    if not mc:
        msg_text = replace_engine(bot_localization.get_answer(
            'cmd_get_hash_incorrect', msg.from_user.language_code))
        msg.answer(msg_text, parse_mode='HTML')
        return

    secret_hash = mc.group('hash')
    with Session(autoflush=False, bind=db_engine) as session:
        secret = session.query(Secret).filter(
            Secret.secret_hash == secret_hash).first()
        if not secret:
            msg_text = replace_engine(bot_localization.get_answer(
                'cmd_get_hash_not_found', msg.from_user.language_code))
            await msg.answer(msg_text, parse_mode='HTML')
        else:
            msg_text = replace_engine(bot_localization.get_answer(
                'cmd_get_hash_correct', msg.from_user.language_code), service=secret.service_name, secret=secret.service_secret)
            await msg.answer(msg_text, parse_mode='HTML')
            session.delete(secret)
            session.commit()


def replace_engine(text: str, **replaces) -> str:
    '''Method is engine for basic template.
    Using replace_engine('one %template_var_1%', template_var_1='is 1')
    '''
    for key, val in replaces.items():
        text = text.replace(f'%{key}%', val)

    # escapes = ['(',')','.','-', '#']
    # for escape in escapes:
    #     text = text.replace(escape, '\\'+escape)

    return text


if __name__ == '__main__':
    executor.start_polling(dispatcher)
