#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import requests
from flask import Flask, render_template
from flask_ask import Ask, statement, session, request, question
import datetime

app = Flask(__name__)
ask = Ask(app, '/')

logging.getLogger('flask_ask').setLevel(logging.DEBUG)

url = 'http://api.rbtv.rodney.io/api/1.0'

@ask.launch
def launch():
    speech_text = "Willkommen zum inoffiziellen Rocket Beans Skill. Mit diesem Skill kannst du das Programm von Rocket Beans TV abfragen"
    help_text = "Frage mich zum Beispiel was läuft gerade oder was kommt danach"
    return question(speech_text).reprompt(help_text).simple_card('Welcome', speech_text)

@ask.intent('ScheduleNowIntent')
def now(title="", topic="", timeEnd=""):
    format = '%Y-%m-%dT%H:%M:%S+01:00'
    time_now = datetime.datetime.now() + datetime.timedelta(hours=1)

    schedule = requests.get(url + '/schedule/schedule_linear.json')
    aktueller_sendeplan = schedule.json()

    for i in aktueller_sendeplan['schedule']:
        if time_now > datetime.datetime.strptime(i['timeStart'], format) and time_now < datetime.datetime.strptime(i['timeEnd'], format):
            title = i['title']
            topic = i['topic']
            timeEnd = datetime.datetime.strptime(i['timeEnd'], format)
            break

    speech_text = "Jetzt läuft {} {} bis {}:{:02d} Uhr".format(
        title.encode('utf-8'),
        topic.encode('utf-8'),
        timeEnd.hour,
        timeEnd.minute).replace("&", "und")
    return statement(speech_text).simple_card('Now', speech_text)

@ask.intent('ScheduleAfterIntent')
def after(title="", topic="", timeEnd=""):
    format = '%Y-%m-%dT%H:%M:%S+01:00'
    time_now = datetime.datetime.now() + datetime.timedelta(hours=1)

    schedule = requests.get(url + '/schedule/schedule_linear.json')
    aktueller_sendeplan = schedule.json()

    for i in aktueller_sendeplan['schedule']:
        if time_now < datetime.datetime.strptime(i['timeStart'], format):
            title = i['title']
            topic = i['topic']
            timeEnd = datetime.datetime.strptime(i['timeEnd'], format)
            break

    speech_text = "Danach laeuft {} {} bis {}:{:02d} Uhr".format(
        title.encode('utf-8'),
        topic.encode('utf-8'),
        timeEnd.hour,
        timeEnd.minute).replace("&", "und")
    return statement(speech_text).simple_card('Now', speech_text)

@ask.intent('SchedulePrimeTimeIntent')
def prime_time(title="", topic="", timeEnd="", after_title="", after_topic="", after_timeEnd=""):
    format = '%Y-%m-%dT%H:%M:%S+01:00'
    time_now = datetime.datetime.now() + datetime.timedelta(hours=1)
    prime_time = time_now.replace(hour=19, minute=59)
    schedule = requests.get(url + '/schedule/schedule_linear.json')
    aktueller_sendeplan = schedule.json()

    for counter, i in enumerate(aktueller_sendeplan['schedule']):
        if prime_time >= datetime.datetime.strptime(i['timeStart'], format):
            continue
        else:
            title = i['title']
            topic = i['topic']
            timeEnd = datetime.datetime.strptime(i['timeEnd'], format)
            after_title = aktueller_sendeplan['schedule'][counter + 1]['title']
            after_topic= aktueller_sendeplan['schedule'][counter +1]['topic']
            after_timeEnd = datetime.datetime.strptime(aktueller_sendeplan['schedule'][counter +1]['timeEnd'], format)
            break

    speech_text = "Zur Prime Time läuft heute {} {}, bis {}:{:02d} Uhr. Und danach kommt {} {}, bis {}:{:02d} Uhr".format(
        title.encode('utf-8'),
        topic.encode('utf-8'),
        timeEnd.hour,
        timeEnd.minute,
        after_title.encode('utf-8'),
        after_topic.encode('utf-8'),
        after_timeEnd.hour,
        after_timeEnd.minute).replace("&", "und")
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

        start_datetime = i['timeStart']
        start = datetime.datetime.strptime(start_datetime, format)

        if start >= time_now and tomorrow > start.date() and i['type'] == "live":
            title.append("um {} kommt {} {}".format(time_of_day,
                i['title'].encode('utf-8'),
                i['topic'].encode('utf-8')).replace("&", "und"))

    if len(title) == 0:
        speech_text = "Heute sind keine Formate LIVE"
        return statement(speech_text).simple_card('Now', speech_text)

    speech_text = "Folgende Formate sind heute LIVE: {}".format(", ".join(title))
    return statement(speech_text).simple_card('Now', speech_text)

@ask.intent('AMAZON.HelpIntent')
def help():
    help_text = '''Folgende Dinge kannst du mich fragen:
        was läuft gerade,
        was kommt danach,
        was läuft heute zur prime time oder was ist heute live'''
    return question(help_text).reprompt(help_text)

@ask.intent('AMAZON.StopIntent')
def stop():
    stop_text = ""
    return statement(stop_text)

@ask.intent('AMAZON.CancelIntent')
def cancel():
    cancel_text = ""
    return statement(cancel_text)

@ask.session_ended
def session_ended():
    return "", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
