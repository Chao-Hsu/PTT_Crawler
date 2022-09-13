import crawler
import os
import urllib.parse
import datetime

line_notify_token = "ZeniahVg1Mp7VVJO57EVlKbUGQf72zMnP4LZUMy5oxp"
# line_notify_token = "UMoGyNcXg6FyOihn9CyTE6JcCql4KDdvUMLfouDGxMU"

now = tonow = datetime.datetime.now()
if (now.day == 1 and now.hour == 0 and now.minute < 5):
    msg = f"{str(now.month)}月置底推文交易"
    query = f'curl -H "Authorization: Bearer {line_notify_token}" -d "message=%0D%0A%0D%0A{msg}" https://notify-api.line.me/api/notify'

url = "https://www.ptt.cc/bbs/Headphone/M.1530392323.A.695.html"

json_data = crawler.GetDataAndNormalize(url)

data = crawler.ReadJson()

for i in range(
        int(data["LAST_UPDATED_ID"]) + 1,
        int(json_data["LAST_UPDATED_ID"]) + 1):

    item = json_data[str(i)]
    msg_sell_or_collect = item["sell_or_collect"]
    msg_name = item["name"]
    msg_price = item["price"]
    msg_datetime = item["datetime"]
    msg = f"[{msg_sell_or_collect}]{msg_name}"
    if msg_price != "" and not msg_price[0].isdigit():
        msg += f" - NT${msg_price}"
    msg = urllib.parse.quote(msg)

    query = f'curl -H "Authorization: Bearer {line_notify_token}" -d "message=%0D%0A{msg}%0D%0A({msg_datetime})" https://notify-api.line.me/api/notify'
    os.system(query)

crawler.WtiteJson(json_data)
