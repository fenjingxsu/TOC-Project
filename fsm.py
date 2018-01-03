from transitions.extensions import GraphMachine
import bs4
from bs4 import BeautifulSoup
import requests

PTT_URL='https://www.ptt.cc'

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(
            model = self,
            **machine_configs
        )
        self.URLtmp1=''
        self.URLtmp2='.html'
        self.getPage='0'
        self.links=[]

    def search_to_articles(self, update):
        text = update.message.text
        return text!='\0' #no use

    def read_article(self, update):
        text = update.message.text
        return text.isdigit()
    def goto_lastPage(self, update):
        text = update.message.text
        return text.lower() == 'last'

    def on_enter_articles(self, update):
        self.pagestatus=0
        text = update.message.text
        self.boardtemp=text
        result = requests.get('https://www.ptt.cc/bbs/'+self.boardtemp+'/index.html')
        #update.message.reply_text(('https://www.ptt.cc/bbs/'+self.boardtemp+'/index.html'))
        self.URLtmp1 = 'https://www.ptt.cc/bbs/'+self.boardtemp+'/index'
        soup = BeautifulSoup(result.content, 'html.parser')
        i=1
        popularity=soup.select(".nrec")
        title=soup.select(".title")
        for a, b in zip(popularity, title) :
            tmp=str(i)+'\t'+a.text+b.text
            update.message.reply_text(tmp)
            i+=1
        update.message.reply_text("上一頁： 輸入last; 返回重選：exit; 選擇文章：輸入編號")
  
        geturl1=soup.find_all('a', 'btn', 'wide')
        geturl2=geturl1[3]['href']
        urlsplitpart=geturl2.split('x')
        urlpart2=urlsplitpart[1].split('.')
        self.getPage=urlpart2[0]

        findLinks=soup.find_all('div', 'title')
        for d in findLinks:
            if d.find('a'):
                self.links.append(d.find('a')['href'])
            else:
                self.links.append("")
       # update.message.reply_text("555")
       # update.message.reply_text(urlresult)
       # self.go_back(update)

    def on_enter_lastPage(self, update):
        self.pagestatus=1
        last_result = requests.get(self.URLtmp1+self.getPage+self.URLtmp2)
        soup = BeautifulSoup(last_result.content, 'html.parser')
        geturl1=soup.find_all('a', 'btn', 'wide')
        geturl2=geturl1[3]['href']
        urlsplitpart=geturl2.split('x')
        urlpart2=urlsplitpart[1].split('.')
        self.getPage=urlpart2[0]
        i=1
        popularity=soup.select(".nrec")
        title=soup.select(".title")
        for a, b in zip(popularity, title) :
            tmp=str(i)+'\t'+a.text+b.text
            update.message.reply_text(tmp)
            i+=1
        update.message.reply_text("上一頁： 輸入last; 選擇文章：輸入編號")

        findLinks=soup.find_all('div', 'title')
        for d in findLinks:
            if d.find('a'):
                self.links.append(d.find('a')['href'])
            else:
                self.links.append("")

    def on_enter_chooseArticle(self, update):
        text=update.message.text
        text=int(text)
        #update.message.reply_text(text)
        read = requests.get(PTT_URL + self.links[text-1])
        read_Find= BeautifulSoup(read.content, 'html.parser')
        article=read_Find.find('div', id='main-container')
        #print(PTT_URL + self.links[text-1])
        update.message.reply_text(article.text)

    def rechoose(self, update):
        return update.message.text.lower()=='exit'

    def backto_search(self, update):
        return True
            
