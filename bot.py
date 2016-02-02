import asyncio
import discord
import win_unicode_console
import pip

try:
    from lxml import html
except ImportError:
    pip.main(['install', 'lxml'])
    
try:
    from bs4 import BeautifulSoup
except ImportError:
    pip.main(['install', 'BeautifulSoup4'])

from config import Config
from kissanimeConnector import KissDownloader

class User(object):
    def __init__(self, userId, userUrl):
        self.discordUser = discord.User()
        self.discordUser.id = userId
        self.userId = userId
        self.userUrl = userUrl

class AnimeBot(discord.Client):
    def __init__(self, config_file='config/options.txt'):
        super().__init__()
        self.config = Config(config_file)
        self.kissAnime = KissDownloader()
        self.users = []
        for line in open('config/users.txt', 'r'):
            equalPos = line.find('-')
            first = line.find('\'', 0, equalPos) + 1
            second = line.find('\'', first, equalPos)
            third = line.find('\'', equalPos) + 1
            fourth = line.find('\'', third)
            user = User(line[first:second], line[third:fourth])
            self.users.append(user)
        
    def run(self):
        return super().run(self.config.username, self.config.password)
    
    async def event_loop(self):
        await asyncio.sleep(1)
        while True:
            for user in self.users:
                await self.handle_check_for_user(user)
                #try:
                #    await self.handle_check_for_user(user)
                #except:
                #    print('Could not check updates for %s' % user.userId)
            await asyncio.sleep(300)
    
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
        if (message.channel.is_private) and (message.author != self.user) and (message.content.startswith(self.config.command_prefix + 'register')):
            url = message.content[message.content.find(' '):].replace(' ', '')
            if url.startswith('https://kissanime.to/MyList/'):
                self.register_user(message.author.id, url)
            
    def register_user(self, userId, userUrl):
        if self.get_user(userId) == 0:
            user = User(userId, userUrl)
            self.users.append(user)
            print('Added user \'%s\' with url \'%s\'' % (userId, userUrl))
        else:
            self.get_user(userId).userUrl = userUrl
            print('Upadated bookmark url for user \'%s\'' % userId)
        
        with open('config/users.txt', 'w') as file:
            for user in self.users:
                file.write('\'%s\' - \'%s\',\n' % (user.userId, user.userUrl))
    
    def get_user(self, userId):
        for user in self.users:
            if user.userId == userId:
                return user
        return 0
    
    async def handle_check_for_user(self, user):
        print('Checking bookmarks for \'%s\'...' % user.userId)
        cachedFilePath = 'cache/%s.dat' % user.userId
        kissDomain = 'https://kissanime.to'
        colonId = '(*:*)'
        
        # Download the users bookmark page
        bookmarkPage = self.kissAnime.downloadPage(user.userUrl).replace('\\r\\n', '')
        #with open('bookmarkpage.html', 'r') as file:
        #    bookmarkPage = file.read()
        
        # Turn the page into an list
        newList = {}
        table = bookmarkPage[bookmarkPage.find('<table class="listing">'):bookmarkPage.find('</table>')]
        table = table[table.find('<tr class="trAnime'):table.find('</tbody>')]
        rows = table.split('</tr>')
        del rows[-1]

        for row in rows:
            row = row + '</tr>'
            soup = BeautifulSoup(row, 'html.parser')
            key = soup.find_all('a')[1].string.strip()
            episode = soup.find_all('a')[2].string.replace('Episode', '').strip()
            link = soup.find_all('a')[1].get('href')
            newList[key] = (episode, link)
        
        # Load the old list from the file
        oldList = {}
        for line in open(cachedFilePath, 'r'):
            try:
                key, value = line.strip().split(': ')
                key = key.replace(colonId, ':')
                oldList[key] = tuple(value.replace('\'', '').replace('(', '').replace(')', '').split(', '))
            except:
                0 #best code evah
        
        # Compare the lists and send messages
        for key, newValue in newList.items():
            try:
                oldValue = oldList[key]
            except:
                oldValue = ('000', '')
                
            if oldValue[0] != newValue[0]:
                await self.send_message(user.discordUser, 'The anime **%s** has just aired episode %s!\n%s' % (key, newValue[0], kissDomain + newValue[1]))
        
        # Save the new list into the file
        with open(cachedFilePath, 'w') as file:
            for key, value in newList.items():
                file.write('%s: %s\n' % (key.replace(':', colonId), value))
        
        print('Done checking bookmarks for \'%s\'!' % user.userId)

if __name__ == '__main__':
    bot = AnimeBot()
    bot.run()