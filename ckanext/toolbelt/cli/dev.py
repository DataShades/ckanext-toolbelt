import asyncio
import email

import click
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Debugging


class DecodingDebugging(Debugging):
    def _print_message_content(self, peer, data: bytes):
        msg = email.message_from_bytes(data)
        print("# Headers:", file=self.stream)
        for header, value in msg.items():
            print(header, ": ", value, file=self.stream)
        print("# Message:", file=self.stream)
        for part in msg.walk():
            print("---------- a part: ----------", file=self.stream)
            maybe_decoded_payload = part.get_payload(decode=True)
            if maybe_decoded_payload is not None:
                try:
                    decoded = bytes.decode(maybe_decoded_payload, encoding="utf-8")
                except UnicodeError as e:
                    decoded = f"<{e}>"

                print(
                    decoded,
                    file=self.stream,
                )


@click.group()
def dev():
    """Tools for debugging and development."""


@dev.command()
@click.option("-p", "--port", default=8025, type=int)
@click.option("-h", "--host", default="localhost")
def mail_server(port: int, host: str):
    """Start mail server that will catch outcomming mails."""
    loop = asyncio.get_event_loop()
    ctrl = Controller(DecodingDebugging(), host, port)
    ctrl.start()
    loop.run_forever()
