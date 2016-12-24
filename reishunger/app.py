#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from flask import Flask, render_template
from flask_ask import Ask, statement

app = Flask(__name__)
ask = Ask(app, '/')

logging.getLogger('flask_ask').setLevel(logging.DEBUG)

Rice = {}
Rice["basmati reis"] = 1.5
Rice["basmati"] = 1.5
Rice["vollkorn basmati reis"] = 2.5
Rice["vollkorn basmati"] = 2.5
Rice["sushi reis"] = 2.5
Rice["risotto reis"] = 3
Rice["risotto"] = 3
Rice["sadri reis"] = 1.5
Rice["jasmin reis"] = 1.5
Rice["jasmin"] = 1.5
Rice["vollkorn jasmin reis"] = 2.5
Rice["vollkorn jasmin"] = 2.5
Rice["milch reis"] = 5
Rice["natur reis"] = 2
Rice["paella reis"] = 3
Rice["paella"] = 3
Rice["roter reis"] = 2.5
Rice["roten reis"] = 2.5
Rice["kleb reis"] = 1.5
Rice["schwarzer reis"] = 2.5
Rice["schwarzen reis"] = 2.5
Rice["lila reis"] = 2.5
Rice["quinoa"] = 2

@ask.launch
def launch():
    speech_text = "Willkommen bei Reishunger"
    return statement(speech_text).simple_card("Initial", speech_text)

@ask.intent('ReisHungerIntent')
def get_water(WEIGHT, TYPE_OF_UNIT, TYPE_OF_RICE):
    try:
        Rice[TYPE_OF_RICE]
    except KeyError:
        speech_text = "Ich finde die Reissorte {} nicht".format(TYPE_OF_RICE)
        return statement(speech_text).simple_card('RICE_NOT_FOUND', speech_text)
    water = int(WEIGHT) * Rice[TYPE_OF_RICE]
    if TYPE_OF_UNIT == "gramm":
        speech_text = "Du benötigst {} Milliliter Wasser".format(int(water))
        return statement(speech_text).simple_card('RICE_FOUND', speech_text)
    elif TYPE_OF_UNIT == "kilogramm":
        speech_text = "Du benötigst {} Liter Wasser".format(int(water))
        return statement(speech_text).simple_card('RICE_FOUND', speech_text)
    else:
        speech_text = "Diese Einheit verstehe ich nicht, bitte benutze Kilogramm\
        oder Gramm"
        return statement(speech_text).simple_card('UNIT_NOT_FOUND', speech_text)

if __name__ == '__main__':
    app.run(debug=False)
