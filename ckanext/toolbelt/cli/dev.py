import click

import smtpd
import email
from smtpd import DebuggingServer


class DecodingDebuggingServer(DebuggingServer):
    def _print_message_content(self, peer, data: bytes):
        msg = email.message_from_bytes(data)
        print("# Headers:")
        for (header, value) in msg.items():
            print(header, ": ", value)
        print("# Message:")
        for part in msg.walk():
            print("---------- a part: ----------")
            maybe_decoded_payload = part.get_payload(decode=True)
            if maybe_decoded_payload is not None:
                print(bytes.decode(maybe_decoded_payload, encoding="utf-8"))


@click.group()
def dev():
    """Tools for debugging and development."""
    pass


@dev.command()
@click.option("-p", "--port", default=8025, type=int)
@click.option("-h", "--host", default="localhost")
def mail_server(port, host):
    """Start mail server that will catch outcomming mails."""
    DecodingDebuggingServer((host, port), (host, port))
    smtpd.asyncore.loop()
