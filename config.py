import configparser


class Config(object):
    def __init__(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)

        self.username = config.get('Credentials', 'BotUsername', fallback=None)
        self.password = config.get('Credentials', 'BotPassword', fallback=None)

        self.mal_username = config.get('Credentials', 'MalUsername', fallback=None)
        self.mal_password = config.get('Credentials', 'MalPassword', fallback=None)

        self.command_prefix = config.get('Chat', 'CommandPrefix', fallback='!!')

        if not self.username or not self.password:
            raise ValueError('A username or password was not specified in the configuration file.')
