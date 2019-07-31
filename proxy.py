from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import re
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment

"""
Proxy server that modifies pages of habr.com website
by putting trademark sign at the end of every 6 character word
"""

SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 8081
SERVER_URL = "http://%s:%s" % (SERVER_ADDRESS, SERVER_PORT)

SVG_URL = "https://habr.com/images/1564133473/common-svg-sprite.svg"


class HTTPServer_RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)

        self.send_header('Content-type', 'text/html')
        self.end_headers()
        source_code = requests.get("https://habr.com" + self.path).text

        # To stay on proxy server address
        source_code = source_code.replace(' href="https://habr.com',
                                          ' href="'+SERVER_URL)
        source_code = source_code.replace(' href="http://habrahabr.ru',
                                          ' href="'+SERVER_URL)

        source_code = add_tm(source_code)
        self.wfile.write(bytes(source_code, "utf-8"))
        return


def is_text_visible(element):
    """
    Checks if text visible on web page
    """
    parents = ['style', 'script', 'head', 'title', 'meta']
    if element.parent.name in parents:
        return False
    if isinstance(element, Comment):
        return False
    return True


def add_tm(source_code):
    """
    Adds trademark sign to every word of length 6
    Args:
        source_code (str): Source code of web page.
    Returns:
        modified_code (str): Modified source code with added trademarks
    """
    modified_code = str()
    in_script = False
    in_style = False
    for line in source_code.split('\n'):
        # Escape js scripts and style
        if "<script" in line:
            in_script = True
        if "</script" in line:
            in_script = False
        if "<style" in line:
            in_style = True
        if "</style" in line:
            in_style = False

        soup = BeautifulSoup(line, 'html.parser')
        text = soup.findAll(text=True)
        visible_text = filter(is_text_visible, text)
        if not in_script and not in_style:
            for sentence in visible_text:
                for word in re.findall(r'\b\w{6}\b', str(sentence)):
                    line = line.replace(word, word+"™")
                # In case if there is a sequence of tm
                line = re.sub(r'™+', r'™', line)
                # If substring was replaced
                line = re.sub(r'(™)([a-zA-Zа-яА-Я])', r'\g<2>', line)

        if in_style:
            # Works better, but relays on web server
            line = line.replace("/fonts/0/FiraSans/", "http://95.213.203.189/")
        # Put svg file for local use in source_code
        if "<body" in line:
            svg_file = requests.get(SVG_URL).text
            line = line + "\n" + svg_file
        if "common-svg-sprite.svg" in line:
            line = re.sub(r'https://habr.com/images/\d*/common-svg-sprite.svg',
                          '', line)
        modified_code += str(line) + "\n"
    return modified_code


def run():
    print('Starting proxy server at %s' % SERVER_URL)
    server_address = (SERVER_ADDRESS, SERVER_PORT)
    httpd = HTTPServer(server_address, HTTPServer_RequestHandler)
    httpd.serve_forever()


if __name__ == "__main__":
    run()
