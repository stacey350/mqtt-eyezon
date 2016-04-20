from eyezon import Daemon as EyezonDaemon
from mqtt import Daemon as MqttDaemon
import queue, threading, time, sys

#main function
if __name__ == "__main__":

  commandQueue = queue.Queue()
  replyQueue = queue.Queue()

  eyezonDaemon = EyezonDaemon("192.168.1.3", 4025, commandQueue, replyQueue)
  eyezonDaemon.setDaemon(True)
  eyezonDaemon.start()

  mqttDaemon = MqttDaemon(commandQueue, replyQueue)
  mqttDaemon.setDaemon(True)
  mqttDaemon.start()

  while threading.active_count() > 0:
    time.sleep(0.1)
    if eyezonDaemon.isAlive() is not True or eyezonDaemon.isAlive() is not True:
      sys.exit()