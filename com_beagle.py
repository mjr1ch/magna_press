#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback
import logging
import bealge_message

class beagleserver():

    sel = selectors.DefaultSelector()
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
    PORT = 65430        # Port to listen on (non-privileged ports are > 1023)
    # Avoid bind() exception: OSError: [Errno 48] Address already in use
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind((HOST, PORT))


    def accept_wrapper(sock):
        conn, addr = sock.accept()  # Should be ready to read
        logging.info("accepted connection from", addr)
        conn.setblocking(False)
        message = server_message.Message(sel, conn, addr)
        sel.register(conn, selectors.EVENT_READ, data=message)
        self.lsock.listen()
        logging.info("listening on", (HOST, PORT))
        lsock.setblocking(False)
        sel.register(lsock, selectors.EVENT_READ, data=None)


    def run():
        try:
            while True:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        accept_wrapper(key.fileobj)
                    else:
                        message = key.data
                        try:
                            message.process_events(mask)
                        except Exception:
                            logging.info(
                                "main: error: exception for",
                                f"{message.addr}:\n{traceback.format_exc()}",
                            )
                    message.close()
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            sel.close()
