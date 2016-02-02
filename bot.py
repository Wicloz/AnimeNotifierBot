import asyncio
import pip
import pickle
import os.path
try:
    import discord
except:
    pip.main(['install', 'git+https://github.com/Rapptz/discord.py@async#egg=discord.py'])
try:
    import win_unicode_console
except:
    0

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
        self.id = userId
        self.kissUrl = userUrl
        self.malUrl = ''

class AnimeBot(discord.Client):
    def __init__(self, config_file='config/options.txt', user_file='config/users.txt'):
        super().__init__()
        self.config = Config(config_file)
        self.kissAnime = KissDownloader()
        self.users = []
        if os.path.isfile(user_file):
            with open(user_file, 'rb') as file:
                self.users = pickle.load(file)

    def run(self):
        return super().run(self.config.username, self.config.password)
    
    async def event_loop(self):
        await asyncio.sleep(1)
        while True:
            for user in self.users:
                try:
                    await self.handle_check_for_user(user)
                except Exception as e:
                    print(e)
                    print('Could not check updates for %s' % user.id)
            await asyncio.sleep(300)
    
    async def on_ready(self):
        try:
            win_unicode_console.enable()
        except:
            0

        print('Connected!\n')
        print('Username: %s' % self.user.name)
        print('Bot ID: %s' % self.user.id)
        print()

        print('Command prefix is %s'% self.config.command_prefix)
        print()

        print('--Connected Servers List--')
        if self.servers:
            [print(s) for s in self.servers]
        else:
            print('No servers have been joined yet.')
        print()
        
        print('--Users Registered--')
        if len(self.users) > 0:
            for user in self.users:
                print(user.id + ' - ' + user.kissUrl)
        else:
            print('No users have registered yet.')
        print()
        
        print('--Log--')
        handler = getattr(self, 'event_loop', None)
        await handler()
        
    async def on_message(self, message):
        if (message.channel.is_private) and (message.author != self.user) and (message.content.startswith(self.config.command_prefix + 'register')):
            data = message.content[message.content.find(' '):].replace(' ', '')
            if data.startswith('https://kissanime.to/MyList/'):
                self.register_user(message.author.id, data)
            elif data.isdigit():
                self.register_user(message.author.id, 'https://kissanime.to/MyList/' + data)
        else:
            page = self.kissAnime.downloadPage(message.content).replace('\\r\\n', '')
            print(self.kiss_latest_episode(page))
            
    def register_user(self, userId, userUrl):
        if self.get_user(userId) == 0:
            user = User(userId, userUrl)
            self.users.append(user)
            print('Added user \'%s\' with url \'%s\'' % (userId, userUrl))
        else:
            self.get_user(userId).userUrl = userUrl
            print('Upadated bookmark url for user \'%s\'' % userId)
        
        with open('config/users.txt', 'wb') as file:
            pickle.dump(self.users, file)
    
    def get_user(self, userId):
        for user in self.users:
            if user.id == userId:
                return user
        return 0
    
    async def handle_check_for_user(self, user):
        print('Checking bookmarks for \'%s\'...' % user.id)
        cachedFilePath = 'cache/%s.dat' % user.id
        kissDomain = 'https://kissanime.to'
        colonId = '(*:*)'
        
        # Download the users bookmark page
        if os.path.isfile('bookmarkpage.html'):
            with open('bookmarkpage.html', 'r') as file:
                bookmarkPage = file.read()
        else:
            bookmarkPage = self.kissAnime.downloadPage(user.kissUrl).replace('\\r\\n', '')
        #with open('bookmarkpage.html', 'w') as file:
        #    file.write(bookmarkPage)
        
        # Turn the page into a list
        newList = self.kiss_list_from_bookmarks(bookmarkPage)
        
        # Load the old list from the file
        oldList = {}
        if os.path.isfile(cachedFilePath):
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
        
        print('Done checking bookmarks for \'%s\'!' % user.id)

    def kiss_list_from_bookmarks(self, content):
        dataList = {}
        table = content[content.find('<table class="listing">'):content.find('</table>')]
        table = table[table.find('<tr class="trAnime'):table.find('</tbody>')]
        rows = table.split('</tr>')
        del rows[-1]

        for row in rows:
            row += '</tr>'
            soup = BeautifulSoup(row, 'html.parser')
            key = soup.find_all('a')[1].string.strip()
            episode = soup.find_all('a')[2].string.replace('Episode', '').strip()
            link = soup.find_all('a')[1].get('href')
            dataList[key] = (episode, link)

        return dataList

    def kiss_latest_episode(self, content):
        bowl = BeautifulSoup(content, 'html.parser').table
        soup = BeautifulSoup(str(bowl), 'html.parser')
        episode = soup.find_all('a')[0].string[-3:]
        return episode

if __name__ == '__main__':
    bot = AnimeBot()
    bot.run()

