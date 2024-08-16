import time
from zoneinfo import ZoneInfo
from datetime import datetime

timestemp = time.time()

print(str(timestemp).split('.')[0])

# obter a data e hora em um timezone específico
d = datetime.fromtimestamp(int(str(timestemp).split('.')[0]), tz=ZoneInfo('America/Sao_Paulo'))
print(d)  # 2019-04-26 20:53:54.483200-03:00