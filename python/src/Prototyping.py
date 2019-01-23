#!/usr/bin/env python3
#
# LOCAL:00:00:00.000
import time
import datetime

dt = datetime.datetime(100,1,1,0,0,0)
# %H:%M:%S:
for x in range(0,70):
    idt = dt + datetime.timedelta(minutes=x)
    header_local = "LOCAL:"+idt.strftime("%H:%M:%S.000")
    print(local)
