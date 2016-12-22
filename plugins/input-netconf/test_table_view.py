import yaml
from jnpr.junos import Device
from jnpr.junos.factory.factory_loader import FactoryLoader
from pprint import pprint

# Set device information with IP-address, login user and passwort
dev = Device(host="192.168.194.128", user="root", password="Juniper", gather_facts=False)

# Open connection to the device
dev.open()

# Instead of loading a YAML-file place it within the code
yml = '''
---
bgpSummaryRoutes:
  # rpc: get-route-summary-information
  item: //route-summary-information/route-table
  key: table-name
  view: bgpSummaryView

bgpSummaryView:
  fields:
    table: table-name
    total_route_count: total-route-count
    active_route_count: active-route-count
    holddown_route_count: holddown-route-count
    hidden_route_count: hidden-route-count
    destination_count: destination-count
'''


dev.facts_refresh()
print dev.facts


bgp_summary = dev.rpc.cli('show bgp summary')

print "is type: {0}".format(type(bgp_summary))

# Load Table and View definitions via YAML into namespace
globals().update(FactoryLoader().load(yaml.load(yml)))

# Catching information from vMX1 through Table/View
bt = bgpSummaryRoutes(xml=bgp_summary).view
# Print all the information received from device

# print pprint(bt)

print("---------------------------------------------")
print("-----------------BGP Routes------------------")
print("---------------------------------------------")
print bt.to_json()
# for item in bt:
#     print item.to_json
    # print("Route: "+item.table_name+"/"+item.total_route_count)
print("---------------------------------------------")
