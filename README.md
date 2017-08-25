# pcxy

Pcxy is a simple parental control proxy to help safeguard your kids while online. It supports both http and https requests.

With Pcxy, you can block inappropriate and dangerous sites, restrict access by time and category, and log internet visits.

## Installation

I run it on my old pc with ubuntu 15.10.

```shell
sudo apt-get update
sudo apt-get install python3-pip
pip3 install croniter
pip3 install pyyaml
pip3 install BeautifulSoup4
sudo mkdir /var/log/pcxy
cd /opt/
sudo git clone https://github.com/limin/pcxy.git
cd pcxy
sudo python3 proxy_server.py
```

## Config access rules

The access rules are defined in the rule.yaml file. e.g.

```yaml
denies:
    - cron_date: 0 0 * * *
      start_time: '00:00'
      end_time: '23:59'
      tags: ['Academic Fraud','Adult Themes','Advertising','Alcohol','Dating','Drugs','Gambling','Hacking','Hate/Discrimination','Illegal Activities','Illegal Downloads','Lingerie/Bikini','Lotteries','Military','Nudity','Online Meetings','Online Trading','Pornography','Proxy/Anonymizer','Religious','Sex Education','Sexuality','Tasteless','Weapons','Web Spam']

allows:
    - cron_date: 0 0 * * *
      start_time: '06:00'
      end_time: '22:00'
      tags: ['News/Media','Content Delivery Networks','Blogs','Non-Profits','Forums/Message boards','Politics','Business Services','Portals','Ecommerce/Shopping','Educational Institutions','Research/Reference','Search Engines','Financial Institutions','Software/Technology','Government','Sports','Health and Fitness','Travel','URL Shortener','Visual Search Engines','Webmail','File Storage','Chat','Certificate Verification']

    - cron_date: 0 0 * * * 1,2,3,4,5
      start_time: '13:00'
      end_time: '16:00'
      tags: ['Photo Sharing','Movies','Social Networking','Video Sharing','Instant Messaging','Games']

    - cron_date: 0 0 * * * 1,2,3,4,7
      start_time: '20:00'
      end_time: '21:30'
      tags: ['Photo Sharing','Movies','Social Networking','Video Sharing','Instant Messaging','Games']

```

## Internet visits log

Two files are generated to record internet visits. 
- /var/log/pcxy/access.log
- /var/log/pcxy/access.csv

### access.log

It's a log file with common log format. e.g.

```
192.168.1.228 - - 2017-08-20 17:01:06,031 "CONNECT www.youtube.com:443 HTTP/1.1" - - "" " Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:54.0) Gecko/20100101 Firefox/54.0"
192.168.1.228 - - 2017-08-20 17:01:07,480 "GET http://img1.gtimg.com/fashion/pics/hv1/140/60/2232/145151240.jpg HTTP/1.1" - - " http://www.qq.com/" " Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:54.0) Gecko/20100101 Firefox/54.0"
```

### access.csv

It's a csv file with the columns of client_ip,time,method,host,request_uri,http_version,message,Referer
and User-Agent.

```
192.168.1.228,2017-08-20 17:01:06,032,CONNECT,www.youtube.com,"www.youtube.com:443",HTTP/1.1,allowed,""," Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:54.0) Gecko/20100101 Firefox/54.0"
192.168.1.228,2017-08-20 17:01:07,481,GET,img1.gtimg.com,"http://img1.gtimg.com/fashion/pics/hv1/140/60/2232/145151240.jpg",HTTP/1.1,allowed," http://www.qq.com/"," Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:54.0) Gecko/20100101 Firefox/54.0"
```
