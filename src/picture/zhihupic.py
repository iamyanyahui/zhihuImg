#-*-coding:utf-8-*-
"""
    Created on 2016/8/31
    
    @author:闫亚辉
"""

from .common import *
import requests
import json
from urllib import request
from picture.answerPic import AnswerPic


class Picture:
    def __init__(self,cookies=None):
        self._session = requests.Session()
        self._session.headers.update(Default_Header)
        if cookies is not None:
            self.login_with_cookies(cookies)
        else:
            self.login()
   
    def login_with_cookies(self,cookies):
        if os.path.isfile(cookies):
            with open(cookies) as f:
                cookies = f.read()
        cookies_str = json.loads(cookies)
        self._session.cookies.update(cookies_str)
        
    def login(self):
        email = input('请输入邮箱地址：')
        password = input('请输入密码：')
        data = {'email':email,'password':password,'remember_me':'true'}
        self._session.post(Login_URL, data=data)
        cookies_str = json.dumps(self._session.cookies.get_dict())
        self.create_cookies_file(cookies_str,'cookies.txt')
        
    def create_cookies_file(self,cookies,filename):
        if cookies:
            with open(filename,'wb') as f:
                f.write(cookies.encode())
            print('cookies已保存。。。')
        else:
            print('保存cookies时出错。。。')
    
    def get_answerPics(self):
        question_id = input('请输入问题的id：')
        goalURL = Question_URL + '/' + str(question_id)
        r = self._session.get(goalURL)
        soup = BeautifulSoup(r.content)
        pagesize = 10
        xsrf = soup.find('input',attrs={'name':'_xsrf'})['value']
        data = {'_xsrf': xsrf,
                'method': 'next',
                'params': ''}
        params = {'url_token': question_id,
                  'pagesize': pagesize,
                  'offset': 0}
        new_headers = dict(Default_Header)
        new_headers['Referer'] = goalURL
        
        for i in range(0, (self.get_answer_num(soup) - 1) // pagesize + 1):
            if i == 0:
                 # 修正各种建议修改的回答……
                error_answers = soup.find_all('div',id='answer-status')
                for each in error_answers:
                    each['class'] = 'zm-editable-content'
                    
                answers_wrap = soup.find('div',id='zh-question-answer-wrap')
                authors = answers_wrap.find_all(
                        'div', class_='zm-item-answer-author-info')
                contents = answers_wrap.find_all('div', class_='zm-editable-content')
                assert len(authors)==len(contents)
                
                for author,content in zip(authors,contents):
                    author_name_itme = author.find('a',class_='author-link')
                    if author_name_itme is None:
                        author_name = '知乎用户'
                    else:
                        author_name = author_name_itme.string
                    
                    pic_urls = []
                    for img in content.find_all('img',class_="origin_image zh-lightbox-thumb"):
                        pic_urls.append(img['src'])
                        
                    yield AnswerPic(author_name,pic_urls)
            else:
                params['offset'] = i*pagesize
                data['params'] = json.dumps(params)
                r = self._session.post(Question_Get_More_Answer_URL, data=data, headers=new_headers)
                answer_list = r.json()['msg']
                for answer_html in answer_list:
                    yield self._parse_html(answer_html)
    
    def _parse_html(self,html):
        soup = BeautifulSoup(html)
        
        error_answers = soup.find_all('div', id='answer-status')
        for each in error_answers:
            each['class'] = 'zm-editable-content'
        
        author = soup.find('div', class_='zm-item-answer-author-info')
        author_name_itme = author.find('a',class_='author-link')
        if author_name_itme:
            author_name = author_name_itme.string
        else:
            author_name = '知乎用户'
        content = soup.find('div', class_='zm-editable-content')
        pic_urls = []
        for img in content.find_all('img',class_="origin_image zh-lightbox-thumb"):
            pic_urls.append(img['src'])
            
        return AnswerPic(author_name,pic_urls)
    
    def get_answer_num(self,soup):
        answer_num_block = soup.find('h3', id='zh-question-answer-num')
        if answer_num_block is None:
            if soup.find('span', class_='count') is not None:
                return 1
            else:
                return 0
        return int(answer_num_block['data-num'])
    
    def save_pics_with_author(self,path):
        if not os.path.exists(path):
            os.makedirs(path)
        for answerPic in self.get_answerPics():
            self._savePics(path,answerPic) 
        print('恭喜！图片已保存完毕！共有图片%d张。。。' % len(os.listdir(path)))       
     
    def _savePics(self,path, answerPic):
        num = 1
        filename = answerPic.author_name
        catalog = path + '/' + filename
        if not os.path.exists(catalog):
            os.makedirs(catalog)
        elif re.match(r'^知乎用户$',filename):
            num = len(os.listdir(catalog)) + 1

        urls = answerPic.pic_urls
        
        self._save_pics(catalog, urls, num)
            
    def save_pics_ignore_author(self,path):
        if not os.path.exists(path):
            os.makedirs(path)
        num = 1
        for answerPic in self.get_answerPics():
            urls = answerPic.pic_urls
            num = self._save_pics(path, urls,num)
        print('恭喜！图片已保存完毕！共有图片%d张。。。' % len(os.listdir(path)))
            
    def _save_pics(self,path,urls,num):   
        for url in urls:
            print('正在保存图片：',url)
            splitPath = url.split('.')
            fTail = splitPath.pop()
            if len(fTail)>3:
                fTail = 'jpg' 
            filename = path + '/' + str(num) +'.' + fTail
            if not os.path.isfile(filename):
                request.urlretrieve(url,filename)
            num += 1
            print('已保存图片：',url)
        return num    
 
def test():
    p = Picture()
    path = input('请输入保存图片的路径名：')
    #p.save_pics_with_author(path)        
    p.save_pics_ignore_author(path)


if __name__=='__main__':
    test()

