import queue
import re
import sys
import threading
import time
from itertools import chain

from webpage import WebPage, WebPageLinkExtractor

FORBIDDEN_DOMAINS = re.compile(
    "twitter\.com$|.*google\.com$|.*youtube\.com$|.*apple\.com$|.*linkedin\.com$|.*amazon\.co\.jp$|.*facebook\.com$|.*steampowered\.com$|.*audible\.co\.jp$|.*amzn\.to$|news\.livedoor\.com$|.*adobe\.com$|.*microsoft\.com$|www\.dtiblog\.com$|blog\.fc2\.com$|.*\.dmm\.com|admin\.blog\.fc2\.com|fc2\.com$|.*dmm\.co\.jp$|feedly\.com&|wiki\.fc2\.com$|instagram.com$|redd.it$"
)
FORBIDDEN_FILETYPES = re.compile(".*png$|.*jpg$|.*gif$")


def get_chunks(s, size, step=1):
    for x in range(0, len(s) - size + step, step):
        yield s[x:x + step]


def process_web_page(thread_id, sites, q):
    webpages = []

    for site in sites:
        try:
            w = WebPageLinkExtractor(WebPage(site))
            # Discard invalid webpages
            for web in w.external_links:
                if FORBIDDEN_DOMAINS.match(web.qdn) or\
                   FORBIDDEN_FILETYPES.match(web.url):
                    continue
                webpages.append(web)
            time.sleep(0.1)
        except:
            pass

    q.put(webpages)


if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: {} <source_url> <depth> [num_threads]".format(
            sys.argv[0]))
        sys.exit(0)

    source_url = sys.argv[1]
    depth = int(sys.argv[2])
    num_threads = 10
    if len(sys.argv) == 4:
        num_threads = int(sys.argv[3])

    webpages = [source_url]
    visited_domains = set()
    q = queue.Queue()

    for d in range(depth):
        size = 1
        if len(webpages) > (num_threads + 1):
            size = len(webpages) // (num_threads + 1)

        threads = []
        for i, wp_sl in enumerate(list(get_chunks(webpages, size, size))):
            t = threading.Thread(target=process_web_page, args=(i, wp_sl, q))
            threads.append(t)
            t.start()

        print("Depth: {}, Threads: {}".format(d, len(threads)))

        for t in threads:
            t.join()

        next_level = []
        while not q.empty():
            item = q.get(False)
            next_level.extend(item)
            q.task_done()

        webpages = []
        for wp in next_level:
            if wp.qdn in visited_domains:
                continue
            visited_domains.add(wp.qdn)
            webpages.append('http://' + wp.qdn)

    for webpage in visited_domains:
        print('http://' + webpage)
