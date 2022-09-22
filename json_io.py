import json


def WtiteJson(my_data, filename):
    json_data = open(f"./json/{filename}.json", "w", encoding="utf-8")
    json.dump(my_data, json_data, ensure_ascii=False)
    json_data.close()


def ReadJson(filename):
    with open(f"./json/{filename}.json", "r", encoding="utf-8") as f:
        return json.load(f)
