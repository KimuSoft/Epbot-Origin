from bs4 import BeautifulSoup
import cloudscraper
import urllib.request
import os
import re

scraper = cloudscraper.CloudScraper()


IMAGE_SAVE_DIR = "static/fish_image"


def img_download(url: str, name: str):
    urllib.request.urlretrieve(url, f"{IMAGE_SAVE_DIR}/{name}.png")


def get_html(name: str):
    _html = ""
    keyword = (
        str(name.encode("euc-kr"))
        .replace("b'", "")
        .replace("'", "")
        .replace("\\x", "%")
        .upper()
    )
    url = (
        "https://www.nifs.go.kr/frcenter/species/?curPage=1&order=asc&mf_psc_cd=&new_input=no&keyword="
        + keyword
    )
    print(url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 7.0; SM-G892A Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/67.0.3396.87 Mobile Safari/537.36"
    }
    resp = scraper.get(url, headers=headers)
    # print(resp)
    if resp.status_code == 200:
        _html = resp.text
    # print(_html)
    return _html


# UTF-8을 EUC-KR로 변환
def utf2euc(string: str):
    return string.encode("euc-kr")


def get_image(name: str):
    if os.path.isfile(f"{IMAGE_SAVE_DIR}/{name}.png"):
        return None
    html = get_html(name)

    bs = BeautifulSoup(html, "html.parser")
    # with open('호해액.html', 'w', encoding='UTF8') as file:
    #     file.write(html)

    bs = bs.find("table", attrs={"class": "sTable_03"})
    # bs = bs.find('tbody')
    for b in bs.children:
        data = b.find("img")
        if data is None or isinstance(data, int):
            continue
        name = data["title"]
        img = "https://www.nifs.go.kr" + data["src"]

        reg = r"\([^)]*\)|\[[^]]*\]|<[^>]*>"
        name = re.sub(reg, "", name)
        if not os.path.isfile(f"{IMAGE_SAVE_DIR}/{name}.png"):
            img_download(img, name)

    # print('종료되었습니다.')

    # with open('호해액2.html', 'w', encoding='UTF8') as file:
    #     file.write(str(bs))
