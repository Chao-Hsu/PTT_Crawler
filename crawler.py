from bs4 import BeautifulSoup
import requests
import datetime
import json
import copy
from fake_useragent import UserAgent
import random
import time


def DoSomeDelay():
    delay_choices = [1, 3, 5, 14, 25, 40]
    delay = random.choice(delay_choices)
    time.sleep(delay)


def CrawlerFindAll(url, dom, class_list):
    # DoSomeDelay()

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


def GenerateObj(item, userid, count, datetime_):
    _dict = {}
    if (len(item) > 1):
        _dict["sell_or_collect"] = item[0].strip()
        _dict["location"] = item[1].strip()
        _dict["condition"] = item[2].strip()
        _dict["name"] = item[3].strip()
        _dict["price"] = ""
        _dict["others"] = ""
        if (_dict["sell_or_collect"] in ("徵", "買")):
            try:
                if (item[4][0].isdigit()):
                    _dict["price"] = item[4].strip()
                else:
                    _dict["others"] = item[4].strip()
            except:
                print(str(count) + "_".join(item) + " no item[4]")
        else:
            try:
                _dict["price"] = item[4].strip()
            except:
                print(str(count) + "_".join(item) + " no item[4]")
            try:
                _dict["others"] = " ".join(item[5:len(item)])
            except:
                print(str(count) + "_".join(item) + " no item[5]")
            try:
                if (not _dict["price"][0].isdigit()):
                    _dict["others"] = _dict["price"] + _dict["others"]
                    _dict["price"] = ""
            except:
                print(str(count) + "_".join(item) + " no price")
        _dict["user_id"] = userid
        _dict["datetime"] = str(datetime_)
        _dict["origin"] = "|".join(_dict.values())
    return _dict


def GetData(url):
    print("Getting data...")
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
        intput_date = push_ipdatetime[i].text.replace("\n", "_").replace(
            ":", "_").replace("/", "_").replace(" ", "_").split("_")
        push_datetime = datetime.datetime(year=datetime.date.today().year,
                                          month=int(intput_date[1]),
                                          day=int(intput_date[2]),
                                          hour=int(intput_date[3]),
                                          minute=int(intput_date[4]))
        last_update_datetime = push_datetime

        if (_item[0] in ("賣", "售", "徵", "買")):
            # if (not ("一手" in item[2] or "二手" in item[2] or "全新" in item[2]
            #          or "皆可" in item[2] or "不限" in item[2])):
            #     item.insert(2, "")
            count_data += 1
            dict_data[str(count_data)] = {
                "sell_or_collect": "",
                "location": "",
                "condition": "",
                "name": "",
                "price": "",
                "others": "",
                "datetime": str(push_datetime),
                "origin": _item
            }
            # dict_data[str(count_data)]["origin"] = _item
        else:
            _s = push_content[i].text.replace(": ", "").strip()
            dict_data[str(count_data)]["origin"] += _s
    dict_data["LAST_UPDATED_DATETIME"] = str(last_update_datetime)
    dict_data["LAST_UPDATED_ID"] = str(count_data)
    print("Done")

    return dict_data


def isPrice(obj):
    if "k" in obj or "K" in obj or '元' in obj or '內' in obj or '00' in obj or obj[
            -1] == '0':
        return True
    else:
        return False


