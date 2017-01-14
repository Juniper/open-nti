#! /bin/sh

trap 'shutdown_runit_services' INT TERM

shutdown_runit_services() {
   #need to check if runit service is runnung before shutdown ..
   echo "Begin shutting down runit services..."
   /sbin/sv down /etc/service/*
   #need to give some time and check if service is down if time greater than allow them force exit
   count=1
   while [ $(/sbin/sv status /etc/service/* | grep -c "^run:") != 0 ]
   do
     sleep 1
     count=`expr $count + 1`
     if [ $count -gt 10 ]; then break ; fi
   done
   exit 0
}

exec env /sbin/runsvdir -P /etc/service
echo "Booting runit daemon..."
exec env /sbin/runsvdir -P /etc/service 'log:.........................................................................................................' &
runsvdir_PID=$!
echo "Process runsvdir running with PID $runsvdir_PID"
