import crawler
import line_msg
import json_io
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta


crawler.isPrintError = False
ptt_url = "https://www.ptt.cc/bbs"
list_board = {
    "Headphone": {
        "index": "Headphone",
        "push": "M.1530392323.A.695.html",
    },
    "Audiophile": {
        "index": "Audiophile",
    },
}


def CrawlTitleAndNotify(board):
    index = board["index"]
    my_title_data = json_io.ReadJson(index)
    crawl_title_data, new_data_id_list = crawler.GetTitleData(
        "/".join((ptt_url, index)), my_title_data
    )
    checked_title_data = crawler.CheckData(my_title_data, crawl_title_data)

    line_msg.SendTitleMessage(checked_title_data, new_data_id_list, board)

    json_io.WtiteJson(checked_title_data, index)


def CrawlPushAndNotify(board):
    url = "/".join((ptt_url, board["index"], board["push"]))
    crawl_push_data = crawler.GetPushData(url)
    normalized_push_data = crawler.Normalize(crawl_push_data)

    index = "_".join((board["index"], "push"))
    my_push_data = json_io.ReadJson(index)

    line_msg.SendItemMessage(my_push_data, normalized_push_data, board)

    # if now.day == 1 and now.hour == 0 and now.minute == 0:
    if normalized_push_data["LAST_UPDATED_ID"] < my_push_data["LAST_UPDATED_ID"]:
        last_month = datetime.now() + relativedelta(months=-1)
        json_io.WtiteJson(
            my_push_data,
            "/".join((board["index"], "Push", datetime.strftime(last_month, "%Y%m"))),
        )

    json_io.WtiteJson(normalized_push_data, index)


def main(argv):
    now = datetime.now()
    if now.hour >= 8 or now.hour < 3:
        version = "test"
        if len(argv) > 1:
            if "--prod" in argv:
                version = "prod"
            if "--delay" in argv:
                crawler.DoSomeDelay()

        token = json_io.ReadJson("Line_Token")
        line_msg.line_notify_token = token[version]
        line_msg.line_notify_token_personal = token["test"]

        CrawlTitleAndNotify(list_board["Headphone"])

        CrawlPushAndNotify(list_board["Headphone"])


if __name__ == "__main__":
    main(sys.argv)
