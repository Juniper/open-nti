#Some script helped to build setup.

tc qdisc add dev eth0 root netem delay 100ms
route add -net 10.255.8.0/24 gw 150.1.1.2 dev eth0

tc qdisc add dev ens17f1 root netem delay 100ms
route add -net 10.255.8.0/24 gw 150.1.9.1 dev ens17f1

tc qdisc add dev ens17f0 root netem delay 100ms
route add -net 1.100.0.0/24 gw 23.1.1.1 dev ens17f0

#gvision server
tc qdisc add dev eth2 root netem delay 100ms
route add -net 1.100.0.0/24 gw 1.0.0.37 dev eth2


#Install influxdb:
curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
source /etc/lsb-release
echo "deb https://repos.influxdata.com/${DISTRIB_ID,,} ${DISTRIB_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/influxdb.list

sudo apt-get update && sudo apt-get install influxdb
sudo systemctl start influxdb

#Install Grafana

wget https://s3-us-west-2.amazonaws.com/grafana-releases/release/grafana_4.4.3_amd64.deb
sudo apt-get install -y adduser libfontconfig
sudo dpkg -i grafana_4.4.3_amd64.deb

systemctl daemon-reload
systemctl start grafana-server
systemctl status grafana-server
sudo systemctl enable grafana-server.service

Or:
sudo service grafana-server start
sudo update-rc.d grafana-server defaults

L1 switch in lab:
    
    
regress@ttsv-shell07 smanik]$ pswitch -l tinybud xe-19/0/23 yangtze ens17f0 
Configuring Interfaces... 
Runtime Error: yangtze:ens17f0 does not exist 
[regress@ttsv-shell07 smanik]$ pi yangtze 
pi: Command not found. 
[regress@ttsv-shell07 smanik]$ params-info yangtze 
Current information on yangtze: 
  Manufacturer..................iXSystems 
  Model.........................ix-22x4 
  Testbed.......................global 
  Host yangtze:Unknown 
    Osname......................linux 
    Ip..........................10.94.8.24/25 
    Ipv6........................abcd::10:94:8:24 
 eth0 

ELK:
https://www.digitalocean.com/community/tutorials/how-to-centralize-logs-with-rsyslog-logstash-and-elasticsearch-on-ubuntu-14-04
https://www.howtoforge.com/tutorial/how-to-install-elastic-stack-on-ubuntu-16-04/
https://discuss.elastic.co/t/how-to-remove-old-indices-and-old-logs-after-specific-duration/79220
https://www.elastic.co/guide/en/elasticsearch/reference/5.6/installing-xpack-es.html#xpack-package-installation

logstash.conf
root@ubuntu16lts:/etc/logstash/conf.d# cat backup.logstash.conf 
input {
  udp {
    port => 5443
    codec => "json"
    type => "rsyslog"
  }
}

filter {
}

output {
  elasticsearch { 
    hosts => "localhost:9200"
    index => "pdt"
  }
}

rsyslog:
hfzhang@moon:/etc/rsyslog.d$ cat 01-json-template.conf 
template(name="json-template"
  type="list") {
    constant(value="{")
      constant(value="\"@timestamp\":\"")     property(name="timereported" dateFormat="rfc3339")
      constant(value="\",\"@version\":\"1")
      constant(value="\",\"message\":\"")     property(name="msg" format="json")
      constant(value="\",\"sysloghost\":\"")  property(name="hostname")
      constant(value="\",\"severity\":\"")    property(name="syslogseverity-text")
      constant(value="\",\"facility\":\"")    property(name="syslogfacility-text")
      constant(value="\",\"daemon\":\"") property(name="programname")
      constant(value="\",\"procid\":\"")      property(name="procid")
    constant(value="\"}\n")
}

hfzhang@moon:/etc/rsyslog.d$ cat 60-output.conf 
*.*                         @192.168.60.205:5443;json-template




        extension-service {
            request-response {
                grpc {
                    ssl {
                        port 10162;
                        local-certificate lcert;
                        mutual-authentication {
                            certificate-authority ca1;
                            client-certificate-request require-certificate-and-verify;
                        }
                    }
                    max-connections 8;
                }
            }
        }
        
        
        
sfcapd: sflow server
apt-get install gnome-panel gnome-settings-daemon metacity nautilus gnome-terminal
apt install xserver-xorg-core
apt-get install xorg
 Xvnc :5 -desktop glo-shell5:5 -geometry 1524x900 -depth 16 -rfbauth /root/.vnc/passwd 
 
Xvnc :5 -desktop glo-shell5:5 -geometry 1524x900 -depth 16 -rfbauth /root/.vnc/passwd 


$ sudo apt-get install snmp-mibs-downloader
Just remember the text on /etc/snmp/snmp.conf. You have to comment out the mibs : line! Now everything is by the book. Enjoy!

