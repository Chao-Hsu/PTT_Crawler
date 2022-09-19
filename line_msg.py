import os
import urllib.parse
import datetime
import json_io

line_notify_token = ""

# TODO:改成id變小的時候
# now = tonow = datetime.datetime.now()
# if (now.day == 1 and now.hour == 0 and now.minute < 5):
#     msg = f"{str(now.month)}月置底推文交易"
#     query = f'curl -H "Authorization: Bearer {line_notify_token}" -d "message=%0D%0A%0D%0A{msg}" https://notify-api.line.me/api/notify'

id_blacklist = json_io.ReadJson('keywords')['blacklist']['id']


def SendLineMessage(msg):
    query = f'curl -H "Authorization: Bearer {line_notify_token}" -d "message={msg}" https://notify-api.line.me/api/notify'
    os.system(query)


def SendItemMessage(my_data, normalized_data):
    for i in range(
            int(my_data["LAST_UPDATED_ID"]) + 1,
            int(normalized_data["LAST_UPDATED_ID"]) + 1):

        item = normalized_data[str(i)]

        line_newline = "%0D%0A"

        msg_sell_or_collect = urllib.parse.quote(item["sell_or_collect"])
        msg_name = urllib.parse.quote(item["name"])
        msg_price = urllib.parse.quote(item["price"])
        msg_user_id = urllib.parse.quote(item["user_id"])
        msg_others = urllib.parse.quote(item["others"])
        msg_datetime = urllib.parse.quote(item["datetime"])

        msg = ""

        msg += f"{line_newline}{urllib.parse.quote('Headphone置底推文交易')}"

        if msg_name != "":
            msg += f"{line_newline}[{msg_sell_or_collect}] {msg_name}"

        if msg_price != "":
            msg += f"{line_newline}[{urllib.parse.quote('價錢')}] {msg_price}"

        if msg_user_id != "":
            msg += f"{line_newline}[ID] {msg_user_id}"

        if msg_others != "":
            msg += f"{line_newline}[{urllib.parse.quote('備註')}] {msg_others}"

        if msg_datetime != "":
            msg += f"{line_newline}({msg_datetime})"

        if item["user_id"] in id_blacklist:
            msg = f"%0D%0A%0D%0A{urllib.parse.quote('中壢人注意！！！')}{msg}"

        SendLineMessage(msg)


def SendTitleMessage(my_data, new_data_id_list):
    for _id in new_data_id_list:
        item = my_data[_id]

        msg_title = urllib.parse.quote(item["title"])
        msg_url = urllib.parse.quote(item["url"])
        msg_date = urllib.parse.quote(item["date"])
        msg = f'%0D%0A{msg_title} ({msg_date})%0D%0A{msg_url}'

        if item["user_id"] in id_blacklist:
            msg = f"%0D%0A%0D%0A{urllib.parse.quote('中壢人注意！！！')}{msg}"

        SendLineMessage(msg)