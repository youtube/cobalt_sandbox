#!/usr/bin/python

from mod_pywebsocket import common, msgutil, util
from mod_pywebsocket.handshake import hybi
from six.moves.urllib import parse as urlparse

def web_socket_do_extra_handshake(request):
    url_parts = urlparse.urlsplit(request.uri)
    request.connection.write('HTTP/1.1 101 Switching Protocols:\x0D\x0AConnection: Upgrade\x0D\x0AUpgrade: WebSocket\x0D\x0ASet-Cookie: ws_test_'+(url_parts.query or '')+'=test; Path=/; HttpOnly\x0D\x0ASec-WebSocket-Origin: '+request.ws_origin+'\x0D\x0ASec-WebSocket-Accept: '+hybi.compute_accept(request.headers_in.get(common.SEC_WEBSOCKET_KEY_HEADER))[0]+'\x0D\x0A\x0D\x0A')
    return

def web_socket_transfer_data(request):
    while True:
        return
