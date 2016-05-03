#!/usr/bin/env python
# -*- coding: utf-8 -*-


import speech_recognition as sr
import os
import time
import sys
import urllib2
from lxml import etree

# get weather from yandex
def get_yandex_weather(city_id):
    try:
        data = ""
        count = 1
        say("Получаю погодные данные. Это может занять некоторое время.")
        while len(data) == 0:
            try:
                data = urllib2.urlopen("http://export.yandex.ru/weather-ng/forecasts/" + city_id + ".xml").read()
            except Exception:
                print count
            count += 1
            if count == 41:
                break
            time.sleep(0.3)
        #print data
        root = etree.fromstring(data)
        say("Текущая температура " + root[0][4].text + " градусов")
        say(root[0][9].text.encode('utf-8'))
        say("Скорость ветра " + root[0][16].text + " метров в секунду")
    except Exception as inst:
        print inst
        say("Не удалось получить погодные данные")

# says string text
def say(text):
    p = sys.platform
    if p == "darwin":
        os.popen("say -v Yuri -r 2000 " + text)
    if p == "win32":
        os.popen("cscript say.vbs " + text)

# get answer on question by words
def get_answer(words):
    say("Подождите секунду сэр")
    is_answer = False
    print words
    if u"стоп" in words :
        global stop_flag
        stop_flag = True
        is_answer = True
        say("Сэр я пошел спать")
    if u"привет" in words :
        is_answer = True
        say("Здравствуйте сэр")
    if u"погода" in words or u"погоду" in words or u"погоде" in words :
        get_yandex_weather("34560")
        is_answer = True
    if not is_answer:
        say("Извините сэр команда не распознана")

# this is called from the background thread
def callback(recognizer, audio):
    # if already answerning then interrupt
    global is_answerning
    if is_answerning:
        return
    is_answerning = True
    res = u''
    print "Get question"
    # received audio data, now we'll recognize it using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        res = r.recognize_google(audio, language='ru-RU', key='AIzaSyAw0SEnqBMx1jkYIA3TNu2Rvz_jVb61ee4')
        print("Google Speech Recognition thinks you said - " + res.encode('utf-8'))
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        is_answerning = False
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        is_answerning = False
    # Response processing
    resmas = res.split()
    resmas = map(lambda x: x.lower(), resmas)
    if u"джарвис" in resmas:
        get_answer(resmas)
    is_answerning = False
    return

# MAIN PROGRAM
r = sr.Recognizer()
m = sr.Microphone()
stop_flag = False
is_answerning = False

with m as source:
    r.adjust_for_ambient_noise(source) # we only need to calibrate once, before we start listening
# start listening in the background (note that we don't have to do this inside a `with` statement)
stop_listening = r.listen_in_background(m, callback)
print "Ready!"
# `stop_listening` is now a function that, when called, stops background listening
# do some other computation for 5 seconds, then stop listening and keep doing other computations
#for _ in range(50): time.sleep(0.1) # we're still listening even though the main thread is doing other things
while not stop_flag: 
    time.sleep(0.1)
stop_listening()
print "Good bye!"