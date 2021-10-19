ifconfig et-0/0/1   down
ifconfig et-0/0/3  down
ifconfig et-0/0/4  down
ifconfig et-0/0/5  down
ifconfig et-0/1/0  down
ifconfig et-0/1/1  down
ifconfig et-0/1/3  down
ifconfig et-0/1/4  down
ifconfig et-2/0/9:0 down
ifconfig et-2/0/9:1 down
ifconfig et-2/0/9:2 down
ifconfig et-2/0/10:1 down
ifconfig et-2/0/10:2 down
ifconfig et-3/0/0  down
ifconfig et-3/0/1  down
ifconfig et-3/0/2  down
ifconfig et-4/0/15  down
ifconfig et-4/0/17  down
ifconfig et-4/0/18:0 down
ifconfig et-4/0/18:1 down
ifconfig ae0.0 down
ifconfig ae1.0 down
ifconfig ae2.0 down
ifconfig ae3.0 down
ifconfig ae4.0 down
 
sleep 1
 
ifconfig et-0/0/1   up
ifconfig et-0/0/3  up
ifconfig et-0/0/4  up
ifconfig et-0/0/5  up
ifconfig et-0/1/0  up
ifconfig et-0/1/1  up
ifconfig et-0/1/3  up
ifconfig et-0/1/4  up
ifconfig et-2/0/9:0 up
ifconfig et-2/0/9:1 up
ifconfig et-2/0/9:2 up
ifconfig et-2/0/10:1 up
ifconfig et-2/0/10:2 up
ifconfig et-3/0/0  up
ifconfig et-3/0/1  up
ifconfig et-3/0/2  up
ifconfig et-4/0/15  up
ifconfig et-4/0/17  up
ifconfig et-4/0/18:0 up
ifconfig et-4/0/18:1 up
ifconfig ae0.0 up
ifconfig ae1.0 up
ifconfig ae2.0 up
ifconfig ae3.0 up
ifconfig ae4.0 up
 
sleep 300
 
cli -c "clear bgp neighbor all"
sleep 300
 
 
cli -c "clear interfaces statistics all"
cli -c "clear firewall all"
sleep 300
 
cli -c "configure; set interfaces et-0/0/3 disable; deactivate interfaces ae9; deactivate snmp; commit and-quit"
sleep 300
 
cli -c "configure; rollback 1; commit"
 
sleep 300
 
cli -c "clear isis adjacency all"
sleep 300

ifconfig et-0/0/1   down
ifconfig et-0/0/3  down
ifconfig et-0/0/4  down
ifconfig et-0/0/5  down
ifconfig et-0/1/0  down
ifconfig et-0/1/1  down
ifconfig et-0/1/3  down
ifconfig et-0/1/4  down
ifconfig et-2/0/9:0 down
ifconfig et-2/0/9:1 down
ifconfig et-2/0/9:2 down
ifconfig et-2/0/10:1 down
ifconfig et-2/0/10:2 down
ifconfig et-3/0/0  down
ifconfig et-3/0/1  down
ifconfig et-3/0/2  down
ifconfig et-4/0/15  down
ifconfig et-4/0/17  down
ifconfig et-4/0/18:0 down
ifconfig et-4/0/18:1 down
ifconfig ae0.0 down
ifconfig ae1.0 down
ifconfig ae2.0 down
ifconfig ae3.0 down
ifconfig ae4.0 down
 
sleep 1
 
ifconfig et-0/0/1   up
ifconfig et-0/0/3  up
ifconfig et-0/0/4  up
ifconfig et-0/0/5  up
ifconfig et-0/1/0  up
ifconfig et-0/1/1  up
ifconfig et-0/1/3  up
ifconfig et-0/1/4  up
ifconfig et-2/0/9:0 up
ifconfig et-2/0/9:1 up
ifconfig et-2/0/9:2 up
ifconfig et-2/0/10:1 up
ifconfig et-2/0/10:2 up
ifconfig et-3/0/0  up
ifconfig et-3/0/1  up
ifconfig et-3/0/2  up
ifconfig et-4/0/15  up
ifconfig et-4/0/17  up
ifconfig et-4/0/18:0 up
ifconfig et-4/0/18:1 up
ifconfig ae0.0 up
ifconfig ae1.0 up
ifconfig ae2.0 up
ifconfig ae3.0 up
ifconfig ae4.0 up
 
sleep 300
 
cli -c "clear bgp neighbor all"
sleep 300
 
 
cli -c "clear interfaces statistics all"
cli -c "clear firewall all"
sleep 300
 
cli -c "configure; set interfaces et-0/0/3 disable; deactivate interfaces ae9; deactivate snmp; commit and-quit"
sleep 300
 
cli -c "configure; rollback 1; commit"
 
sleep 300
 
cli -c "clear isis adjacency all"
sleep 300