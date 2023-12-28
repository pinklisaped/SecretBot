import os
import bot_settings


def get_localization_file(command, language_code=bot_settings.LANG):
    '''Read file with user localization or eng as default'''
    filename = f'{bot_settings.LOCAL_PATH}/{command}_{language_code}.txt'
    if not os.path.isfile(filename):
        if os.path.isfile(f'{bot_settings.LOCAL_PATH}/{command}_en.txt'):
            filename = f'{bot_settings.LOCAL_PATH}/{command}_en.txt'

    with open(filename, 'r') as file:
        return file.read()


def check_localization_files(path=bot_settings.LOCAL_PATH, localization=bot_settings.LANG):
    files = set()
    for file in os.listdir(path):
        _file = file.split('_')[0]
        files.add(_file)
    
    for file in files:
        if not os.path.isfile(f'{path}/{file}_{localization}.txt'):
            raise FileNotFoundError(f'Not found localization file "{file}_{localization}.txt"')
    pass


check_localization_files()
