'''seta_JSON 1.0
제작 : 키뮤소프트

파이썬 초보자 분들의 JSON 사용을 더욱 편리하게 만들어 드리는 모듈입니다.
※ 이 모듈은 PEP8을 준수하려고 노력은... 했습니다.

<사용법>
이 모듈을 사용하는 py 파일과 같은 경로에 놓은 뒤 코드 맨 윗 줄에
import seta_json as sj
...이라고 적어 주세요. (뒤의 'as sj'는 그냥 추천)
'''

import json
import os
from utils import logger


def set_json(exist: str, content: dict):
    '''content를 json 형식으로 exist 경로에 저장합니다.
    예) sj.set_json('키뮤귀여워.json', {'키뮤':1004})'''
    logger.debug(f'{exist} 작성')

    with open(exist, 'w', encoding="utf-8") as make_file:
        json.dump(content, make_file, ensure_ascii=False, indent="\t")


def get_json(exist: str, default_content=False):
    '''exist 경로의 json 파일을 불러옵니다.
    예) my_dict = sj.get_json('키뮤귀여워.json')

    파일이 없는 경우 None을 반환합니다.
    단, 이 경우에 default_content에 dict 값을 넣었을 경우 해당 dict 내용으로 그 경로에 json 파일을 생성합니다

    예) my_dict = sj.get_json('키뮤귀여워.json', default_content={'키뮤':1004})
    → 키뮤귀여워.json을 불러오지만 파일이 없을 경우 {'키뮤':1004} 내용으로 키뮤귀여워.json을 만듦.
    ※ 이 경우 반환값은 default_content ({'키뮤':1004})임.'''
    logger.debug(f'{exist} 로드')
    if not os.path.isfile(exist):
        if not default_content:
            print('[SETA_Module/ERROR] ' + exist + ' 파일은 존재하지 않습니다.')
            return None
        else:
            set_json(exist, default_content)
            return default_content
    else:
        with open(exist, encoding="utf-8") as json_file:
            return json.load(json_file)
