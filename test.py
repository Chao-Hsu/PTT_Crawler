import crawler
import line_msg
import sys

url_title = "https://www.ptt.cc/bbs/Headphone/index.html"
url_push = "https://www.ptt.cc/bbs/Headphone/M.1530392323.A.695.html"

crawler.isPrintError = False


def main(argv):
    if (len(argv) > 1 and argv[1] == '--delay'):
        crawler.DoSomeDelay()

    line_msg.line_notify_token = crawler.ReadJson("Line_Token")["test"]

    # title
    my_title_data = crawler.ReadJson("data_title")
    crawl_title_data, new_data_id_list = crawler.GetTitleData(
        url_title, my_title_data)
    checked_title_data = crawler.CheckData(my_title_data, crawl_title_data)

    line_msg.SendTitleMessage(checked_title_data, new_data_id_list)

    crawler.WtiteJson(checked_title_data, "data_title")

    # push
    crawl_push_data = crawler.GetPushData(url_push)
    normalized_push_data = crawler.Normalize(crawl_push_data)
    my_push_data = crawler.ReadJson("data_push")

    line_msg.SendItemMessage(my_push_data, normalized_push_data)

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
