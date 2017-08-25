import socket
import threading
import signal
import sys
import fnmatch
import errno
import time
import pdb
import re
import os
from time import gmtime, strftime, localtime
from subprocess import Popen
import logging
import logging.config
import pthread
import config

logging.config.fileConfig('logging.conf')
proxy_logger = logging.getLogger('proxy')

class Server:
    """ The server class """

    def __init__(self, config):
        signal.signal(signal.SIGINT, self.shutdown)     # Shutdown on Ctrl+C
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)             # Create a TCP socket
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    # Re-use the socket
        self.serverSocket.bind((config.bind_host, config.bind_port)) # bind the socket to a public host, and a port
        self.serverSocket.listen(10)    # become a server socket
        proxy_logger.info('Pcxy started. Listening at port:'+str(config.bind_port))
        self.__clients = {}


    def listenForClient(self):
        """ Wait for clients to connect """
        while True:
            (clientSocket, client_address) = self.serverSocket.accept()   # Establish the connection
            d = threading.Thread(name=self._getClientName(client_address), target=pthread.proxy, args=(clientSocket, client_address))
            d.setDaemon(True)
            d.start()
        self.shutdown(0,0)

    def shutdown(self, signum, frame):
        """ Handle the exiting server. Clean all traces """
        proxy_logger.info('Shutting down gracefully...')
        main_thread = threading.currentThread()        # Wait for all clients to exit
        for t in threading.enumerate():
            if t is main_thread:
                continue
            proxy_logger.warning('joining '+t.getName())
            t.join()
        self.serverSocket.close()
        sys.exit(0)

    def _getClientName(self, cli_addr):
        """ Return the clientName.
        """
        return "Client"

if __name__ == "__main__":
    server = Server(config)
    server.listenForClient()
