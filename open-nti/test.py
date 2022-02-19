from jnpr.junos import Device
from jnpr.junos.utils.start_shell import StartShell
import re

dev = Device(host='sup-tb4-geodc-2-brackla', user='regress', password='MaRtInI')

with StartShell(dev, timeout=60) as ss:
    result = ss.run('top -b -n 1')
    print result[-1]
    regex = '\s*[0-9]+\s+\w+\s+\d+\s+\d+\s+\d*\S*\s+(\d*\S*)\s+(\d*\S*)\s+\S+\s+(\S+)\s+\S+\s+\S+\s+EvoAftMan'

    text_matches = re.search(regex,result[-1],re.MULTILINE)
    print(text_matches.lastindex)

    for i in text_matches.groups():
        print(i)

