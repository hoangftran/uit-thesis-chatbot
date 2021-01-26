import os
import flask
from flask import request, jsonify
import json
import pandas as pd
import datetime as dt
import pytz
import requests
import base64
import psycopg2
import sqlalchemy
import logging
from model import report, history_mssv, thoi_khoa_bieu
from constant import BOT_CODE, BOT_TOKEN, USER_DEPARTMENT_ID, department_map
import utils
import re


app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET', 'POST'])
def home():
    return "<h1>Welcome to UIT Chatbot API</h1><p>Written by HOANG TRAN VAN, University of Information Technology</p><p>For more information, please contact: <a href='mailto:16520449@gm.uit.edu.vn'>16520449@gm.uit.edu.vn</a></p>"


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.route('/mssv_validation', methods=['GET', 'POST'])
def mssv_validation():

    data = json.loads(str(request.data.decode('utf-8')))
    mssv = data['mssv']

    mssv = utils.get_mssv_entity(mssv)
    valid_result = utils.mssv_validation(mssv)

    return {
        'set_attributes': {
            'mssv': '{}'.format(valid_result.get('mssv')),
            'validation_bool': '{}'.format(valid_result.get('validation_bool'))
        }
    }


@app.route('/check_history_mssv', methods=['GET', 'POST'])
def check_history_mssv():
    try:
        data = json.loads(str(request.data.decode('utf-8')))
        sender_id = data['sender_id']

        history_mssv_obj = history_mssv.HistoryMssvDB()
        df = history_mssv_obj.check_history_mssv(sender_id)
        if df is not None:
            df = df.values
        if df is None or len(df) == 0:
            mssv = ""
        else:
            mssv = df[0][1]
    except Exception as e:
        print('/check_history_mssv :: ', e)
    finally:
        return {
            'set_attributes': {
                'mssv': '{}'.format(mssv)
            }
        }

@app.route('/insert_history_mssv', methods=['GET', 'POST'])
def insert_history_mssv():
    try:
        data = json.loads(str(request.data.decode('utf-8')))
        sender_id = data['sender_id']
        mssv_input = data['mssv']

        now = dt.datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime('%Y-%m-%d %H:%M:%S')
        history_mssv_obj = history_mssv.HistoryMssvDB()

        df = history_mssv_obj.check_history_mssv(sender_id)

        if df is not None:
            df=df.values
        
        if (df is None) or (len(df) == 0):
            history_mssv_obj.insert_row(sender_id, mssv_input, now)
        else:
            history_mssv_obj.update_history_mssv(sender_id, mssv_input, now)
    except Exception as e:
        print('/insert_history_mssv :: ', e)
    finally:
        return {
            'set_attributes': {
                'mssv': '{}'.format(mssv_input)
            }
        }


@app.route('/send_report', methods=['GET', 'POST'])
def send_report():
    try:
        data = json.loads(str(request.data.decode('utf-8')))
        mssv = data['mssv']
        report_content = data['report_content']
        sender_id = data['sender_id']

        report_intent = utils.get_rasa_intent(report_content)

        headers = {
            'Authorization': 'Bearer %s' % (BOT_TOKEN[report_intent]),
            'Content-Type': 'application/json',
        }

        payload_data = {
            "set_attributes": {
                "sender_id_sv": "{}".format(sender_id),
                "mssv_sv": "{}".format(mssv),
                "report_intent": "{}".format(report_intent)
            }
        }
        base64_payload_data = base64.b64encode(json.dumps(payload_data).encode('utf-8'))

        data = """{
            "messages": [
                {
                    "content": {
                        "text": "[%s]: %s",
                        "buttons": [
                            {
                                "title": "Trả lời report",
                                "payload": "Reply report#%s"
                            }
                        ]
                    },
                    "type": "text"
                }
            ],
            "app_code": "%s",
            "sender_id": "%s",
            "channel": "facebook"
        }""" % (mssv, report_content, base64_payload_data.decode("utf-8"), BOT_CODE[report_intent], USER_DEPARTMENT_ID[report_intent])

        response = requests.post('https://bot.fpt.ai/api/send_messages/', headers=headers, data=data.encode('utf-8'))

        now = dt.datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime('%Y-%m-%d %H:%M:%S')

        report_obj = report.ReportDB()
        report_obj.insert_row(sender_id, mssv, report_intent, report_content, now, 'success')
    except Exception as e:
        print('/send_report', e)
        report_obj = report.ReportDB()
        report_obj.insert_row(sender_id, mssv, report_intent, report_content, now, 'failed')
        return {
            'set_attributes': {
                'report_status': 'failed'
            }
        }
    finally:
        return {
            'set_attributes': {
                'report_status': 'success',
                'report_intent': '{}'.format(department_map[report_intent])
            }
        }

