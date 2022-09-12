from bs4 import BeautifulSoup
import requests
import datetime
import json

my_headers = {'cookie': 'over18=1;'}
response = requests.get(
    "https://www.ptt.cc/bbs/Headphone/M.1530392323.A.695.html",
    headers=my_headers)
response.encoding = "utf-8"
soup = BeautifulSoup(response.text, "lxml")
push_content = soup.find_all("span", class_="push-content")
push_ipdatetime = soup.find_all("span", class_="push-ipdatetime")

file = ".txt"
sell = './sell' + file
collect = './collect' + file
f_sell = open(sell, 'a', encoding='utf-8')
f_collect = open(collect, 'a', encoding='utf-8')

count_sell = 0
count_collect = 0

last_update_sell = datetime.datetime.today()
last_update_collect = datetime.datetime.today()


def AppeendToJson(json, item, count, datetime, last_update):
    last_update = datetime
    count += 1
    try:
        tmp = {
            "id": count,
            "location": item[1],
            "condition": item[2],
            "name": item[3],
            "price": item[4],
            "others": item[5] if len(item) == 6 else "",
            "datetime": datetime
        }
        json.append(tmp)
    except:
        print(item)


data_sell = []
data_collect = []
for i in range(len(push_content)):
    item = push_content[i].text.replace(": ", "").split("_")
    intput_date = push_ipdatetime[i].text.replace("\n", "_").replace(
        ":", "_").replace("/", "_").replace(" ", "_").split("_")
    date = datetime.datetime(year=datetime.date.today().year,
                             month=int(intput_date[1]),
                             day=int(intput_date[2]),
                             hour=int(intput_date[3]),
                             minute=int(intput_date[4]))
    if (item[0] == "賣" or item[0] == "售"):
        AppeendToJson(data_sell, item, count_sell, date, last_update_sell)
        # last_update_sell = date
        # count_sell += 1
        # f_sell.write(str(count_sell) + ", ")
        # for j in item:
        #     if (j != "賣" or j != "售"):
        #         f_sell.write(j + ", ")
        # f_sell.write(str(date))
        # f_sell.write("\n")
    elif (item[0] == "徵"):
        AppeendToJson(data_collect, item, count_collect, date,
                      last_update_collect)
        # last_update_collect = date
        # count_collect += 1
        # f_collect.write(str(count_collect) + ", ")
        # for j in item:
        #     if (j != "徵"):
        #         f_collect.write(j + ", ")
        # f_collect.write(str(date))
        # f_collect.write("\n")

f_sell.write(data_sell)
f_collect.write(data_collect)
f_sell.close()
f_collect.close()
