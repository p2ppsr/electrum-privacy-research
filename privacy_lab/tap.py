"""Server-side TLS termination and newline-exact JSON-RPC evidence capture.

This is instrumentation in front of a server we select, not a TLS interceptor.
It never obtains a client's seed, wallet database, or derivation metadata.
"""
import asyncio
import base64
import hashlib
import json
import ssl
import time
from datetime import datetime, timezone
from pathlib import Path

LIMIT = 64 * 1024 * 1024


class Journal:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.file = self.path.open("x")
        self.previous = "0" * 64
        self.sequence = 0

    def record(self, **fields):
        self.sequence += 1
        row = dict(sequence=self.sequence,
                   utc=datetime.now(timezone.utc).isoformat(),
                   monotonic_ns=time.monotonic_ns(),
                   previous_sha256=self.previous, **fields)
        encoded = json.dumps(row, sort_keys=True, separators=(",", ":")).encode()
        self.previous = hashlib.sha256(encoded).hexdigest()
        row["sha256"] = self.previous
        self.file.write(json.dumps(row, sort_keys=True) + "\n")
        self.file.flush()

    def frame(self, session, direction, frame):
        # Preserve exact wire bytes as well as parsed JSON. Decode failures remain evidence.
        fields = dict(session=session, direction=direction,
                      wire_base64=base64.b64encode(frame).decode())
        try:
            fields["message"] = json.loads(frame)
        except (ValueError, UnicodeDecodeError) as exc:
            fields["parse_error"] = str(exc)
        self.record(event="frame", **fields)

    def close(self):
        self.file.close()


class Tap:
    def __init__(self, journal, backend, tls_context=None):
        self.journal, self.backend, self.tls_context = journal, backend, tls_context
        self.connections = 0
        self.active = set()

    async def start(self, port=0):
        self.server = await asyncio.start_server(self.handle, "127.0.0.1", port,
                                                ssl=self.tls_context, limit=LIMIT)
        return self.server.sockets[0].getsockname()[1]

    async def handle(self, reader, writer):
        self.connections += 1
        session = self.connections
        task = asyncio.current_task()
        self.active.add(task)
        self.journal.record(event="connect", session=session, peer=writer.get_extra_info("peername"))
        upstream_writer = None
        try:
            host, port, use_ssl = self.backend
            context = ssl.create_default_context() if use_ssl else None
            # Public Electrum deployments commonly use self-signed certs. This is explicit
            # and recorded; an advertised version string is never binary attestation.
            if context:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            upstream_reader, upstream_writer = await asyncio.open_connection(
                host, port, ssl=context, server_hostname=host if use_ssl else None, limit=LIMIT)
            self.journal.record(event="backend", session=session, host=host, port=port,
                                tls=bool(context), certificate_validation=False if context else None)

            async def pump(src, dst, direction):
                while True:
                    line = await src.readline()
                    if not line:
                        break
                    self.journal.frame(session, direction, line)
                    dst.write(line)
                    await dst.drain()

            tasks = [asyncio.create_task(pump(reader, upstream_writer, "request")),
                     asyncio.create_task(pump(upstream_reader, writer, "response"))]
            _, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for item in pending:
                item.cancel()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    self.journal.record(event="transport_error", session=session, error=repr(result))
        except Exception as exc:
            self.journal.record(event="transport_error", session=session, error=repr(exc))
        finally:
            if upstream_writer:
                upstream_writer.close()
            writer.close()
            self.journal.record(event="disconnect", session=session)
            self.active.discard(task)

    async def stop(self):
        self.server.close()
        await self.server.wait_closed()
        for task in list(self.active):
            task.cancel()
        await asyncio.gather(*list(self.active), return_exceptions=True)
