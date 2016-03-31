#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import logging
import socket
import aiohttp
from asyncio import Queue

__author__ = 'Bruce Chen'

logging.basicConfig(level=logging.INFO)

loop = asyncio.get_event_loop()


class Crawler:
    def __init__(self, root_url, max_redirect):
        self.max_tasks = 10
        self.max_redirect = max_redirect
        self.q = Queue()
        self.seen_urls = set()

        # aiohttp's ClientSession does connection pooling and
        # HTTP keep-alives for us.
        self.session = aiohttp.ClientSession(loop=loop)

        # Put (URL, max_redirect) in the Queue
        self.q.put((root_url, self.max_redirect))
        
    @asyncio.coroutine
    def crawl(self):
        '''Run the crawler untill all work is done.'''
        workers = [asyncio.Task(self.work())
                   for _ in range(self.max_tasks)]

        # When all work is done, exit.
        yield from self.q.join()
        for w in workers:
            w.cancel()

    @asyncio.coroutine
    def work(self):
        while True:
            url, max_redirect = yield from self.q.get()

            # Download page and add new links to self.q
            yield from self.fetch(url, max_redirect)
            self.q.task_done()

    @asyncio.coroutine
    def fetch(self, url, max_redirect):
        # Handle redirects ourselves.
        response = yield from self.session.get(
            url, allow_redirects=False)

        try:
            if is_redirect(response):
                if max_redirect > 0:
                    next_url = response.headers['location']
                    if next_url in self.seen_urls:
                        # We have done this before.
                        return

                    # Remember we have seen this url.
                    self.seen_urls.add(next_url)

                    # Follow the redirect. One less redirect remains.
                    self.q.put_nowait((next_url, max_redirect -1))
            else:
                links = yield from self.parse_links(response)
                # Python set-logic:
                for link in links.difference(self.seen_urls):
                    self.q.put_nowait((link, self.max_redirect))
                self.seen_urls.update(links)
        finally:
            # Return connection to pool.
            yield from response.release()

crawler = Crawler('http://guazi.com', max_redirect=10)

loop.run_until_complete(crawler.crawl())
