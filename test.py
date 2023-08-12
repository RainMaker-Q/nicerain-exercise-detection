#!/usr/bin/python3

import RPi.GPIO as GPIO
import time

# 设置led 或者蜂鸣器的引脚
# led 是21  蜂鸣器是20
LED_PIN = 20

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)
blinks = 0
print('开始闪烁')
while (blinks < 10):
    GPIO.output(LED_PIN, GPIO.HIGH)
    time.sleep(1.0)
    GPIO.output(LED_PIN, GPIO.LOW)
    time.sleep(1.0)
    blinks = blinks + 1
GPIO.output(LED_PIN, GPIO.LOW)
GPIO.cleanup()
print('结束闪烁')
