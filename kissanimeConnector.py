import pip

try:
    from pyquery import PyQuery
except ImportError:
    pip.main(['install', 'pyquery'])

class KissDownloader():
    def downloadPage(self, url):
        return PyQuery(url)