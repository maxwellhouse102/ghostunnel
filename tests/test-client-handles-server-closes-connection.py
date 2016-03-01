#!/usr/bin/env python3

# Creates a ghostunnel. Ensures when server disconnects that the client
# connection also disconnects.

from subprocess import Popen
from test_common import RootCert, LOCALHOST, STATUS_PORT, SocketPair, print_ok, TcpClient, TlsServer
import socket, ssl

if __name__ == "__main__":
  ghostunnel = None
  try:
    # create certs
    root = RootCert('root')
    root.create_signed_cert('server')
    root.create_signed_cert('client')

    # start ghostunnel
    ghostunnel = Popen(['../ghostunnel', 'client', '--listen={0}:13004'.format(LOCALHOST),
      '--target={0}:13005'.format(LOCALHOST), '--keystore=client.p12',
      '--status={0}:{1}'.format(LOCALHOST, STATUS_PORT), '--cacert=root.crt'])

    # connect with client, confirm that the tunnel is up
    pair = SocketPair(TcpClient(13004), TlsServer('server', 'root', 13005))
    pair.validate_can_send_from_server("hello world", "1: server -> client")
    pair.validate_can_send_from_client("hello world", "1: client -> server")
    pair.validate_closing_server_closes_client("1: server closed -> client closed")

    print_ok("OK")
  finally:
    if ghostunnel:
      ghostunnel.kill()
