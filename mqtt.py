import threading, queue, socket, configparser, re, paho.mqtt.client as mqtt


class Daemon(threading.Thread):
  def __init__(self, cmd_q=None, reply_q=None):
    threading.Thread.__init__(self)
    self.settings = configparser.ConfigParser()
    # self.settings.read('../config/site.ini')
    # self.rabbitmqUsername = self.settings.get('rabbitmq', 'username')
    # self.rabbitmqPassword = self.settings.get('rabbitmq', 'password')
    # self.rabbitmqHost = self.settings.get('rabbitmq', 'host')
    # self.conn = Connection('amqp://'+self.rabbitmqUsername+':'+self.rabbitmqPassword+'@'+self.rabbitmqHost+':5672//')
    # self.producer = Producer(self.conn.channel(), exchange = Exchange('eyezon.status', type='fanout'), serializer="json")
    # self.rpcProducer= Producer(self.conn.channel(), serializer="json")

    self.client = mqtt.Client()
    self.client.on_connect = self.on_connect
    self.client.on_message = self.on_message
    self.client.connect("localhost", 1883, 60)


    self.cmd_q = cmd_q or queue.Queue()
    self.reply_q = reply_q or queue.Queue()

    self.alarmCache = {
      "zoneTimerDump": None,
      "keypadUpdate": None,
      "zoneStateChange": None,
      "partitionStateChange": None,
      "realtimeCIDEvent": None,
      "zoneTimerDump": None
    }
  def on_connect(self, client, userdata, flags, rc):
    print("Successfully connected to mqtt broker "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("home/alarm/set")
  def on_message(self,client, userdata, msg):
    # print(msg.topic+" "+str(msg.payload))
    if msg.topic == "home/alarm/set":
      command = msg.payload.decode('utf-8')
      print("Forwarding alarm panel command "+command)
      self.cmd_q.put(command)
    else:
      print("Ignoring message on topic"+msg.topic)



  def publishEvent(self, event):
    if event['name'] == "Zone Timer Dump":
      self.alarmCache["zoneTimerDump"] = event
    elif event['name'] == "Virtual Keypad Update":
      payload = None
      # for now just dump out one of the canned status values
      if event['payload']['leds']['ARMED STAY'] == True:
        payload = "armed_home"
      elif event['payload']['leds']['READY'] == True:
        payload = "disarmed"
      elif event['payload']['leds']['ARMED AWAY'] == True:
        payload = "armed_away"
      elif event['payload']['leds']['ALARM (System is in Alarm)'] == True:
        payload = "triggered"

      if payload != None:
        print("Publishing "+payload)
        self.client.publish("home/alarm", payload=payload, qos=0, retain=True)


  def run(self):
    while 1:
      try:
        cmd = self.reply_q.get(True, 0.1)
        self.publishEvent(cmd)

      except queue.Empty as e:
        try:
          self.client.loop(timeout=0.1)
        except socket.timeout:
          None

#main function
if __name__ == "__main__":
  daemon = Daemon()
  daemon.setDaemon(True)
  daemon.start()
  while 1:
    None