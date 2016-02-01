import asyncio
import discord
import win_unicode_console

from config import Config
from kissanimeConnector import KissDownloader

class User(object):
    def __init__(self, userId, userUrl):
        self.userId = userId
        self.userUrl = userUrl

class AnimeBot(discord.Client):
    def __init__(self, config_file='config/options.txt'):
        super().__init__()
        self.config = Config(config_file)
        self.kissAnime = KissDownloader()
        self.users = []
        for line in open('config/users.txt', 'r'):
            equalPos = line.find('=')
            first = line.find('\'', 0, equalPos) + 1
            second = line.find('\'', first, equalPos)
            third = line.find('\'', equalPos) + 1
            fourth = line.find('\'', third)
            self.users.append(User(line[first:second], line[third:fourth]))
        
    def run(self):
        return super().run(self.config.username, self.config.password)
        
    async def on_ready(self):
        win_unicode_console.enable()

        print('Connected!\n')
        print('Username: %s' % self.user.name)
        print('Bot ID: %s' % self.user.id)
        print()

        print("Command prefix is %s" % self.config.command_prefix)
        print()

        if self.servers:
            print('--Connected Servers List--')
            [print(s) for s in self.servers]
        else:
            print("No servers have been joined yet.")
        print()
        print("--Users Registered--")
        
        for user in self.users:
            print(user.userId + ' - ' + user.userUrl)
        print()
        print("--Log--")
        
        handler = getattr(self, 'check_for_user', None)
        await handler(self.users[0])
        
    async def on_message(self, message):
        if (message.channel.is_private) and (message.author != self.user):
            await self.send_message(message.channel, 'This is a response!')
            await self.send_message(message.channel, self.kissAnime.downloadPage('https://kissanime.to/MyList/1084174')[:100])
            
    async def check_for_user(self, user):
        await self.send_message(user.userId, 'This is not a response!')
            
if __name__ == '__main__':
    bot = AnimeBot()
    bot.run()