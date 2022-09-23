from bs4 import BeautifulSoup
import requests
import datetime
import copy
from fake_useragent import UserAgent
import random
import time
import re

isPrintError = False


def DoSomeDelay():
    delay_choices = [1, 3, 5, 14, 25, 40]
    delay = random.choice(delay_choices)
    print(f"delay for {delay} seconds")
    time.sleep(delay)


def CrawlerFindAll(url, dom, class_list):
    user_agent = UserAgent()
    my_headers = {
        "cookie": "over18=1",
        "content-type": "text/html; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
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
    class_ = ("title", "author", "date")
    title, author, date = CrawlerFindAll(url, "div", class_)
    print("Done")

    dict_data = {}
    new_data = []

    print("Go through data...")
    for index in range(len(title)):
        try:
            title_string = title[index].find("a").string
            title_href = title[index].find("a")["href"]
            try:
                type_index = title_string.index("[") + 1
                title_index = title_string.index("]")
                _type = title_string[type_index:title_index]
                if _type in ("交易", "情報", "贈送"):
                    _title = title_string[title_index + 1:].strip()
                    try:
                        input_date = date[index].string.strip().split("/")
                        _title_date = datetime.datetime(
                            year=datetime.date.today().year,
                            month=int(input_date[0]),
                            day=int(input_date[1]),
                        )
                        title_date = _title_date.strftime("%Y-%m-%d")
                    except:
                        print(f"date: {date} error")
                    try:
                        _id = title_href.strip().split("/")[-1].replace(".html", "")
                        if not old_data.get(_id):
                            new_data.append(_id)
                            dict_data[_id] = {
                                "type": _type,
                                "title": _title,
                                "url": "https://www.ptt.cc" + title_href,
                                "user_id": author[index].string,
                                "date": title_date,
                                "origin": title_string,
                            }
                    except:
                        print(f"id: {_id} error")
            except:
                pass
        except:
            pass

    print("Done")
    return dict_data, new_data


def GetPushData(url):
    print("Getting push data...")
    class_ = ("push-content", "push-ipdatetime", "push-userid")
    push_content, push_ipdatetime, push_userid = CrawlerFindAll(url, "span", class_)
    print("Done")

    count_data = 0
    last_update_datetime = datetime.datetime.today()
    dict_data = {}
    dict_data["LAST_UPDATED_ID"] = 0
    dict_data["LAST_UPDATED_DATETIME"] = last_update_datetime

    print("Go through data...")
    for i in range(len(push_content)):
        _item = push_content[i].text.replace(": ", "").strip()
        input_date = (
            push_ipdatetime[i]
            .text.replace("\n", "_")
            .replace(":", "_")
            .replace("/", "_")
            .replace(" ", "_")
            .split("_")
        )
        push_datetime = datetime.datetime(
            year=datetime.date.today().year,
            month=int(input_date[1]),
            day=int(input_date[2]),
            hour=int(input_date[3]),
            minute=int(input_date[4]),
        )
        last_update_datetime = push_datetime

        if _item[0] in ("賣", "售", "徵", "買"):
            count_data += 1
            dict_data[str(count_data)] = {
                "sell_or_collect": "",
                "location": "",
                "condition": "",
                "name": "",
                "price": "",
                "others": "",
                "user_id": push_userid[i].text.replace(": ", "").strip(),
                "datetime": push_datetime.strftime("%Y-%m-%d %H:%M"),
                "origin": _item,
            }
        else:
            _s = push_content[i].text.replace(": ", "").strip()
            dict_data[str(count_data)]["origin"] += _s
    dict_data["LAST_UPDATED_ID"] = str(count_data)
    dict_data["LAST_UPDATED_DATETIME"] = last_update_datetime.strftime("%Y-%m-%d %H:%M")

    print("Done")
    return dict_data


def isSlicePrice(obj):
    tuple_keyword = ("k", "K", "元", "00", "50")
    index_keyword = []
    for i in tuple_keyword:
        if i in obj:
            index_keyword.append(obj.find(i))
    # TODO:正數
    pattern = re.compile(r"^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$")
    for i in index_keyword:
        _str = obj[:i]
        if not pattern.match(_str) and str != "":
            return False
    return True


def isPrice(obj):
    # TODO: fix price with / or ~
    return isSlicePrice(obj) and (
        "k" in obj or "K" in obj or "元" in obj or "00" in obj or "50" in obj
    )


def ReplaceK(obj, k_list):
    point_index = obj.find(".")
    for k in k_list:
        if k in obj:
            if "." in obj:
                _int = obj[:point_index]
                if "0." in obj:
                    if int(_int) > 0:
                        obj = obj.replace(".", "").replace(k, "00")
                    else:
                        obj = obj.replace("0.", "").replace(k, "00")
                else:
                    obj = obj.replace(".", "").replace(k, "00")
            else:
                obj = obj.replace(k, "000")

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
                # TODO: /
                sell_condition = ("一手", "二手", "全新")
                collect_condition = ("一手", "二手", "全新", "皆可", "不限")
                for i in collect_condition:
                    if i in item[2]:
                        _list = item[2].split(i)
                        if len(_list) > 1:
                            if _list[1] != "":
                                item[3] = _list[1]
                            item[2] = i
                            break
                if item[0] in ("賣", "售"):
                    if not item[2] in sell_condition:
                        item.insert(2, "")
                elif item[0] in ("徵", "買"):
                    if not item[2] in collect_condition:
                        item.insert(2, "")

                # if not ("一手" in item[2] or "二手" in item[2] or "全新" in item[2]
                # or "皆可" in item[2] or "不限" in item[2]):
                # item.insert(2, "")
            except:
                ErrorMessage("condition", normalize_data[str(index)])

            # 0    1   2    3   4    5   6
            # 賣徵_地點_狀況_品名_其它_價錢_其它    7
            # 0    1   2    3   4    5   6    7
            # 賣徵_地點_狀況_品名_品名_價錢_其它_其它   8
            try:
                if not isPrice(item[4]) and len(item) > 5:
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
                    item[5] = " ".join(item[others_index : len(item)])
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
                    _dict["price"], _dict["others"] = _dict["others"], _dict["price"]
            except:
                ErrorMessage("swap price and others", normalize_data[str(index)])

            try:
                k_list = ("k", "K")
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
