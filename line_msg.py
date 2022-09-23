import os
import urllib.parse
import datetime
import json_io

line_notify_token = ""
line_notify_token_personal = ""

line_newline = "%0D%0A"
ptt_url = "https://www.ptt.cc/bbs"


def GetIdBlacklist():
    return json_io.ReadJson("keywords")["blacklist"]["id"]


def SendLineMessageOfError(error_msg):
    query = f'curl -H "Authorization: Bearer {line_notify_token_personal}" -d "message={error_msg}" https://notify-api.line.me/api/notify'
    os.system(query)


def SendLineMessage(msg):
    query = f'curl -H "Authorization: Bearer {line_notify_token}" -d "message={msg}" https://notify-api.line.me/api/notify'
    os.system(query)


def SendItemMessage(my_data, normalized_data, board):
    for i in range(
        int(my_data["LAST_UPDATED_ID"]) + 1, int(normalized_data["LAST_UPDATED_ID"]) + 1
    ):

        msg_list = [f"{board['index']} #置底推文交易"]

        item = normalized_data[str(i)]
        if item["name"] == "":
            error_msg = (
                f"{line_newline}Error: #{i} {urllib.parse.quote(item['origin'])}"
            )
            SendLineMessageOfError(error_msg)
            msg_list.append(item["origin"])
            # continue
        else:
            msg_list.append(f'[{item["sell_or_collect"]}] {item["name"]}')
            if item["price"] != "":
                msg_list.append(f'[價錢] {item["price"]}')
            if item["others"] != "":
                msg_list.append(f'[備註] {item["others"]}')
        msg_list.append(
            f'[ID] {item["user_id"]+(" <--中壢人！" if item["user_id"] in GetIdBlacklist() else "")}'
        )
        msg_list.append(f'({item["datetime"]})')

        msg = line_newline
        for m in msg_list:
            msg += urllib.parse.quote(m) + line_newline
        msg += "/".join((ptt_url, board["index"], board["push"]))

        SendLineMessage(msg)


def SendTitleMessage(my_data, new_data_id_list, board):
    index = board["index"]
    for _id in new_data_id_list:
        item = my_data[_id]

        msg_board = urllib.parse.quote(f"{index} #交易文")
        msg_title = urllib.parse.quote(item["title"])
        msg_url = urllib.parse.quote(item["url"])
        msg_date = urllib.parse.quote(item["date"])
        msg = f"{line_newline}{msg_board}{line_newline}{msg_title} ({msg_date}){line_newline}{msg_url}"

        if item["user_id"] in GetIdBlacklist():
            msg = f"{urllib.parse.quote('中壢人！')}{msg}"

        SendLineMessage(msg)
