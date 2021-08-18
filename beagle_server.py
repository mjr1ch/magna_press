#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback
import beagle_message
from PyQt5.QtCore import QRunnable,QThreadPool

class Responder():
    
    sel = selectors.DefaultSelector()
    HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
    PORT = 65413 # Port to listen on (non-privileged ports are > 1023)
    message = None 

    def __init__(self):
        super().__init__()
        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        self.lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.lsock.bind((self.HOST, self.PORT))
        self.lsock.listen()
        print("listening on", (self.HOST, self.PORT))
        self.lsock.setblocking(False)
        self.sel.register(self.lsock, selectors.EVENT_READ, data=None)

    def accept_wrapper(self,sock):
        conn, addr = sock.accept()  # Should be ready to read
        print("accepted connection from", addr)
        conn.setblocking(False)
        self.message = beagle_message.Message(self.sel, conn, addr)
        print('blocking and creating message')
        self.sel.register(conn, selectors.EVENT_READ, data=self.message)
        print(' register mmessage')

    def listen(self):
        try:
            while True:
                events = self.sel.select(timeout=None)
                print(events)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                        print('registering conneciton')
                    else:
                        self.message = key.data
                        try:
                            print('processing  message')
                            self.message.process_events(mask)
                        except Exception:
                            print(
                                "main: error: exception for",
                                f"{self.message.addr}:\n{traceback.format_exc()}",
                            )
                            self.message.close()
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self.sel.close()



