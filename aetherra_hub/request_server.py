"""Bounded HTTP transport for the in-process compatibility Hub."""

from __future__ import annotations

# Standard library imports
import contextlib
import socketserver
import threading

# Third party imports
from werkzeug.serving import ThreadedWSGIServer, WSGIRequestHandler

# Local imports
from .services.request_ownership import RESPONSE_CLOSE_KEY, busy_response

MAX_REQUEST_WORKERS = 8
REQUEST_IO_TIMEOUT_SECONDS = 5.0


class _RequestHandler(WSGIRequestHandler):
    # Per socket operation, not an elapsed-time budget for generation. Incomplete
    # headers/bodies and clients that stop reading cannot hold workers indefinitely.
    timeout = REQUEST_IO_TIMEOUT_SECONDS

    def run_wsgi(self):
        try:
            super().run_wsgi()
        finally:
            # A reset/timeout while Werkzeug discards unread input can skip its
            # iterable.close(). Always finalize our response, exactly once.
            close = getattr(self, "environ", {}).pop(RESPONSE_CLOSE_KEY, None)
            if close is not None:
                close()


class BoundedWSGIServer(ThreadedWSGIServer):
    def __init__(self, host, port, app):
        self._workers = threading.Condition()
        self._active_workers = 0
        super().__init__(host, port, app, handler=_RequestHandler)

    def serve_forever(self, poll_interval=0.5):
        # Werkzeug closes the listener as soon as this loop exits. The compat
        # owner instead closes it only after HTTP and retained stream workers drain.
        socketserver.BaseServer.serve_forever(self, poll_interval=poll_interval)

    def process_request(self, request, client_address):
        with self._workers:
            if self._active_workers < MAX_REQUEST_WORKERS:
                self._active_workers += 1
                self._workers.notify_all()
                admitted = True
            else:
                admitted = False
        if not admitted:
            # This is before HTTP parsing: there is no trusted path or trace ID.
            # Never block the accept loop on a client that is not reading.
            body, headers = busy_response("hub_saturated")
            response = (
                "HTTP/1.1 503 Service Unavailable\r\n"
                + "".join(f"{name}: {value}\r\n" for name, value in headers)
                + "Connection: close\r\n\r\n"
            ).encode("ascii") + body
            try:
                request.setblocking(False)
                with contextlib.suppress(OSError):
                    request.send(response)
            finally:
                self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except BaseException:
            self._release_worker()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self._release_worker()

    def _release_worker(self):
        with self._workers:
            self._active_workers -= 1
            self._workers.notify_all()

    def wait_for_idle(self, timeout):
        with self._workers:
            return self._workers.wait_for(
                lambda: self._active_workers == 0, timeout=timeout
            )


def make_server(host, port, app):
    """Keep the historical three-argument compat factory interface."""
    return BoundedWSGIServer(host, port, app)
