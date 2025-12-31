import requests
import json
import time
import random

from typing import TypedDict


class CityConfig(TypedDict):
    name: str
    id: str
    pinyin: str


def get_city_configs() -> list[CityConfig]:
    return [
        {"name": "北京", "id": "1100", "pinyin": "beijing"},
        {"name": "上海", "id": "3100", "pinyin": "shanghai"},
        {"name": "广州", "id": "4401", "pinyin": "guangzhou"},
        {"name": "深圳", "id": "4403", "pinyin": "shenzhen"},
        {"name": "武汉", "id": "4201", "pinyin": "wuhan"},
        {"name": "天津", "id": "1200", "pinyin": "tianjin"},
        {"name": "南京", "id": "3201", "pinyin": "nanjing"},
        {"name": "香港", "id": "8100", "pinyin": "xianggang"},
        {"name": "重庆", "id": "5000", "pinyin": "chongqing"},
        {"name": "杭州", "id": "3301", "pinyin": "hangzhou"},
        {"name": "沈阳", "id": "2101", "pinyin": "shenyang"},
        {"name": "大连", "id": "2102", "pinyin": "dalian"},
        {"name": "成都", "id": "5101", "pinyin": "chengdu"},
        {"name": "长春", "id": "2201", "pinyin": "changchun"},
        {"name": "苏州", "id": "3205", "pinyin": "suzhou"},
        {"name": "佛山", "id": "4406", "pinyin": "foshan"},
        {"name": "昆明", "id": "5301", "pinyin": "kunming"},
        {"name": "西安", "id": "6101", "pinyin": "xian"},
        {"name": "郑州", "id": "4101", "pinyin": "zhengzhou"},
        {"name": "长沙", "id": "4301", "pinyin": "changsha"},
        {"name": "宁波", "id": "3302", "pinyin": "ningbo"},
        {"name": "无锡", "id": "3202", "pinyin": "wuxi"},
        {"name": "青岛", "id": "3702", "pinyin": "qingdao"},
        {"name": "南昌", "id": "3601", "pinyin": "nanchang"},
        {"name": "福州", "id": "3501", "pinyin": "fuzhou"},
        {"name": "东莞", "id": "4419", "pinyin": "dongguan"},
        {"name": "南宁", "id": "4501", "pinyin": "nanning"},
        {"name": "合肥", "id": "3401", "pinyin": "hefei"},
        {"name": "石家庄", "id": "1301", "pinyin": "shijiazhuang"},
        {"name": "贵阳", "id": "5201", "pinyin": "guiyang"},
        {"name": "厦门", "id": "3502", "pinyin": "xiamen"},
        {"name": "乌鲁木齐", "id": "6501", "pinyin": "wulumuqi"},
        {"name": "温州", "id": "3303", "pinyin": "wenzhou"},
        {"name": "济南", "id": "3701", "pinyin": "jinan"},
        {"name": "兰州", "id": "6201", "pinyin": "lanzhou"},
        {"name": "常州", "id": "3204", "pinyin": "changzhou"},
        {"name": "徐州", "id": "3203", "pinyin": "xuzhou"},
        {"name": "呼和浩特", "id": "1501", "pinyin": "huhehaote"},
        {"name": "哈尔滨", "id": "2301", "pinyin": "haerbin"},
        {"name": "太原", "id": "1401", "pinyin": "taiyuan"},
        {"name": "洛阳", "id": "4103", "pinyin": "luoyang"},
        {"name": "南通", "id": "3206", "pinyin": "nantong"},
        {"name": "绍兴", "id": "3306", "pinyin": "shaoxing"},
    ]


class StationJSON(TypedDict):
    n: str


class LineJSON(TypedDict):
    ln: str
    st: list[StationJSON]


class CityJSON(TypedDict):
    l: list[LineJSON]


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://map.amap.com/subway/index.html",
    "Host": "map.amap.com",
}


def fetch_city_json(city: CityConfig) -> CityJSON | None:
    name = city["name"]
    url = "https://map.amap.com/service/subway?_1469083453978&srhdata={id}_drw_{pinyin}.json".format(
        id=city["id"],
        pinyin=city["pinyin"],
    )
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        response.encoding = "utf-8"
        return response.json()
    except Exception as e:
        print(f"Error fetching data for {name}: {e}")
        return None


StationData = str
LineData = list[StationData]
CityData = dict[str, LineData]
MetroData = dict[str, CityData]


def parse_city_data(raw_data: CityJSON) -> CityData | None:
    if not raw_data or "l" not in raw_data:
        return None

    parsed_data: CityData = {}
    for line in raw_data["l"]:
        line_name = line["ln"]
        stations = LineData()
        if "st" in line:
            for station in line["st"]:
                stations.append(station["n"])
        parsed_data[line_name] = stations

    return parsed_data


def run_crawler() -> MetroData:
    cities = get_city_configs()
    print(f"Starting metro data crawler for {len(cities)} cities...")

    all_metro_data = MetroData()
    for city in cities:
        name = city["name"]
        print(f"Crawling data for {name}...", end=" ")

        raw_json = fetch_city_json(city)
        if raw_json:
            clean_data = parse_city_data(raw_json)
            if clean_data:
                all_metro_data[name] = clean_data
                print(f"Success ({len(clean_data)} lines)")
            else:
                print(f"Failed (parsing error)")
        else:
            print(f"Failed (fetching error)")

        time.sleep(random.uniform(0.5, 1.0))

    return all_metro_data


def show_metro_data(data: MetroData) -> None:
    for city, lines in data.items():
        print(f"City: {city}")
        for line, stations in lines.items():
            print(f"  Line: {line}")
            for station in stations:
                print(f"    Station: {station}")


def save_metro_data(data: MetroData, filename: str) -> bool:
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("Data successfully saved to", filename)
        return True
    except IOError as e:
        print("Failed to save data to", filename, ":", e)
        return False


def load_metro_data(filename: str) -> MetroData | None:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("Data successfully loaded from", filename)
        return data
    except IOError as e:
        print("Failed to load data from", filename, ":", e)
        return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Metro Data Crawler")
    parser.add_argument("--save", type=str, help="File to save the metro data")
    parser.add_argument("--load", type=str, help="File to load the metro data")

    args = parser.parse_args()

    if args.load:
        metro_data = load_metro_data(args.load)
    else:
        metro_data = run_crawler()

    if metro_data is None:
        exit(1)

    if args.save:
        save_metro_data(metro_data, args.save)
