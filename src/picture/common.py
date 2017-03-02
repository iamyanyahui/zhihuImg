#-*-coding:utf-8-*-
"""
    Created on 2016/8/31
    
    @author:闫亚辉
"""

import re
import os
from bs4 import BeautifulSoup as _Bs

try:
    __import__('lxml')
    BeautifulSoup = lambda makeup: _Bs(makeup, 'lxml')
except ImportError:
    BeautifulSoup = lambda makeup: _Bs(makeup, 'html.parser')
Default_Header = {'X-Requested-With': 'XMLHttpRequest',
                  'Referer': 'http://www.zhihu.com',
                  'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; '
                                'rv:39.0) Gecko/20100101 Firefox/39.0',
                  'Host': 'www.zhihu.com'}

Zhihu_URL = 'https://www.zhihu.com'
Login_URL = Zhihu_URL + '/login/email'
Captcha_URL = Zhihu_URL + '/captcha.gif'
Question_URL = Zhihu_URL + '/question'
Question_Get_More_Answer_URL = Zhihu_URL + '/node/QuestionAnswerListV2'


re_question_url = re.compile(
    r'^https?://www\.zhihu\.com/question/\d+(\?sort=created|/?)$')
re_question_url_std = re.compile(r'^https?://www\.zhihu\.com/question/\d+/?')
re_ans_url = re.compile(
    r'^https?://www\.zhihu\.com/question/\d+/answer/\d+/?$')