@app.route('/reply_report', methods=['GET', 'POST'])
def reply_report():
    try:
        data = json.loads(str(request.data.decode('utf-8')))
        mssv = data['mssv']
        report_content = data['report_content']
        report_intent = data['report_intent']
        sender_id_sv = data['sender_id_sv']

        headers = {
            'Authorization': 'Bearer %s' % (BOT_TOKEN[report_intent]),
            'Content-Type': 'application/json',
        }

        data = """{
            "messages": [
                {
                    "content": {
                        "text": "[%s]: %s"
                    },
                    "type": "text"
                }
            ],
            "app_code": "%s",
            "sender_id": "%s",
            "channel": "facebook"
        }""" % (department_map[mssv], report_content, BOT_CODE[report_intent], sender_id_sv)

        response = requests.post('https://bot.fpt.ai/api/send_messages/', headers=headers, data=data.encode('utf-8'))

        now = dt.datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime('%Y-%m-%d %H:%M:%S')
        report_obj = report.ReportDB()
        report_obj.insert_row(sender_id_sv, mssv, report_intent, report_content, now, 'success')
    except Exception as e:
        print('/reply_report :: ', e)
        report_obj = report.ReportDB()
        report_obj.insert_row(sender_id_sv, mssv, report_intent, report_content, now, 'failed')
        return {
            'set_attributes': {
                'report_status': 'failed'
            }
        }
    finally:
        return {
            'set_attributes': {
                'report_status': 'success',
                'mssv': '{}'.format(mssv)
            }
        }

@app.route('/get_tkb_all', methods=['GET', 'POST'])
def get_tkb_all():
    try:
        data = json.loads(str(request.data.decode('utf-8')))
        mssv = data['mssv']
        sender_id = data['sender_id']

        tkb_obj = thoi_khoa_bieu.ThoiKhoaBieuDB()
        df = tkb_obj.get_tkb(mssv)

        if (df is not None):
            df=df.values
        
        if (df is None) or (len(df) == 0):
            result= {
                'set_attributes': {
                    'tkb_status': 'failed'
                }
            }
        else:
            tkb = json.loads(df[0][1])
            if((tkb['mssv'] == mssv) and (tkb['status'] == 1)):
                tkb_content = tkb['contents']
                messages = [{
                        "type": "text",
                        "content": {
                            "text": "Thông tin TKB của MSSV {}: ".format(mssv)
                        }
                    }]
                for course in tkb_content:
                    messages.append({
                        "type": "text",
                        "content": {
                            "text": "{}, môn {}, {}, tiết {}".format(course['schedules']['day_of_week'], course['course_name'], course['room'].replace('P', 'phòng'), course['schedules']['periods'])
                        }
                    })
                result = {
                    "channel": "api",
                    "app_code": "{}".format(BOT_CODE['FPT_Fanpage']),
                    "messages": messages,
                    "sender_id": "{}".format(sender_id)
                }
            else:
                result = {
                    'set_attributes': {
                        'tkb_status': 'failed'
                    }
                }
    except Exception as e:
        print('/get_tkb :: ', e)
        result = {
            'set_attributes': {
                'tkb_status': 'failed'
            }
        }
    finally:
        return result

