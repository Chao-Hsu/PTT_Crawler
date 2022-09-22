import os
import urllib.parse
import datetime
import json_io

line_notify_token = ""
line_notify_token_personal = ""

# TODO:改成id變小的時候
# now = tonow = datetime.datetime.now()
# if (now.day == 1 and now.hour == 0 and now.minute < 5):
#     msg = f"{str(now.month)}月置底推文交易"
#     query = f'curl -H "Authorization: Bearer {line_notify_token}" -d "message=%0D%0A%0D%0A{msg}" https://notify-api.line.me/api/notify'

id_blacklist = json_io.ReadJson('keywords')['blacklist']['id']
line_newline = "%0D%0A"


def SendLineMessageOfError(error_msg):
    query = f'curl -H "Authorization: Bearer {line_notify_token_personal}" -d "message={error_msg}" https://notify-api.line.me/api/notify'
    os.system(query)


def SendLineMessage(msg):
    query = f'curl -H "Authorization: Bearer {line_notify_token}" -d "message={msg}" https://notify-api.line.me/api/notify'
    os.system(query)


def SendItemMessage(my_data, normalized_data):
    for i in range(
            int(my_data["LAST_UPDATED_ID"]) + 1,
            int(normalized_data["LAST_UPDATED_ID"]) + 1):

        msg_list = ['Headphone #置底推文交易']

        item = normalized_data[str(i)]
        if item["name"] == "":
            error_msg = f"{line_newline}Error: #{i} {urllib.parse.quote(item['origin'])}"
            SendLineMessageOfError(error_msg)
            msg_list.append(item["origin"])
            # continue
        else:
            msg_list.append(f'[{item["sell_or_collect"]}] {item["name"]}')
            if item["price"] != "":
                msg_list.append(f'[價錢] {item["price"]}')
            if item["others"] != "":
                msg_list.append(f'[備註] {item["others"]}')
        msg_list.append(f'[ID] {item["user_id"]}')
        msg_list.append(f'({item["datetime"]})')

        if item["user_id"] in id_blacklist:
            msg_list.insert(0, '---中壢人注意！---')

        msg = line_newline
        for m in msg_list:
            msg += urllib.parse.quote(m) + line_newline
        msg += "https://www.ptt.cc/bbs/Headphone/M.1530392323.A.695.html"

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