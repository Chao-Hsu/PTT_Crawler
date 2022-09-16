import crawler
import os
import urllib.parse
import datetime
import sys

#prod
line_notify_token = "8drpZinsFqBppybCSdzT8Nd4vcfXimIChGA7UWdZike"   #Akira Ptt Crawler
# line_notify_token = "ZeniahVg1Mp7VVJO57EVlKbUGQf72zMnP4LZUMy5oxp" #PttHeadphoneCrawler
#test
# line_notify_token = "UMoGyNcXg6FyOihn9CyTE6JcCql4KDdvUMLfouDGxMU"  #Akira Ptt Crawler to person

# TODO:改成id變小的時候
# now = tonow = datetime.datetime.now()
# if (now.day == 1 and now.hour == 0 and now.minute < 5):
#     msg = f"{str(now.month)}月置底推文交易"
#     query = f'curl -H "Authorization: Bearer {line_notify_token}" -d "message=%0D%0A%0D%0A{msg}" https://notify-api.line.me/api/notify'

url_title = "https://www.ptt.cc/bbs/Headphone/index.html"
url_push = "https://www.ptt.cc/bbs/Headphone/M.1530392323.A.695.html"

id_blacklist = ['IPv7', 'kev72806']


def SendLineMessage(msg):
    query = f'curl -H "Authorization: Bearer {line_notify_token}" -d "message={msg}" https://notify-api.line.me/api/notify'
    os.system(query)


def SendItemMessage(my_data, normalized_data):
    for i in range(
            int(my_data["LAST_UPDATED_ID"]) + 1,
            int(normalized_data["LAST_UPDATED_ID"]) + 1):

        item = normalized_data[str(i)]
        msg_sell_or_collect = item["sell_or_collect"]
        msg_name = item["name"]
        msg_price = item["price"]
        msg_datetime = item["datetime"]
        msg = f"[{msg_sell_or_collect}]{msg_name}"
        if msg_price != "":
            msg += f" - NT${msg_price}"
        msg = f"%0D%0A{urllib.parse.quote(msg)}%0D%0A({msg_datetime})"
        if item["used_id"] in id_blacklist:
            msg = f"{urllib.parse.quote('中壢人注意！！！')}{msg}"
        SendLineMessage(msg)


def SendTitleMessage(my_data, new_data_id_list):
    for _id in new_data_id_list:
        item = my_data[_id]
        msg_title = urllib.parse.quote(item["title"])
        msg_url = urllib.parse.quote(item["url"])
        msg_date = urllib.parse.quote(item["date"])
        msg = f'%0D%0A{msg_title} ({msg_date})%0D%0A{msg_url}'
        if item["used_id"] in id_blacklist:
            msg = f"{urllib.parse.quote('中壢人注意！！！')}{msg}"
        SendLineMessage(msg)


def main(argv):
    if (len(argv) > 1 and argv[1] == '--delay'):
        crawler.DoSomeDelay()

    # title
    my_title_data = crawler.ReadJson("data_title")
    crawl_title_data, new_data_id_list = crawler.GetTitleData(
        url_title, my_title_data)
    checked_title_data = crawler.CheckData(my_title_data, crawl_title_data)

    SendTitleMessage(checked_title_data, new_data_id_list)

    crawler.WtiteJson(checked_title_data, "data_title")

    # push
    crawl_push_data = crawler.GetPushData(url_push)
    normalized_push_data = crawler.Normalize(crawl_push_data)
    my_push_data = crawler.ReadJson("data_push")

    SendItemMessage(my_push_data, normalized_push_data)

    crawler.WtiteJson(normalized_push_data, "data_push")

    # TODO:檢查ID變小
    # if id變小:
    #     query=f''
    #     os.system(query)
    #     crawler.WtiteJson(my_data,"年+上個月")
    # else:
    #     crawler.WtiteJson(crawl_data,"data.json")


if __name__ == '__main__':
    main(sys.argv)