@app.route('/get_tkb_by_course_name', methods=['GET', 'POST'])
def get_tkb_by_course_name():
    try:
        data = json.loads(str(request.data.decode('utf-8')))
        mssv = data['mssv']
        course_name_input = data['course_name_input']
        sender_id = data['sender_id']

        tkb_obj = thoi_khoa_bieu.ThoiKhoaBieuDB()
        df = tkb_obj.get_tkb(mssv)
        if (df is not None):
                df=df.values
            
        if (df is None) or (len(df) == 0):
            result= {
                'set_attributes': {
                    'tkb_status': 'failed'
                }
            }
        else:
            tkb=json.loads(df[0][1])
            # course_name_input = utils.get_rasa_entity(course_name_input, 'course_name')
            course_name_input = utils.get_course_name_entity(course_name_input)
            if (course_name_input == -1) or (course_name_input == None):
                result= {
                    'set_attributes': {
                        'tkb_status': 'failed'
                    }
                }
            else:
                if((tkb['mssv'] == mssv) and (tkb['status'] == 1)):
                    tkb_content = tkb['contents']
                    tkb_by_course_name = utils.get_tkb_by_course_name(course_name_input, tkb_content)

                    if (len(tkb_by_course_name) == 0) or (tkb_by_course_name == None):
                        result = {
                            'set_attributes': {
                                'tkb_status': 'failed'
                            }
                        }
                    else:
                        messages = [{
                            "type": "text",
                            "content": {
                                "text": "Thông tin môn học '{}' của MSSV {}: ".format(course_name_input, mssv)
                            }
                        }]
                        for course in tkb_by_course_name:
                            messages.append({
                                "type": "text",
                                "content": {
                                    "text": "{}, môn {}, {}, tiết {}".format(course['schedules']['day_of_week'], course['course_name'], course['room'].replace('P', 'phòng'), course['schedules']['periods'])
                                }
                            })
                        result = {
                            "channel": "api",
                            "app_code": "{}".format(BOT_CODE['FPT_Fanpage']),
                            "messages": messages,
                            "sender_id": "{}".format(sender_id)
                        }
                else:
                    result = {
                        'set_attributes': {
                            'tkb_status': 'failed'
                        }
                    }
    except Exception as e:
        print('/get_tkb_by_course_name :: ', e)
        result = {
            'set_attributes': {
                'tkb_status': 'failed'
            }
        }
    finally:
        return result

@app.route('/get_tkb_by_datetime', methods=['GET', 'POST'])
def get_tkb_by_datetime():
    try:
        data = json.loads(str(request.data.decode('utf-8')))
        mssv = data['mssv']
        datetime_input = data['datetime_input']
        sender_id = data['sender_id']

        tkb_obj = thoi_khoa_bieu.ThoiKhoaBieuDB()
        df = tkb_obj.get_tkb(mssv)

        if (df is not None):
                df=df.values
            
        if (df is None) or (len(df) == 0):
            result= {
                'set_attributes': {
                    'tkb_status': 'failed'
                }
            }
        else:
            tkb=json.loads(df[0][1])
            if((tkb['mssv'] == mssv) and (tkb['status'] == 1)):
                tkb_content = tkb['contents']
                tkb_by_datetime = utils.get_tkb_by_datetime(datetime_input, tkb_content)
                print(tkb_by_datetime)
                if (len(tkb_by_datetime) == 0 or tkb_by_datetime is None):
                    result = {
                        'set_attributes': {
                            'tkb_status': 'failed'
                        }
                    }
                else:
                    messages = [{
                        "type": "text",
                        "content": {
                            "text": "Thông tin TKB của MSSV {}: ".format(mssv)
                        }
                    }]
                    for course in tkb_by_datetime:
                        messages.append({
                            "type": "text",
                            "content": {
                                "text": "{}, môn {}, {}, tiết {}".format(course['schedules']['day_of_week'], course['course_name'], course['room'].replace('P', 'phòng'), course['schedules']['periods'])
                            }
                        })
                    result = {
                        "channel": "api",
                        "app_code": "{}".format(BOT_CODE['FPT_Fanpage']),
                        "messages": messages,
                        "sender_id": "{}".format(sender_id)
                    }
            else:
                result = {
                    'set_attributes': {
                        'tkb_status': 'failed'
                    }
                }
    except Exception as e:
        print('/get_tkb_by_datetime :: ', e)
        result = {
            'set_attributes': {
                'tkb_status': 'failed'
            }
        }
    finally:
        return result


app.run(host='localhost', port=5000, threaded=True)