from bs4 import BeautifulSoup
import requests
import datetime
import json


def CrawlFindAll(url, dom, class_list):
    my_headers = {'cookie': 'over18=1;'}
    response = requests.get(url, headers=my_headers)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "lxml")
    result_list = []
    for i in class_list:
        result_list.append(soup.find_all(dom, i))
    return result_list


def GenerateObj(item, userid, count, datetime_):
    _dict = {}
    if (len(item) > 1):
        # _dict["id"] = count
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
        _dict["user_id"] = userid
        _dict["datetime"] = str(datetime_)

    return _dict


def GetDataAndNormalize(url):
    class_ = ["push-content", "push-ipdatetime", "push-userid"]
    push_content, push_ipdatetime, push_userid = CrawlFindAll(
        url, "span", class_)

    count_data = 0
    last_update = datetime.datetime.today()
    dict_data = {}
    dict_data["LAST_UPDATED_ID"] = 0
    dict_data["LAST_UPDATED_DATETIME"] = last_update

    for i in range(len(push_content)):
        item = push_content[i].text.replace(": ", "").strip().split("_")
        intput_date = push_ipdatetime[i].text.replace("\n", "_").replace(
            ":", "_").replace("/", "_").replace(" ", "_").split("_")
        date = datetime.datetime(year=datetime.date.today().year,
                                 month=int(intput_date[1]),
                                 day=int(intput_date[2]),
                                 hour=int(intput_date[3]),
                                 minute=int(intput_date[4]))
        last_update = date
        if (item[0] in ("賣", "售", "徵", "買")):
            if (not ("一手" in item[2] or "二手" in item[2] or "全新" in item[2]
                     or "皆可" in item[2] or "不限" in item[2])):
                item.insert(2, "闕漏")
            if (len(item[1]) > 2):
                item[1] = item[1][0] + item[1][1]
            try:
                if (not item[4][0].isdigit() and len(item) > 5):
                    item[3] += " " + item[4]
                    for i in range(4, len(item) - 1):
                        item[i] = item[i + 1]
                    item.pop(-1)
            except:
                pass
            try:
                if (item[3][0].isdigit()):
                    if (len(item) <= 4):
                        item.append(item[3])
                        item[3] = ""
                    elif (not item[4][0].isdigit()):
                        item[3], item[4] = item[4], item[3]
            except:
                pass
            try:
                if (item[5][0].isdigit()):
                    if (len(item) <= 4):
                        item.append(item[3])
                        item[3] = ""
                    elif (not item[4][0].isdigit()):
                        item[5], item[4] = item[4], item[5]
            except:
                pass
            try:
                if (not item[4][0].isdigit() and not item[5][0].isdigit()):
                    if (item[5] == "" and item[4] != ""):
                        item[5], item[4] = item[4], item[5]
            except:
                pass
            try:
                if (item[4][-1].lower() == 'k'):
                    item[4] = str(int(float(item[4][0:-1]) * 1000))
            except:
                pass
            count_data += 1
            dict_data[str(count_data)] = GenerateObj(item, push_userid[i].text,
                                                     count_data, date)
        else:
            _str = push_content[i].text.replace(": ", "").strip().split("_")
            _dict = dict_data[str(count_data)]
            if (not _dict.get("price")):
                _dict["name"] += _str[0]
                if (len(_str) > 1):
                    _dict["price"] = _str[1]
                    if (_dict["price"][-1].lower() == 'k'):
                        _dict["price"] = str(
                            int(float(_dict["price"][0:-1]) * 1000))
                if (len(_str) > 2):
                    _dict["others"] = _str[2]
            elif (_dict.get("others")):
                _dict["others"] += push_content[i].text.replace(": ",
                                                                "").strip()
            else:
                _dict["others"] = push_content[i].text.replace(": ",
                                                               "").strip()
    dict_data["LAST_UPDATED_DATETIME"] = str(last_update)
    dict_data["LAST_UPDATED_ID"] = str(count_data)
    return dict_data


def WtiteJson(dict_data):
    json_data = open("./data.json", 'w', encoding='utf-8')
    json.dump(dict_data, json_data, ensure_ascii=False)
    json_data.close()


def ReadJson():
    with open('data.json', 'r', encoding='utf-8') as f:
        return json.load(f)