#!/usr/bin/env python3
import logging
import sys
import socket
import selectors
import traceback
import pc_message
from PyQt5.QtCore import QRunnable, pyqtSignal

class SingleCommand(QRunnable):
    HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
    PORT = 65413 # Port to listen on (non-privileged ports are > 1023)

    def __init__(self,command_text):
        super().__init__()
        self.message_text = command_text

    def _start_connection(self,host, port, request):
        sel = selectors.DefaultSelector()
        addr = (host, port)
        print(f"starting connection to", addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        message = pc_message.Message(sel, sock, addr, request)
        print(sock)
        sel.register(sock, events, data=message)
        return sel 

    def transmit(self):
        sel = self._start_connection(self.HOST, self.PORT, self.message_text)
        try:
            while True:
                events = sel.select(timeout=1)
                for key, mask in events:
                    message = key.data
                    try:
                        message.process_events(mask)
                    except Exception:
                        print(
                            "main: error: exception for",
                            f"{message.addr}:\n{traceback.format_exc()}",
                        )
                        message.close()
                # Check for a socket being monitored to continue.
                if not sel.get_map():
                    break
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            print('closing sel')
            sel.close()
        
    def run(self):
        # Your long-running task goes here ...
        self.transmit()





