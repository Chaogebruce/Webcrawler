#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Bruce Chen'

import socket

def fetch(url):
    sock = socket.socket()
    sock.connect(('guazi.com',80))
    request = 'GET {} HTTP/1.1\r\nHost: www.guazi.com\r\n\r\n'.format(url)
    sock.send(request.encode('ascii'))
    response = b''
    chunk = sock.recv(4096)
    while chunk:
        response += chunk
        chunk = sock.recv(4096)
    head,data = str(response).split('\r\n\r\n')
    print(head)

fetch('/sh/')