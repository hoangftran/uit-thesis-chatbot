import os

REGEX_DATE = r"(3[01]|[12][0-9]|0?[1-9])[-\/:|](1[0-2]|0?[1-9])([-\/:|](2[0-1][0-9][0-9]))"
REGEX_DAY_MONTH = r"(3[01]|[12][0-9]|0?[1-9])[-\/:|](1[0-2]|0?[1-9])"
REGEX_MONTH_YEAR = r"(1[0-2]|0?[1-9])([-\/:|](2[0-1][0-9][0-9]))"

BOT_CODE = {
    'FPT_Fanpage': 'd4c4693620be2fd0e03013b4ff7363c1',
    'PHONG_THIET_BI': 'dad0eea41acfd595489f69e217a0f99c',
    'PHONG_DAO_TAO': '49fa0c8435d993cfe27897a7a8484b1a'
}

BOT_TOKEN = {
    'FPT_Fanpage': '1e1fe218b56218efaca311d2d72e0264',
    'PHONG_THIET_BI': '990fcb060ef5a3e4705e84c1e5110270',
    'PHONG_DAO_TAO': '5bdfc7cd48d6373b367222d9ae5cc4e2'
}

USER_DEPARTMENT_ID = {
    'FPT_Fanpage': '3057658924363117',
    'PHONG_THIET_BI': '4509146825824300',
    'PHONG_DAO_TAO': '3673462279341258'
}

department_map = {
    'PHONG_DAO_TAO': 'Phòng đào tạo',
    'PHONG_THIET_BI': 'Phòng thiết bị'
}

RASA_NLU_MODEL_PATH = '/home/hoangtv/Documents/uit-thesis-chatbot_diet/rasa/models/nlu-20210123-151418/nlu'