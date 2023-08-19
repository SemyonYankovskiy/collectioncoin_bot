import ntplib
import time

client = ntplib.NTPClient()
response = client.request('pool.ntp.org')
local_time = time.localtime(response.tx_time)
formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', local_time)
print(formatted_time)