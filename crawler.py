from bs4 import BeautifulSoup
import requests
import datetime
import json
import copy
from fake_useragent import UserAgent
import random
import time

isPrintError = False


def DoSomeDelay():
    delay_choices = [1, 3, 5, 14, 25, 40]
    delay = random.choice(delay_choices)
    print(f"delay for {delay} seconds")
    time.sleep(delay)


def CrawlerFindAll(url, dom, class_list):
    user_agent = UserAgent()
    my_headers = {
        "cookie":
        "over18=1",
        "content-type":
        "text/html; charset=UTF-8",
        "user-agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"
    }
    response = requests.get(url, headers=my_headers)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "lxml")
    # print(soup.prettify())

    result_list = []
    for i in class_list:
        result_list.append(soup.find_all(dom, i))
    return result_list


def GetTitleData(url, old_data):
    print("Getting title data...")
    class_ = ["title", "author", "date"]
    title, author, date = CrawlerFindAll(url, "div", class_)
    print("Done")

    dict_data = {}
    new_data = []

    print("Go through data...")
    for index in range(len(title)):
        try:
            title_string = title[index].find('a').string
            title_href = title[index].find('a')['href']
            if '[交易]' in title_string or '贈送' in title_string:
                try:
                    if '[交易]' in title_string:
                        title_index = title_string.index('[交易]') + 4
                        _title = title_string[title_index:].strip()
                    else:
                        _title = title_string.strip()
                except:
                    pass
                try:
                    input_date = date[index].string.strip().split('/')
                    _title_date = datetime.datetime(
                        year=datetime.date.today().year,
                        month=int(input_date[0]),
                        day=int(input_date[1]))
                    title_date = _title_date.strftime('%Y-%m-%d')
                except:
                    print(f"date: {date} error")
                try:
                    _id = title_href.strip().split('/')[-1].replace(
                        '.html', '')
                    if not old_data.get(_id):
                        new_data.append(_id)
                        dict_data[_id] = {
                            "title": _title,
                            "url": "https://www.ptt.cc" + title_href,
                            "used_id": author[index].string,
                            "date": title_date,
                            "origin": title_string
                        }
                except:
                    print(f"id: {_id} error")
        except:
            pass

    print("Done")
    return dict_data, new_data


def GetPushData(url):
    print("Getting push data...")
    class_ = ["push-content", "push-ipdatetime", "push-userid"]
    push_content, push_ipdatetime, push_userid = CrawlerFindAll(
        url, "span", class_)
    print("Done")

    count_data = 0
    last_update_datetime = datetime.datetime.today()
    dict_data = {}
    dict_data["LAST_UPDATED_ID"] = 0
    dict_data["LAST_UPDATED_DATETIME"] = last_update_datetime

    print("Go through data...")
    for i in range(len(push_content)):
        _item = push_content[i].text.replace(": ", "").strip()
        input_date = push_ipdatetime[i].text.replace("\n", "_").replace(
            ":", "_").replace("/", "_").replace(" ", "_").split("_")
        push_datetime = datetime.datetime(year=datetime.date.today().year,
                                          month=int(input_date[1]),
                                          day=int(input_date[2]),
                                          hour=int(input_date[3]),
                                          minute=int(input_date[4]))
        last_update_datetime = push_datetime

        if (_item[0] in ("賣", "售", "徵", "買")):
            count_data += 1
            dict_data[str(count_data)] = {
                "sell_or_collect": "",
                "location": "",
                "condition": "",
                "name": "",
                "price": "",
                "others": "",
                "used_id": push_userid[i].text.replace(": ", "").strip(),
                "datetime": push_datetime.strftime('%Y-%m-%d %H:%M'),
                "origin": _item
            }
        else:
            _s = push_content[i].text.replace(": ", "").strip()
            dict_data[str(count_data)]["origin"] += _s
    dict_data["LAST_UPDATED_ID"] = str(count_data)
    dict_data["LAST_UPDATED_DATETIME"] = last_update_datetime.strftime(
        '%Y-%m-%d %H:%M')

    print("Done")
    return dict_data


