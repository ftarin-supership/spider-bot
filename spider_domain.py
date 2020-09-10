import re
import sys
import time
import threading
import queue

from itertools import chain

from webpage import WebPage, WebPageLinkExtractor

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: {} <source_url> [max num of internal_links]".format(sys.argv[0]))
        sys.exit(0)

    source_url = sys.argv[1]
    max_sites = float('inf')
    if len(sys.argv) == 3:
        max_sites = int(sys.argv[2])

    to_process = [source_url]
    visited = set()
    internal_links = []

    while len(to_process):
        url = to_process.pop()
        w = WebPageLinkExtractor(WebPage(url))

        if len(visited) >= max_sites:
            break

        for web in w.internal_links:
            index = web.url.find('#')
            if index != -1:
                web.url = web.url[:index]
            if web.url not in visited:
                visited.add(web.url)
                to_process.append(web.url)

        time.sleep(0.3)

    for link in visited:
        print(link)
