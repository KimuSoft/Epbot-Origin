"""
    <seta_josa>
    한국어 조사 변환 자체 라이브러리입니다.
"""
import hgtk
import re


class Josa:
    def convert(self, string: str):
        string = string.replace("(이)랑", "랑(이랑)")
        string = string.replace("(으)로", "로(으로)")
        string = string.replace("(이)다", "다(이다)")
        string = string.replace("(이)잖", "잖(이잖)")
        string = string.replace("(이)자", "자(이자)")
        string = string.replace("(이)라", "라(이라)")

        ls = string.split(" ")
        for k in ls:
            p = re.compile(r"..\(.+\)")
            r = p.findall(k)

            for i in r:
                p = re.compile(r"(.).\(.+\)")
                josa_list = i[1:].replace(")", "").split("(")
                if "잖" in i or "자" in i:
                    josa_list.sort(reverse=True)
                else:
                    josa_list.sort()

                try:
                    dec = hgtk.letter.decompose(i[0])
                except hgtk.exception.NotHangulException:
                    string = string.replace(i, i[0] + josa_list[0])
                    continue

                if dec[2] == "":
                    string = string.replace(i, i[0] + josa_list[0])
                else:
                    string = string.replace(i, i[0] + josa_list[1])

        return string
