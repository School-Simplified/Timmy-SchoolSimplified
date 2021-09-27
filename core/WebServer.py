import socketserver
import socket

from threading import Thread

import flask
from flask import Flask

app = Flask('')


@app.route('/')
def main():
    status_code = flask.Response(
        response = "Hello! I am alive, you can check my status at https://school-simplified.github.io/Timmy-StatusPage/.", 
        status=200
    )
    return status_code


def run():
    #socketserver.TCPServer.allow_reuse_address = True
    try:
        app.run(host="spaceturtle.tech", port = 5050, ssl_context='adhoc')
    except OSError:
        app.run(host = "0.0.0.0", port = 8080, ssl_context='adhoc')

def keep_alive():
    server = Thread(target=run)
    server.start()
