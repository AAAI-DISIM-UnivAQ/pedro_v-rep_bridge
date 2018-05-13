"""Bridge PEDRO-->Redis """

from pedroclient import *
from redis import Redis

R = Redis()

def keepalive():
    R.set('PEDRO', 'OK')
    R.expire('PEDRO', 120)

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
if me.register('actions'):
    print('OK')
else:
    print('FAILED')
    exit()

print('receiving actions..')
while True:
    msg = me.get_term()[0]
    print(msg)
    R.publish('ROBOT', msg)

exit()
