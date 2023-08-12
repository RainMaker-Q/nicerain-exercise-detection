import RPi.GPIO as GPIO
import schedule
import time
import requests

# 超声波触发输出信号引脚
TRIGGER_PIN = 23
# 超声波接受信号引脚
ECHO_PIN = 24
# 声音在空气中的传播速度
SPEED_IN_AIR = 34300
# 触发信号的最小时长
TRIGGER_GAP = 0.00001

# led 是21  蜂鸣器是20
LED_PIN = 21
BEEP_PIN = 20

A_BIG_NUMBER = 1000
# normalDistance = 5
count = 0
countInAday = 0


def getDistance():
    # 设置GPIO模式为BCM
    GPIO.setmode(GPIO.BCM)

    # 设置触发引脚为输出，回波引脚为输入
    GPIO.setup(TRIGGER_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)

    # 发送触发信号
    GPIO.output(TRIGGER_PIN, True)
    time.sleep(TRIGGER_GAP)
    GPIO.output(TRIGGER_PIN, False)

    # 等待接收回波
    startTime = time.time()
    endTime = time.time()
    startTimeStatic = time.time()
    while GPIO.input(ECHO_PIN) == 0:
        startTime = time.time()
        if (startTime - startTimeStatic > 1):
            return A_BIG_NUMBER
    while GPIO.input(ECHO_PIN) == 1:
        endTime = time.time()
        if (endTime - startTime > 1):
            return A_BIG_NUMBER

    # 计算距离
    duration = endTime - startTime
    distance = duration * SPEED_IN_AIR / 2

    # 清理GPIO设置
    GPIO.cleanup()

    return distance


def detection():
    global count
    array = []
    normalCount = 0
    normalSignal = False
    triggerCount = 0
    triggerSignal = False
    lastTriggerTime = time.time()

    beepedDistance = []

    try:
        while True:
            distance = getDistance()
            # value = "{:.2f}".format(distance)
            # print("当前测距为: ", value)
            # array.append(value)

            # 过滤脏数据
            if (distance > 8 or distance < 4):
                continue

            if (distance > 6.1):
                normalCount = normalCount + 1
                # 清除出现小的噪声
                triggerCount = 0
                # 大于阈值出现3次
                if (normalCount > 3):
                    normalSignal = True
                    normalCount = 0

                # GPIO.setmode(GPIO.BCM)
                # GPIO.setup(LED_PIN, GPIO.OUT)
                # GPIO.output(LED_PIN, GPIO.LOW)
            # else:
                # GPIO.setmode(GPIO.BCM)
                # GPIO.setup(LED_PIN, GPIO.OUT)
                # GPIO.output(LED_PIN, GPIO.HIGH)

            if (distance < 4.8):
                triggerCount = triggerCount + 1
                # 大于阈值出现2次
                if (triggerCount > 1):
                    triggerCount = 0
                    triggerSignal = True

            if (normalSignal and triggerSignal):
                normalSignal = False
                triggerSignal = False
                # 两次触发之间间隔至少300ms  否则就作废
                if (time.time() - lastTriggerTime > 0.55):
                    count = count + 1
                    lastTriggerTime = time.time()
                    GPIO.setmode(GPIO.BCM)
                    GPIO.setup(BEEP_PIN, GPIO.OUT)
                    GPIO.output(BEEP_PIN, GPIO.HIGH)
                    # beepedDistance.append(value)

            time.sleep(0.02)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(BEEP_PIN, GPIO.OUT)
            GPIO.output(BEEP_PIN, GPIO.LOW)
            schedule.run_pending()

    except KeyboardInterrupt:
        print(array)
        file = open("data.txt", "w")
        file.write("[" + ", ".join(array) + "]")
        file = open("realTragger.txt", "w")
        file.write("[" + ", ".join(beepedDistance) + "]")
        print("仓鼠一共跑了 ", count, "圈")
        GPIO.cleanup()


def writeRecord():
    global count
    global countInAday
    now = time.localtime()
    file = open("result.txt", "a")
    file.write("好雨在" + str(now.tm_mon) + "月" + str(now.tm_mday) +
               "日" + str(now.tm_hour) + "时 跑了" + str(count) + "圈 \n")
    print("count is ", count)
    countInAday = countInAday + count
    count = 0
    if (now.tm_hour == 23):
        # 发送请求
        requests.post(url='http://192.168.0.109:3000/nicerain',
                      headers={"Content-Type": "application/json"}, json={"turns": countInAday})
        file.write("好雨在" + str(now.tm_mon) + "月" + str(now.tm_mday) +
                   "日 跑了" + str(countInAday) + "圈 \n")
        countInAday = 0


if __name__ == "__main__":
    schedule.every().hour.at(":59").do(writeRecord)
    # schedule.every().minute.at(":00").do(writeRecord)
    detection()