def isPrice(obj):
    if "k" in obj or "K" in obj or '元' in obj or '00' in obj or '50' in obj or obj[
            -1] == '0':
        return True
    else:
        return False


def ReplaceK(obj, k_list):
    for k in k_list:
        if k in obj:
            if '0.' in obj:
                obj = obj.replace('0.', '')
                obj = obj.replace(k, "00")
            elif '.5k' in obj:
                obj = obj.replace('.5k', '500')
            else:
                obj = obj.replace(k, "000")
                if '.' in obj:
                    obj = obj.replace('.', '')
    return obj


def ErrorMessage(error, obj):
    if isPrintError:
        print(error + " fail")
        print("|".join(obj.values()))
        print()


def Normalize(my_data):
    print("Normalizing...")
    normalize_data = copy.deepcopy(my_data)
    for index in range(1, int(normalize_data["LAST_UPDATED_ID"]) + 1):
        origin_item = normalize_data[str(index)]["origin"]
        item = origin_item.split("_")

        # 0    1   2    3   4    5
        # 賣徵_地點_狀況_品名_價錢_其它

        # if (item[0] in ("賣", "售", "徵", "買")):
        # 賣徵_地點_品名_價錢_其它
        try:
            try:
                if not ("一手" in item[2] or "二手" in item[2] or "全新" in item[2]
                        or "皆可" in item[2] or "不限" in item[2]):
                    item.insert(2, "")
            except:
                ErrorMessage("condition", normalize_data[str(index)])

            # 0    1   2    3   4    5   6
            # 賣徵_地點_狀況_品名_其它_價錢_其它    7
            # 0    1   2    3   4    5   6    7
            # 賣徵_地點_狀況_品名_品名_價錢_其它_其它   8
            try:
                if (not isPrice(item[4]) and len(item) > 5):
                    item[3] += " " + item[4]
                    others_index = 6
                    for i in range(5, len(item)):
                        # to recognize price
                        if isPrice(item[i]):
                            item[4] = item[i]
                            others_index = i + 1
                            break
                        else:
                            item[3] += " " + item[i]
                    item[5] = " ".join(item[others_index:len(item)])
                    for i in range(len(item) - others_index):
                        item.pop(-1)
            except:
                ErrorMessage("rearrange", normalize_data[str(index)])

            _dict = normalize_data[str(index)]

            # generate obj
            try:
                _dict["sell_or_collect"] = item[0].strip()
                _dict["location"] = item[1].strip()
                _dict["condition"] = item[2].strip()
                _dict["name"] = item[3].strip()
                try:
                    _dict["price"] = item[4].strip()
                except:
                    ErrorMessage("price", normalize_data[str(index)])
                try:
                    _dict["others"] = item[5].strip()
                except:
                    ErrorMessage("others", normalize_data[str(index)])
            except:
                ErrorMessage("obj", normalize_data[str(index)])

            try:
                # 0    1   2    3   4    5
                # 賣徵_地點_狀況_品名_品名_其它     6
                if not isPrice(_dict["price"]):
                    _dict["price"], _dict["others"] = _dict["others"], _dict[
                        "price"]
            except:
                ErrorMessage("swap price and others",
                             normalize_data[str(index)])

            try:
                k_list = ['k', 'K']
                _dict["price"] = ReplaceK(_dict["price"], k_list)
            except:
                ErrorMessage("ReplaceK", normalize_data[str(index)])
        except:
            print()
            print(f"!!!!!")
            ErrorMessage("fatal error", normalize_data[str(index)])
            print(f"!!!!!")
            print()

    print("Done")
    return normalize_data


def CheckData(old_data, new_data):
    checked_data = copy.deepcopy(old_data)
    for _id in new_data.keys():
        if checked_data.get(_id) == None:
            checked_data[_id] = new_data[_id]

    return checked_data


def WtiteJson(my_data, filename):
    json_data = open(f"./json/{filename}.json", 'w', encoding='utf-8')
    json.dump(my_data, json_data, ensure_ascii=False)
    json_data.close()


def ReadJson(filename):
    with open(f'./json/{filename}.json', 'r', encoding='utf-8') as f:
        return json.load(f)