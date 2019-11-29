from flask import Flask, render_template, request
import requests
import sys
import re
from urllib.request import quote


class crawler:
    url = ''
    urls = []
    o_urls = []
    html = ''
    total_pages = 5
    current_page = 0
    next_page_url = ''
    timeout = 60
    headersParameters = {
        'Connection': 'Keep-Alive',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'Mozilla/6.1 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
    }

    def __init__(self,keyword):
        self.url = 'https://www.baidu.com/baidu?wd='+quote(keyword)+'&tn=monline_dg&ie=utf-8'

    def set_timeoput(self, time):
        try:
            self.timeout = int(time)
        except:
            pass

    def set_total_pages(self, num):
        try:
            self.total_pages = int(num)
        except:
            pass

    def set_current_url(self, url):
        self.url = url

    def switch_url(self):
        if self.next_page_url == '':
            sys.exit()
        else:
            self.set_current_url(self.next_page_url)

    def is_finish(self):
        if self.current_page >= self.total_pages:
            return True
        else:
            return False

    def get_html(self):
        r = requests.get(self.url, timeout=self.timeout, headers=self.headersParameters)
        if r.status_code == 200:
            self.html = r.text
            print ("[Current URL]: ",self.url)
            self.current_page += 1
        else:
            self.html = ''
            print('[ERROR]', self.url,'Http Return Code is Not 200!')

    def get_urls(self):
        o_urls = re.findall('href\=\"(http\:\/\/www\.baidu\.com\/link\?url\=.*?)\" class\=\"c\-showurl\"', self.html)
        o_urls = list(set(o_urls))
        self.o_urls = o_urls
        next = re.findall(' href\=\"(\/s\?wd\=[\w\d\%\&\=\_\-]*?)\" class\=\"n\"', self.html)
        if len(next) > 0:
            self.next_page_url = 'https://www.baidu.com'+next[-1]
        else:
            self.next_page_url = ''

    def get_real(self, o_url):
        r = requests.get(o_url, allow_redirects=False)
        if r.status_code == 302:
            try:
                return r.headers['location']
            except:
                pass
        return o_url

    def transformation(self):
        self.urls = []
        for o_url in self.o_urls:
            self.urls.append(self.get_real(o_url))

    def run(self):
        while(not self.is_finish()):
            self.get_html()
            self.get_urls()
            self.transformation()
            self.switch_url()
        return self.urls

app = Flask(__name__)
@app.route('/')
def index():
    key = request.args.get('query',None)
    if key:
        c = crawler(key)
        c.set_timeoput(10)
        c.set_total_pages(11)
        results = c.run()
        return render_template('results.html', query=key, results=results)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)