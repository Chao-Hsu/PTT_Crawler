import crawler
import line_msg
import json_io
import sys
from datetime import datetime

url_title = "https://www.ptt.cc/bbs/Headphone/index.html"
url_push = "https://www.ptt.cc/bbs/Headphone/M.1530392323.A.695.html"

version = "test"
line_msg.line_notify_token_personal = token["test"]
crawler.isPrintError = False


def main(argv):
    now = datetime.now()
    if now.hour >= 8 or now.hour < 3:
        if len(argv) > 1:
            if "--prod" in argv:
                version = "prod"
            if "--delay" in argv:
                crawler.DoSomeDelay()

        token = json_io.ReadJson("Line_Token")
        line_msg.line_notify_token = token[version]

        # title
        my_title_data = json_io.ReadJson("data_title")
        crawl_title_data, new_data_id_list = crawler.GetTitleData(
            url_title, my_title_data
        )
        checked_title_data = crawler.CheckData(my_title_data, crawl_title_data)

        line_msg.SendTitleMessage(checked_title_data, new_data_id_list)

        json_io.WtiteJson(checked_title_data, "data_title")

        # push
        crawl_push_data = crawler.GetPushData(url_push)
        normalized_push_data = crawler.Normalize(crawl_push_data)
        my_push_data = json_io.ReadJson("data_push")

        line_msg.SendItemMessage(my_push_data, normalized_push_data)

        # if now.day == 1 and now.hour == 0 and now.minute == 0:
        if normalized_push_data["LAST_UPDATED_ID"] < my_push_data["LAST_UPDATED_ID"]:
            json_io.WtiteJson(
                my_push_data, f"Headphone/Push/{datetime.strftime(now,'%Y%m')}"
            )

        json_io.WtiteJson(normalized_push_data, "data_push")


if __name__ == "__main__":
    main(sys.argv)
