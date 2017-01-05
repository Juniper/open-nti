worker_processes auto;

events {
  worker_connections  1024;
}

stream {
  #######################
  ## Event / Syslog
  #######################
  upstream udp_6000 {
    {{range service "input-syslog"}}
      server {{.Address}}:{{.Port}};{{end}}
  }

  server {
    listen 6000 udp;
    proxy_pass udp_6000;
    proxy_timeout 1s;
    proxy_responses 1;
    error_log dns.log;
  }

  #######################
  ## JTI
  #######################
  upstream udp_50000 {
    {{range service "input-jti-50000"}}
      server {{.Address}}:{{.Port}};{{end}}
  }

  server {
    listen 50000 udp;
    proxy_pass udp_50000;
    proxy_timeout 1s;
    proxy_responses 1;
    error_log dns.log;
  }

  #######################
  ## JTI Analyticsd
  #######################
  upstream udp_50020 {
    {{range service "input-jti-50020"}}
      server {{.Address}}:{{.Port}};{{end}}
  }

  server {
    listen 50020 udp;
    proxy_pass udp_50020;
    proxy_timeout 1s;
    proxy_responses 1;
    error_log dns.log;
  }
}
