import re
import string
import requests

from constant import RASA_NLU_MODEL_PATH, REGEX_DATE, REGEX_DAY_MONTH, REGEX_MONTH_YEAR
from rasa.nlu.model import Interpreter

import datetime as dt
import pytz
import string
import numpy as np
import json


def mssv_validation(mssv):

    final_result = dict()
    validation_bool = 1

    if mssv == '' or mssv == None or mssv == -1:
        validation_bool = 0
        mssv = -1
    else:
        mssv = (mssv.translate(str.maketrans('', '', string.punctuation))).replace(' ', '')
        mssv_regex = re.compile('([0-9]{2})+(52)+([0-9]{4})')
        
        if(len(mssv) != 8):
            validation_bool = 0
            mssv = -1
            
        if (not mssv_regex.match(mssv)):
            validation_bool = 0
            mssv = -1
        
    final_result['mssv'] = mssv
    final_result['validation_bool'] = validation_bool
    
    return final_result

def get_rasa_intent(sample):
    interpreter = Interpreter.load(RASA_NLU_MODEL_PATH)

    intent_parsed = interpreter.parse(sample).get('intent').get('name')

    if not intent_parsed:
        intent_parsed = 'PHONG_THIET_BI'
    return intent_parsed

def get_rasa_entity(sample, entity_name):
    interpreter = Interpreter.load(RASA_NLU_MODEL_PATH)
    parsed = interpreter.parse(sample)

    entities=[]
    for item in parsed.get('entities'):
        if entity_name in item.values():
            entities.append(item)
    
    if len(entities) == 0:
        entity_value = -1

    if len(entities) == 1:
        entity_value = entities[0].get('value')
    else:
        return -1

    return entity_value

def get_course_name_entity(sample):
    interpreter = Interpreter.load(RASA_NLU_MODEL_PATH)
    parsed = interpreter.parse(sample)

    regex_entity = [i for i in parsed['entities'] if i['extractor'] == 'RegexEntityExtractor']
    if len(regex_entity) == 1:
        if regex_entity[0]['entity'] == 'course_name':
            course_name = regex_entity[0]['value']
    else:
        course_name = -1
    
    return course_name

def get_mssv_entity(sample):
    interpreter = Interpreter.load(RASA_NLU_MODEL_PATH)
    parsed = interpreter.parse(sample)

    regex_entity = [i for i in parsed['entities'] if i['extractor'] == 'DIETClassifier']
    if len(regex_entity) == 1:
        if regex_entity[0]['entity'] == 'mssv':
            mssv = regex_entity[0]['value']
    else:
        mssv = -1
    
    return mssv

def get_day_of_week(sample):
    try:
        data = {
        'locale': 'vi_VI',
        'text': '{}'.format(sample)
        }

        response = requests.post('http://0.0.0.0:8000/parse', data=data)
        parsed = json.loads(response.text)
        for i in range(len(parsed)):
            if ('dim' in parsed[i].keys()) and (parsed[i]['dim'] == "time"):
                return dt.datetime.strptime(parsed[i]["value"]['value'][:-6],'%Y-%m-%dT%H:%M:%S.%f').weekday()
            else:
                return -1
    except Exception:
        return -1

def clean_string(text):
    """ Remove punctuations and stop words, lower string """
    
    stopwords = ['với', 'được', 'nữa', 'nhỉ', 'nha', 'nhá', 'luôn']
    text = ''.join([word for word in text if word not in string.punctuation])
    text = text.lower()
    text = ' '.join([word for word in text.split() if word not in stopwords])
    return text

def levenshtein_distance(first, second):
    first = clean_string(first)
    second = clean_string(second)

    first_len = len(first)
    second_len = len(second)
    if first_len == 0 or second_len == 0:
        raise ValueError("Inputs must not have length 0")

    matrix = np.zeros((first_len+1, second_len+1), dtype=np.int)
    matrix[:,0] = range(first_len+1)
    matrix[0,:] = range(second_len+1)

    for i, first_char in enumerate(first, start=1):
        for j, second_char in enumerate(second, start=1):
            if first_char == second_char:
                cost = 0
            else:
                cost = 1

            min_cost = min(
                matrix[i-1, j] + 1,
                matrix[i, j-1] + 1,
                matrix[i-1, j-1] + cost
            )
            matrix[i, j] = min_cost

    return matrix[first_len, second_len]

