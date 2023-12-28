'''
Module handled localization for telegram bot
'''
import os
import yaml
import bot_settings


with open(f'{bot_settings.LOCALIZATION_PATH}/answers.yml', 'r', encoding='utf8') as file:
    answers = yaml.safe_load(file)


def get_localization_file(command: str, language_code: str=bot_settings.DEFAULT_LOCALE) -> str:
    '''Read file with user localization or eng as default'''
    filename = f'{bot_settings.LOCALIZATION_PATH}/{command}_{language_code}.txt'
    if not os.path.isfile(filename):
        if os.path.isfile(f'{bot_settings.LOCALIZATION_PATH}/{command}_en.txt'):
            filename = f'{bot_settings.LOCALIZATION_PATH}/{command}_en.txt'

    with open(filename, 'r', encoding='utf8') as file:
        return file.read()


def check_localization_files(path: str=bot_settings.LOCALIZATION_PATH, localization: str=bot_settings.DEFAULT_LOCALE) -> None:
    '''Check localization files on path'''
    files = set()
    for file in os.listdir(path):
        if not file.endswith('.txt'):
            continue
        _file = file.split('_')[0]
        files.add(_file)

    for file in files:
        if not os.path.isfile(f'{path}/{file}_{localization}.txt'):
            raise FileNotFoundError(
                f'Not found localization file "{file}_{localization}.txt"')


def get_answer(phrase: str, localization: str=bot_settings.DEFAULT_LOCALE) -> str:
    '''Get localization text answer for command'''
    return answers.get(phrase, {localization: f'Hello, I forgot to add translate this text {phrase}'}).get(localization)


check_localization_files()
