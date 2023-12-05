import redis

db = redis.StrictRedis(host='localhost', port=6379, db=0)

db.set('key1', 'value1')

value1 = db.get('key1').decode()
print(value1)