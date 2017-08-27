import socket
import threading
import signal
import sys
import fnmatch
import errno
import time
import pdb
import re
from time import gmtime, strftime, localtime
import logging
import config
import rule
import tag as tag_store

p=re.compile('(http:\/\/)?([\w\.-]*)(\:(\d*))?(\/.*)?')
thread_logger = logging.getLogger('thread')
access_logger = logging.getLogger('access')
csv_logger = logging.getLogger('csv')

def proxy(browser_conn, client_addr):
    def ishostAllowed(host):
        if host.split('.')[-1].isdigit():
            thread_logger.warn("Invalid host:".format(host),extra=req);            
            return False
        #pdb.set_trace()
        tags=tag_store.get(host)
        if not tags:
            thread_logger.warn("{0} isn't allowed: empty tags".format(host),extra=req);            
            return False
        for tag in tag_store.get(host):
            if not rule.isTagAllowed(tag):
                thread_logger.warn("{0}:{1} isn't allowed".format(host,tag),extra=req);
                return False
        return True

    def proxy_http(request):
        try:
            # create a socket to connect to the web server
            #pdb.set_trace()
            server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_conn.settimeout(config.connection_timeout)
            server_conn.connect((request['host'], request['port']))
            server_conn.sendall(request['raw_data'])                           # send request to webserver

            while 1:
                data = server_conn.recv(config.max_request_len)          # receive data from web server
                if (len(data) > 0):
                    browser_conn.send(data)                               # send to browser
                else:
                    break
        except socket.error as error_msg:
            thread_logger.error(str(error_msg)+":"+str(request),extra=req);
        finally:
            if server_conn:
                server_conn.close()
            if browser_conn:
                browser_conn.close()
            
        return
    
    def response(status,message):
        reply = "HTTP/1.0 {0} {1}\r\n"
        reply += "Proxy-agent: Pcxy\r\n"
        reply += "\r\n"
        reply = reply.format(status,message);
        #pdb.set_trace()
        browser_conn.sendall( reply.encode() )

    def proxy_https(request):
        #pdb.set_trace()
        try:
            server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # If successful, send 200 code response
            server_conn.connect((req['host'], req['port']))
            response(200,'Connection established')
        except socket.error as err:
        # If the connection could not be established, exit
        # Should properly handle the exit with http error code here
            thread_logger.error("Cannot establish https connection:"+err,extra=req);
            if server_conn:
                server_conn.close()
            if browser_conn:
                browser_conn.close()
            return

        # Indiscriminately forward bytes
        browser_conn.setblocking(0)
        server_conn.setblocking(0)

        timeout=time.time()+60 # 1 minute
        while timeout-time.time()>0:
            request_done=False
            replied_done=False
            try:
                    request =browser_conn.recv(config.max_request_len)           # receive data from browser
                    if (len(request) > 0):
                        server_conn.sendall(request)                               # send to web server
                    else:
                        request_done=True
                    #hread_logger.info("REQUEST len: " + str(len(request)),extra=req);
            except socket.error as e:
                    if e.errno==errno.EWOULDBLOCK:
                            time.sleep(0.1)
                            pass
                    else:
                            thread_logger.error("pipe error:"+str(e),extra=req);
                            break                        
            try:
                    reply = server_conn.recv(config.max_request_len)          # receive data from web server
                    if (len(reply) > 0):
                        browser_conn.sendall(reply)                               # send to browser
                    else:
                        replied_done=True
                    #thread_logger.info("reply len: " + str(len(reply)),extra=req);
            except socket.error as e:

                    if e.errno==errno.EWOULDBLOCK:
                            time.sleep(0.1)
                            pass
                    else:
                            thread_logger.error("pipe error:"+str(e),extra=req);
                            break  
            if request_done and replied_done:
                break

        server_conn.close()
        browser_conn.close()
       

    raw_data = browser_conn.recv(config.max_request_len)        # get the request from browser
    req={'raw_data':raw_data,
         'tname' : threading.currentThread().getName(),
         'client_ip' : client_addr[0],
         'client_port' : client_addr[1]
        }
    thread_logger.info("REQUEST: {0}".format(raw_data),extra=req);
    #pdb.set_trace()

    try:
        # request_line is the first one. https://www.w3.org/Protocols/rfc2616/rfc2616-sec5.html
        msg_body_pos=len(raw_data)
        for i in range(4,len(raw_data)):
            if raw_data[i-4:i].decode()=='\r\n\r\n':
                msg_body_pos=i
                break
        lines=raw_data[:msg_body_pos-4].decode('utf-8').split('\r\n')
        if len(lines[0])<16:
            thread_logger.warn("INVALU REQUEST:{0}".format(raw_data),extra=req);
            return
        headers = {k:v for k,v in (x.split(':',1) for x in lines[1:]) }
        if 'Referer' in headers:
            req['Referer']=headers['Referer']
        else:
            req['Referer']=''
        if 'User-Agent' in headers:
            req['User-Agent']=headers['User-Agent']
        else:
            req['User-Agent']=''
        req['request_line'] =lines[0]        
        req['method'],req['request_uri'],req['http_version']=lines[0].split(' ')

        #check if the first line is valid request. request_line might be empty
        if not req['method'] or not req['request_uri'] or not req['http_version']:
            thread_logger.warn("INVALU REQUEST:{0}".format(raw_data),extra=req);
            return
    except Exception as e:
        thread_logger.error("INVALU REQUEST:{0} {1}".format(e, raw_data),extra=req);
        logging.exception("INVALU REQUEST")
        return
    access_logger.info("",extra=req)
    #pdb.set_trace()
    m=p.match(req['request_uri'])
    req['host']=m.group(2)
    req['port']=int(m.group(4)) if m.group(4) else 80


    # Check if request is allowed or not
    if not ishostAllowed(req['host']):
        csv_logger.info("blocked",extra=req);
        thread_logger.warn("Block REQUEST:{0}".format(raw_data),extra=req);
        response(403,"The website isn't allowed")
        return

    csv_logger.info("allowed",extra=req);
    #pdb.set_trace() 
    if req['method']=='CONNECT':
        proxy_https(req)
    else:
        proxy_http(req)
