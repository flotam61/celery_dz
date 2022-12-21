import time
import requests

HOST = "http://127.0.0.1:5000/comparison"

img_1 = open('lama_300px.png', 'rb')


task_id = requests.post(HOST, files={'image_1': img_1}).json()['task_id']


status = 'PENDING'
result = None

while status == 'PENDING':
    response = requests.get(f'{HOST}/{task_id}').json()
    time.sleep(3)
    print(response)
    status = response['status']
    result = response['result']

print(result)

img_1.close()
