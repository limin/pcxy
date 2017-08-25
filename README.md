# pcxy

Pcxy is a simple parental control proxy to help safeguard your kids while online.

With Pcxy, you can block inappropriate and dangerous sites, restrict access by time and category, and log internet visits.

## Installation

I run it on my old pc with ubuntu 15.10.

```
sudo apt-get update
sudo apt-get install python3-pip
pip3 install croniter
pip3 install pyyaml
pip3 install BeautifulSoup4
sudo mkdir /var/log/pcxy
cd /opt/
sudo git clone https://github.com/limin/pcxy.git
sudo python3 proxy_server.py
```

