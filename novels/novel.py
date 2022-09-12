# -*- coding: utf-8 -*-
"""
Created on Fri May 29 00:38:13 2020
@author: ASUS
"""

# 導入 模組(module)
import requests
# 導入 BeautifulSoup 模組(module)：解析HTML 語法工具
import bs4


def ptt(link, index):
    # 文章連結
    # TODO 一堆連結
    URL = link
    # 設定Header與Cookie
    my_headers = {'cookie': 'over18=1;'}
    # 發送get 請求
    response = requests.get(URL, headers=my_headers)

    #  把網頁程式碼(HTML) 丟入 bs4模組分析
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    ## PTT 上方4個欄位
    header = soup.find_all('span', 'article-meta-value')

    # 作者
    author = header[0].text
    # 看版
    board = header[1].text
    # 標題
    title = header[2].text
    # 日期
    date = header[3].text

    ## 查找所有html 元素 抓出內容
    main_container = soup.find(id='main-container')
    # 把所有文字都抓出來
    all_text = main_container.text
    # 把整個內容切割透過 "-- " 切割成2個陣列
    pre_text = all_text.split('--')[0]

    # 把每段文字 根據 '\n' 切開
    texts = pre_text.split('\n')
    # 如果你爬多篇你會發現
    contents = texts[2:]
    while '' in contents:
        contents.remove('')
    # i = 0
    # while i < len(contents) - 2:
    #     if contents[i + 1] == '':
    #         if contents[i + 2] != '':
    #             del (contents[i + 1])
    #     else:
    #         i += 1
    # i = 0
    # while i < len(contents) - 2:
    #     if contents[i] == '':
    #         if contents[i + 1] == '':
    #             del (contents[i + 1])
    #         else:
    #             i += 1
    #     else:
    #         i += 1
    print(contents)
    content = '\n'.join(contents)
    # print(content)
    # 顯示
    # print('作者：'+author)
    # print('看板：'+board)
    # print('標題：'+title)
    # print('日期：'+date)

    # TODO 存成.txt
    # print('內容：' + content)

    path = './tmp_/' + str(index + 554) + '.txt'
    f = open(path, 'a', encoding='utf16')
    f.write(content)
    f.close()


ptt('https://www.ptt.cc/bbs/C_Chat/M.1569845220.A.C55.html', 0)
