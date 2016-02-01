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
            user = User(line[first:second], line[third:fourth])
            self.users.append(user)
        
    def run(self):
        return super().run(self.config.username, self.config.password)
    
    async def event_loop(self):
        while True:
            for user in self.users:
                try:
                    await self.handle_check_for_user(user)
                except:
                    print('Could not check updates for %s' % user.userId)
            await asyncio.sleep(60)
    
    async def on_ready(self):
        win_unicode_console.enable()

        print('Connected!\n')
        print('Username: %s' % self.user.name)
        print('Bot ID: %s' % self.user.id)
        print()

        print('Command prefix is %s'% self.config.command_prefix)
        print()

        if self.servers:
            print('--Connected Servers List--')
            [print(s) for s in self.servers]
        else:
            print('No servers have been joined yet.')
        print()
        print('--Users Registered--')
        
        for user in self.users:
            print(user.userId + ' - ' + user.userUrl)
        print()
        print('--Log--')
        
        handler = getattr(self, 'event_loop', None)
        await handler()
        
    async def on_message(self, message):
        if (message.channel.is_private) and (message.author != self.user):
            await self.send_message(message.channel, self.kissAnime.downloadPage('https://kissanime.to/MyList/1084174')[:1000])
            
    async def handle_check_for_user(self, user):
        await self.send_message(user.userId, 'This is not a response!')
            
if __name__ == '__main__':
    bot = AnimeBot()
    bot.run()