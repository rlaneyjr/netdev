"""
Copyright (c) 2020 Sergey Yakovlev <selfuryon@gmail.com>.

The module contains Telnet Connection class.
This class connects to devices using asyncio protocol.
"""
import asyncio
import logging

from netdev.connections.constants import MAX_BUFFER
from netdev.connections.io_connection import IOConnection
from netdev.exceptions import DisconnectError
from netdev.logger import logger


class TelnetConnection(IOConnection):
    """ Telnet Connection Class """

    def __init__(
        self,
        host: str,
        port: int = 23,
        username: str = "",
        password: str = "",
        *,
        family: int = 0,
        flags: int = 0,
    ) -> None:
        if not host:
            raise ValueError("Host must be set")
        self.host = host
        self.port = port 
        self.args = {"username": username, "password": password, "family": family, "flags": flags}

    async def connect(self) -> None:
        """ Establish the Telnet Connection """
        self._logger.info(
            "Host %s: Establishing Telnet Connection on port %s", self.host, self.port)
        try:
            self._stdout, self._stdin = await asyncio.open_connection(self.host, self.port, **self.args)
        except Exception as error:
            raise DisconnectError(self.host, None, str(error))

    async def disconnect(self) -> None:
        """ Gracefully close the Telnet Connection """
        self._logger.info("Host %s: Disconnecting", self.host)
        self._stdin.close()
        await self._stdin.wait_closed()

    async def send(self, cmd: str) -> None:
        """ Send command to the channel"""
        self._logger.debug("Host %s: Send to channel: %r", self.host, cmd)
        self._stdin.write(cmd.encode())

    async def read(self) -> str:
        """ Read buffer from the channel """
        output = await self._stdout.read(MAX_BUFFER)
        self._logger.debug(
            "Host %s: Recieved from channel: %r", self.host, output)
        return output.decode(errors="ignore")

    @property
    def _logger(self) -> logging.Logger:
        return logger.getChild("TelnetConnection")