def get_similarity(first, second):
    changes = levenshtein_distance(first, second)
    min_total_chars = min(len(first), len(second))
    
    return (min_total_chars - changes)/min_total_chars

def get_tkb_by_course_name(course_name_input, tkb_content):
    
    list_courses_match = set()
    similarity_threshold = 0.5

    for course in tkb_content:
        course_name = course['course_name']
        if(get_similarity(course_name, course_name_input) >= similarity_threshold):
            list_courses_match.add(course_name)
    
    tkb_by_course_name = list()
    for course in tkb_content:
        for course_match in list(list_courses_match):
            if course_match == course['course_name']:
                tkb_by_course_name.append(course)
        
    return tkb_by_course_name

def parse_datetime(msg, timezone="Asia/Ho_Chi_Minh"):
    try:  
        tz = pytz.timezone(timezone)
        now = dt.datetime.now(tz=tz)

        date_str = []
        regex = REGEX_DATE
        regex_day_month = REGEX_DAY_MONTH
        regex_month_year = REGEX_MONTH_YEAR
        pattern = re.compile("(%s|%s|%s)" % (
            regex, regex_month_year, regex_day_month), re.UNICODE)

        matches = pattern.finditer(msg)
        for match in matches:
            _dt = match.group(0)
            _dt = _dt.replace("/", "-").replace("|", "-").replace(":", "-").replace("tháng", "-").replace("thang", "-")
            for i in range(len(_dt.split("-"))):
                if len(_dt.split("-")[i]) == 1:
                    _dt = _dt.replace(_dt.split("-")[i], "0"+_dt.split("-")[i])
            if len(_dt.split("-")) == 2:
                pos1 = _dt.split("-")[0]
                pos2 = _dt.split("-")[1]
                if 0 < int(pos1) < 32 and 0 < int(pos2) < 13:
                    _dt = pos1+"-"+pos2+"-"+str(now.year)
            date_str.append(_dt)

        if(len(date_str) != 1):
            msg = msg.replace("/", "-").replace("|", "-").replace(":", "-").replace("tháng", "-").replace("thang", "-").replace("sáng", "9:00").replace("sang", "9:00").replace("chiều", "15:00").replace("chieu", "15:00")
            interpreter = Interpreter.load(RASA_NLU_MODEL_PATH)
            parsed = interpreter.parse(msg)
            duckling_entity = [i for i in parsed['entities'] if i['extractor'] == 'DucklingEntityExtractor']
            
            if len(duckling_entity) == 1:
                if type(duckling_entity[0]['value']) == str:
                    datetime_parsed = dt.datetime.strptime(duckling_entity[0]['value'][:-6],'%Y-%m-%dT%H:%M:%S.%f')
                else:
                    datetime_parsed = -1
            else:
                datetime_parsed = -1
        else:
            datetime_parsed = dt.datetime.strptime(date_str[0],'%d-%m-%Y')
    except Exception as e:
        print(e)
    finally:
        return datetime_parsed

def get_day_of_week_2(msg):
    datetime_parsed = parse_datetime(msg)
    print(datetime_parsed)
    if datetime_parsed == -1:        
        day_of_week = -1
    else:
        day_of_week = datetime_parsed.weekday()
    return day_of_week

def get_tkb_by_datetime(datetime_input, tkb_content):

    day_of_week = get_day_of_week_2(datetime_input)

    tkb_by_datetime = list()
    for course in tkb_content:
        if course['schedules']['day_of_week_code'] == day_of_week:
            tkb_by_datetime.append(course)
    return tkb_by_datetime


print(get_day_of_week('thứ hai tuần sau'))