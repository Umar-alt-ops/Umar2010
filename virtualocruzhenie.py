'''Виртуальное окружение(виртуальная среда) - это изолированная среда для Python проектов, которая позволяет 
управлять зависимостями и пакетами отдельно для каждого проекта. 
Это особенно полезно, когда у вас есть несколько проектов, требующих разных версий библиотек или пакетов.'''

# python -m venv venv
# venv\Scripts\activate

from datetime import datetime
print(datetime.now())

import math 
print(math.sqrt(16))

import random
print(random.randint(1, 10))

import os 
print(os.getcwd())

import json

data = {'name': 'Aliya', 'age': 16}
text = json.dumps(data, ensure_ascii=False)
print(type(text))
