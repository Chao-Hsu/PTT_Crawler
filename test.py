import crawler
import line_msg
import json_io
import sys
import datetime

url_title = "https://www.ptt.cc/bbs/Headphone/index.html"
url_push = "https://www.ptt.cc/bbs/Headphone/M.1530392323.A.695.html"

crawler.isPrintError = False


def main(argv):
    if datetime.datetime.now().hour >= 8 or datetime.datetime.now().hour < 3:
        version = "test"
        if len(argv) > 1:
            if "--prod" in argv:
                version = "prod"
            if "--delay" in argv:
                crawler.DoSomeDelay()

        token = json_io.ReadJson("Line_Token")
        line_msg.line_notify_token_personal = token["test"]
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

        json_io.WtiteJson(normalized_push_data, "data_push")

        # TODO:檢查ID變小
        # if id變小:
        #     query=f''
        #     os.system(query)
        #     json_io.WtiteJson(my_data,"年+上個月")
        # else:
        #     json_io.WtiteJson(crawl_data,"data.json")


if __name__ == "__main__":
    main(sys.argv)
