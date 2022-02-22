"""
<Sentence 객체>
- 문장을 통해 객체를 생성합니다.
EX) st = Sentence('안녕하세요')

- 태그 리스트 데이터와 함께 넣을 경우 해당 태그에 해당하는 내용만 조사합니다.
(나머지는 무조건 문제 없음 처리.)
EX) st = Sentence('안녕하세요')
"""

from static.hanspell import spell_checker
import re
import hgtk

from db import seta_json
from utils import tag as eptag

nadict = seta_json.get_json("static/bad_words.json", {"yoks": [], "ems": [], "jcs": []})


def reload():
    global nadict
    nadict = seta_json.get_json(
        "static/bad_words.json", {"yoks": [], "ems": [], "jcs": []}
    )


class Sentence:
    content = ""

    def __init__(self, sentence=""):
        self.content = sentence
        # logger.debug(f"'{sentence}' 문장 객체 생성")

    def prohibition(self, tags=["*"]):
        """금칙어 관련 해당 태그 목록과 걸린 목록을 반환
        tags에 아무 것도 넣지 않으면 모든 태그를 검사

        <금칙어 태그>
        욕설금지, 야한말금지, 정치발언금지, ..."""
        correct = []  # 걸린 태그 리스트
        what = []  # 걸린 말의 키워드

        # 불필요한 요소를 제외하고 키워드화
        replaces = [
            ".",
            ",",
            " ",
            "/",
            "1",
            "2",
            "3",
            "4",
            "5",
            "7",
            "8",
            "'",
            '"',
            "?",
            "-",
            "=",
            "\n",
            "~",
            "`",
            "@",
            "|",
        ]
        keyword = to_keyword(self.content, replaces)

        # 욕설 필터링
        for tag in eptag.prohibit_tags:
            if tag in tags or tags == ["*"]:
                for i in nadict[tag]:
                    p = re.compile(i.replace("//", "\\"))
                    li = p.findall(keyword)
                    if len(li) > 0:
                        correct.append(tag)
                        what += li

        # logger.debug(f"금칙어 // {correct}, {what}")
        for i in what:
            if type(i) == tuple:
                what.remove(i)
                what.append("".join(i))
        return correct, what

    # 처음 객체를 만들면 어떤 어미인지 분석합니다.
    def termination(self, tags=["*"]):
        """말투 태그 목록에 들어있는 것 중 문장에 해당하는 태그 목록을 반환
        tags에 아무 것도 넣지 않으면 모든 태그를 검사

        <말투 태그>
        예요체, ㅂ니다체, 냥냥체, 마침표, ..."""

        # 불필요한 요소를 제외하고 키워드화
        replaces = [".", "?", "!", "/", "❤️", "⭐", "💕", "\n", "~", "|", "*", "_"]
        keyword = to_keyword(self.content, replaces)
        correct = []  # 걸린 태그 리스트

        # 공통 존댓말
        if (
            keyword == "예"
            or keyword == "네"
            or keyword == "아니오"
            or keyword.endswith("님")
        ):
            if "예요체" in tags or tags == ["*"]:
                correct.append("예요체")
            if "ㅂ니다체" in tags or tags == ["*"]:
                correct.append("ㅂ니다체")

        # 예요체 분석
        if "예요체" in tags or tags == ["*"]:
            if (
                keyword.endswith("요")
                or keyword.endswith("죠")
                and not keyword.endswith(" 예요")
                and not keyword.endswith(" 요")
            ):
                correct.append("예요체")

        # ㅂ니다체 분석
        if "ㅂ니다체" in tags or tags == ["*"]:
            de_munjang = hgtk.text.decompose(keyword).replace("ᴥ", "")
            if (
                de_munjang.endswith("ㅂㄴㅣㄷㅏ")
                or de_munjang.endswith("ㅂㄴㅣㄲㅏ")
                or de_munjang.endswith("ㅂㅅㅣㄷㅏ")
            ):
                correct.append("ㅂ니다체")

        # 다나까체 분석
        if "다나까체" in tags or tags == ["*"]:
            if keyword.endswith("다") or keyword.endswith("나") or keyword.endswith("까"):
                correct.append("다나까체")

        # 읍니다체 분석
        if "읍니다체" in tags or tags == ["*"]:
            if keyword.endswith("읍니다"):
                correct.append("읍니다체")

        # 냥냥체 분석
        if "냥냥체" in tags or tags == ["*"]:
            if (
                keyword.endswith("냥")
                or keyword.endswith("다냐")
                or keyword.endswith("냣")
                or keyword.endswith("냐앙")
            ):
                correct.append("냥냥체")

        # 뀨뀨체 분석
        if "뀨뀨체" in tags or tags == ["*"]:
            if (
                keyword.endswith("뀨")
                or keyword.endswith("뀨웃")
                or keyword.endswith("뀻")
                or keyword.endswith("뀽")
            ):
                correct.append("뀨뀨체")

        # 애오체 분석
        if "애오체" in tags or tags == ["*"]:
            if (
                keyword.endswith("애오")
                or keyword.endswith("새오")
                or keyword.endswith("어오")
            ):
                correct.append("애오체")

        # 이즈나체 분석
        if "이즈나체" in tags or tags == ["*"]:
            if keyword.endswith(", 예요"):
                correct.append("이즈나체")

        # 멍멍체 분석
        if "멍멍체" in tags or tags == ["*"]:
            if keyword.endswith("멍"):
                correct.append("멍멍체")

        # 음슴체 분석
        if "음슴체" in tags or tags == ["*"]:
            de_munjang = hgtk.text.decompose(keyword).replace("ᴥ", "")
            if de_munjang.endswith("ㅁ"):
                correct.append("음슴체")

        # logger.debug(f"말투 // {correct}")
        return correct

    def determination(self, tags=["*"]):
        """말투 태그 목록에 들어있는 것 중 문장에 해당하는 태그 목록을 반환
        tags에 아무 것도 넣지 않으면 모든 태그를 검사

        <말투 태그>
        예요체, ㅂ니다체, 냥냥체, 마침표, ..."""

        # 불필요한 요소를 제외하고 키워드화
        replaces = [".", "?", "!", "/", "❤️", "⭐", "💕", "\n"]
        keyword = to_keyword(self.content, replaces)
        correct = []  # 걸린 태그 리스트

        # 공통 존댓말
        if (
            keyword == "예"
            or keyword == "네"
            or keyword == "아니오"
            or keyword.endswith("님")
        ):
            if "예요체" in tags or tags == ["*"]:
                correct.append("예요체")
            if "ㅂ니다체" in tags or tags == ["*"]:
                correct.append("ㅂ니다체")

        # 예요체 분석
        if "예요체" in tags or tags == ["*"]:
            if (
                keyword.endswith("요")
                and not keyword.endswith(" 예요")
                and not keyword.endswith(" 요")
            ):
                correct.append("예요체")

        # ㅂ니다체 분석
        if "ㅂ니다체" in tags or tags == ["*"]:
            de_munjang = hgtk.text.decompose(keyword).replace("ᴥ", "")
            if (
                de_munjang.endswith("ㅂㄴㅣㄷㅏ")
                or de_munjang.endswith("ㅂㄴㅣㄲㅏ")
                or de_munjang.endswith("ㅂㅅㅣㄷㅏ")
            ):
                correct.append("ㅂ니다체")

        # 애오체 분석
        if "애오체" in tags or tags == ["*"]:
            if (
                keyword.endswith("애오")
                or keyword.endswith("새오")
                or keyword.endswith("어오")
            ):
                correct.append("애오체")

        # 이즈나체 분석
        if "이즈나체" in tags or tags == ["*"]:
            if keyword.endswith(", 예요"):
                correct.append("이즈나체")

        # logger.debug(f"말투 // {correct}")
        return correct

    def spelling(self):
        """해당 문장의 한국어 맞춤법 일치 여부(bool)와 분석 결과 문자열(str)을 반환"""
        result = check_machum(self.content)

        if result is not True:
            if result is not False:
                return False, f'- "{self.content}"\n+ "{result}"\n// 이렇게 바꾸면 될...걸?'
            else:
                return False, f'- "{self.content}"\n// 이 문장... 잘 이해가 안 돼네.'
        else:
            return True, "+ 딱히 문제는 없는 것 같은데...?"

    def machim(self):
        """마침표 있음 유무를 반환"""
        return (
            self.content.endswith(".")
            or self.content.endswith("!")
            or self.content.endswith("?")
        )


def to_keyword(st: str, replaces: list):
    """문장에서 list에 들어간 문자열을 빼고 영어의 경우 소문자화시킴"""
    for i in replaces:
        st = st.replace(i, "")
    return st.lower()


def check_machum(text: str):
    """문장의 text를 넣어 주면 맞춤법이 맞는지 알려 줌
    <반환값>
    문제 없는 경우 : True
    문제 있는 경우 : 수정한 문자열
    표준어 아님 : False
    """
    text = text.replace("  ", " ")  # 과한 띄어쓰기로 글자 잡아먹기 방지
    result = spell_checker.check(text)
    check = result.as_dict()
    error = int(check["errors"])
    fixed = check["checked"]  # .replace('kimuiskimya', author.name)
    check.clear()

    if error == 0:  # 문제 없음
        return True

    elif text != fixed:  # 수정됨
        return fixed

    else:  # 표준어가 아니지 않을까 싶음
        return False


def reload_bw():
    global nadict
    nadict = seta_json.get_json("bad_words.json", {"yoks": [], "ems": [], "jcs": []})
