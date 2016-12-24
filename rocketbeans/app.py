#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import requests
from flask import Flask, render_template
from flask_ask import Ask, statement
import datetime

app = Flask(__name__)
ask = Ask(app, '/')

logging.getLogger('flask_ask').setLevel(logging.DEBUG)

url = 'http://api.rbtv.rodney.io/api/1.0'

@ask.launch
def launch():
    speech_text = "Willkommen zum inoffiziellen Rocket Beans Skill. Mit diesem Skill kannst du das Programm von Rocket Beans TV abfragen"
    return statement(speech_text).simple_card("Initial", speech_text)

@ask.intent('ScheduleNowIntent')
def now(title="", topic=""):
    format = '%Y-%m-%dT%H:%M:%S+01:00'
    time_now = datetime.datetime.now() + datetime.timedelta(hours=1)

    print(time_now)
    schedule = requests.get(url + '/schedule/schedule_linear.json')
    aktueller_sendeplan = schedule.json()

    for i in aktueller_sendeplan['schedule']:
        if time_now > datetime.datetime.strptime(i['timeStart'], format) and time_now < datetime.datetime.strptime(i['timeEnd'], format):
            print(i['title'])
            title = i['title']
            topic = i['topic']

    speech_text = "Jetzt läuft {} {}".format(title, topic)
    return statement(speech_text).simple_card('Now', speech_text)

@ask.intent('ScheduleAfterIntent')
def after(title="", topic=""):
    format = '%Y-%m-%dT%H:%M:%S+01:00'
    time_now = datetime.datetime.now() + datetime.timedelta(hours=1)

    schedule = requests.get(url + '/schedule/schedule_linear.json')
    aktueller_sendeplan = schedule.json()

    for i in aktueller_sendeplan['schedule']:
        if time_now < datetime.datetime.strptime(i['timeStart'], format):
            title = i['title']
            topic = i['topic']
            break

    speech_text = "Danach laeuft {} {}".format(title, topic)
    return statement(speech_text).simple_card('Now', speech_text)

@ask.intent('SchedulePrimeTimeIntent')
def prime_time(title="", topic=""):
    format = '%Y-%m-%dT%H:%M:%S+01:00'
    time_now = datetime.datetime.now() + datetime.timedelta(hours=1)
    prime_time = time_now.replace(hour=20, minute=13)

    schedule = requests.get(url + '/schedule/schedule_linear.json')
    aktueller_sendeplan = schedule.json()

    for i in aktueller_sendeplan['schedule']:
        if prime_time >= datetime.datetime.strptime(i['timeStart'], format):
            continue
        else:
            title = i['title']
            topic = i['topic']
            break

    speech_text = "Zur Prime Time läuft heute {} {}".format(title, topic)
    return statement(speech_text).simple_card('Now', speech_text)

@ask.intent('ScheduleLiveIntent')
def live():
    title = []
    format = '%Y-%m-%dT%H:%M:%S+01:00'
    time_now = datetime.datetime.now() + datetime.timedelta(hours=1)
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)

    schedule = requests.get(url + '/schedule/schedule_linear.json')
    aktueller_sendeplan = schedule.json()

    for i in aktueller_sendeplan['schedule']:

        time_start_datetime = i['timeStart'].split("+")
        time_start_date = i['timeStart'].split("T")
        time_of_day = i['timeStart'].split("T")
        time_of_day = time_of_day[1].split("+")
        time_of_day = time_of_day[0]
        time_of_day = time_of_day[:-3]

        start_datetime = datetime.datetime.strptime(time_start_datetime[0], "%Y-%m-%dT%H:%M:%S")
        start_date = datetime.datetime.strptime(time_start_date[0], '%Y-%m-%d').date()

        if start_datetime >= time_now and tomorrow > start_date and i['type'] == "live":
            title.append("um {} kommt {} {}".format(time_of_day,i['title'], i['topic']))

    if len(title) == 0:
        speech_text = "Heute sind keine Formate LIVE"
        return statement(speech_text).simple_card('Now', speech_text)

    speech_text = "Folgende Formate sind heute LIVE: {}".format(", ".join(title))
    return statement(speech_text).simple_card('Now', speech_text)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
    app.run