def Normalize(my_data):
    print("Normalizing...")
    normalize_data = copy.deepcopy(my_data)
    for index in range(1, int(normalize_data["LAST_UPDATED_ID"]) + 1):
        origin_item = normalize_data[str(index)]["origin"]
        item = origin_item.split("_")

        # 0    1   2    3   4    5
        # 賣徵_地點_狀況_品名_價錢_其它

        if (item[0] in ("賣", "售", "徵", "買")):
            # 賣徵_地點_品名_價錢_其它
            if not ("一手" in item[2] or "二手" in item[2] or "全新" in item[2]
                    or "皆可" in item[2] or "不限" in item[2]):
                item.insert(2, "")

            # 0    1   2    3   4    5   6
            # 賣徵_地點_狀況_品名_其它_價錢_其它    7
            # 0    1   2    3   4    5   6    7
            # 賣徵_地點_狀況_品名_品名_價錢_其它_其它   8
            try:
                if (not item[4][0].isdigit() and len(item) > 5):
                    item[3] += " " + item[4]
                    others_index = 6
                    for i in range(5, len(item)):
                        # to recognize price
                        if isPrice(item[i][-1]):
                            item[4] = item[i]
                            others_index = i + 1
                            break
                        else:
                            item[3] += " " + item[i]
                    item[5] = " ".join(item[others_index:len(item) + 1])
                    for i in range(len(item) - others_index):
                        item.pop(-1)
            except:
                print(f"err {index}")

            _dict = normalize_data[str(index)]

            try:
                _dict["sell_or_collect"] = item[0].strip()
                _dict["location"] = item[1].strip()
                _dict["condition"] = item[2].strip()
                _dict["name"] = item[3].strip()
                try:
                    _dict["price"] = item[4].strip()
                except:
                    pass
                try:
                    _dict["others"] = item[5].strip()
                except:
                    pass

                # 0    1   2    3   4    5
                # 賣徵_地點_狀況_品名_品名_其它     6
                if not isPrice(_dict["price"]):
                    _dict["price"], _dict["others"] = _dict["others"], _dict[
                        "price"]
                    print(f"{index} swap price and others")
            except:
                pass

            try:
                if "k" in _dict["price"]:
                    _dict["price"] = _dict["price"].replace("k", "000")
                    if '.' in _dict["price"]:
                        _dict["price"] = _dict["price"].replace('.', '')
                if "K" in _dict["price"]:
                    _dict["price"] = _dict["price"].replace("K", "000")
                    if '.' in _dict["price"]:
                        _dict["price"] = _dict["price"].replace('.', '')
            except:
                pass
    print("Done")
    return normalize_data

    # if (len(item[1]) > 2):
    # item[1] = item[1][0] + item[1][1]

    #         try:
    #             if (item[3][0].isdigit()):
    #                 if (len(item) <= 4):
    #                     item.append(item[3])
    #                     item[3] = ""
    #                 elif (not item[4][0].isdigit()):
    #                     item[3], item[4] = item[4], item[3]
    #         except:
    #             pass
    #         try:
    #             if (item[5][0].isdigit()):
    #                 if (len(item) <= 4):
    #                     item.append(item[3])
    #                     item[3] = ""
    #                 elif (not item[4][0].isdigit()):
    #                     item[5], item[4] = item[4], item[5]
    #         except:
    #             pass
    #         try:
    #             if (not item[4][0].isdigit() and not item[5][0].isdigit()):
    #                 if (item[5] == "" and item[4] != ""):
    #                     item[5], item[4] = item[4], item[5]
    #         except:
    #             pass
    #         TODO: 重複???
    #         try:
    #             if (not item[4][0].isdigit() and not item[5][0].isdigit()):
    #                 if (item[5] == "" and item[4] != ""):
    #                     item[5], item[4] = item[4], item[5]
    #         except:
    #             pass
    #         try:
    #             if (item[4][0].isdigit()):
    #                 list_k = item[4].split("k")
    #                 if len(list_k) > 1:
    #                     item[4] = str(int(float(list_k[0]) * 1000)) + list_k[1]
    #                 list_K = item[4].split("K")
    #                 if len(list_K) > 1:
    #                     item[4] = str(int(float(list_K[0]) * 1000)) + list_K[1]
    #         except:
    #             pass
    #         try:
    #             if (item[4][-1].lower() == "k"):
    #                 item[4] = str(int(float(item[4][0:-1]) * 1000))
    #         except:
    #             pass
    #         count_data += 1
    #         dict_data[str(count_data)] = GenerateObj(item, push_userid[i].text,
    #                                                  count_data, date)
    #         dict_data[str(count_data)]["origin"] = _item
    #     else:
    #         _s = push_content[i].text.replace(": ", "").strip()
    #         _str = _s.split("_")
    #         _dict = dict_data[str(count_data)]
    #         if not _dict.get("price"):
    #             _dict["name"] += _str[0]
    #             if (len(_str) > 1):
    #                 _dict["price"] = _str[1]
    #                 if (_dict["price"][-1].lower() == "k"):
    #                     _dict["price"] = str(
    #                         int(float(_dict["price"][0:-1]) * 1000))
    #             if (len(_str) > 2):
    #                 _dict["others"] = " ".join(_str[2:len(_str)])
    #         elif _dict.get("price"):
    #             isDigitEach = True
    #             for c in _str[0]:
    #                 if not c.isdigit():
    #                     isDigitEach = False
    #             if isDigitEach:
    #                 _dict["price"] += _str[0]
    #             else:
    #                 __str = " ".join(_str)
    #                 if _dict.get("others"):
    #                     _dict["others"] += __str
    #                 else:
    #                     _dict["others"] = __str
    #         dict_data[str(count_data)]["origin"] += _s
    # dict_data["LAST_UPDATED_DATETIME"] = str(last_update)
    # dict_data["LAST_UPDATED_ID"] = str(count_data)
    # return dict_data


def WtiteJson(my_data, filename):
    json_data = open(f"./{filename}.json", 'w', encoding='utf-8')
    json.dump(my_data, json_data, ensure_ascii=False)
    json_data.close()


def ReadJson():
    with open('data.json', 'r', encoding='utf-8') as f:
        return json.load(f)