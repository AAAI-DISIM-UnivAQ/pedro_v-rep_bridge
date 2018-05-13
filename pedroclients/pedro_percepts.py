"""Bridge Redis-->PEDRO """

from pedroclient import *
from redis import Redis

PEDRO_AI = 'server'
Red = Redis()

def keepalive():
    Red.set('PEDRO', 'OK')
    Red.expire('PEDRO', 120)

print("Trying Pedro connection ... ")

try:
    me = PedroClient(async=True)
    print('OK')
except Exception as e:
    print('FAILED')
    print(e)
    exit()

keepalive()

print("Trying Pedro registration ... ")
if me.register('percepts'):
    print('OK')
else:
    print('FAILED')
    exit()

pubsub = Red.pubsub()
pubsub.subscribe('ROBOT:PERCEPTS')

print('sending percepts...')
while True:
    msg = pubsub.get_message(ignore_subscribe_messages=True)
    if msg:
        if me.p2p(PEDRO_AI+'@'+PEDRO_IP, msg['data']):
            pass
        else:
            print 'FAILED'
            exit()
exit()
