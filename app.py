#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import socket
from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ

from bs4 import BeautifulSoup

__author__ = 'Bruce Chen'

logging.basicConfig(level=logging.INFO)

selector = DefaultSelector()

sock = socket.socket()
sock.setblocking(False)
try:
    sock.connect(('guazi.com', 80))
except BlockingIOError:
    pass


def connected():
    selector.unregister(sock.fileno())
    logging.info('connected!')


def loop():
    while True:
        events = selector.select()
        for event_key, event_mask in events:
            callback = event_key.data
            callback()


urls_todo = {'/'}
seen_urls = {'/'}


class Fetcher:
    def __init__(self, url):
        self.response = b''
        self.url = url
        self.sock = None

    # Method on Fetcher class
    def fetch(self):
        self.sock = socket.socket()
        self.sock.setblocking(False)
        try:
            self.sock.connect(('guazi.com', 80))
        except BlockingIOError:
            pass

        # Register next callback.
        selector.register(self.sock.fileno(),
                          EVENT_WRITE, self.connected)

    def connected(self, key, mask):
        logging.info('connected!')
        selector.unregister(key.fd)
        request = 'GET {} HTTP/1.1\r\nHost: www.guazi.com\r\n\r\n'.format(self.url)
        self.sock.send(request.encode('ascii'))

        # Register next callback.
        selector.register(self.sock.fileno(),
                          EVENT_READ, self.read_response)

    def read_response(self, key, mask):
        global stopped

        chunk = self.sock.recv(4096)
        if chunk:
            self.response += chunk
        else:
            selector.unregister(key.fd)  # Done reading
            links = self.parse_links()

    def parse_links(self):
        links = set()

class Future:
    def __init__(self):
        self.result = None

# def parse_links(html):
#     soup = BeautifulSoup(html, 'lxml')
#     return soup.findAll('a').get('href')
#
#
# with open('guazi.txt', 'rt', encoding='utf-8') as f:
#     html = f.read()
# soup = BeautifulSoup(html, 'lxml')
# with open('links.txt', 'w') as f:
#     for link in soup.findAll('a'):
#         f.write('%s\n' % link.get('href'))
