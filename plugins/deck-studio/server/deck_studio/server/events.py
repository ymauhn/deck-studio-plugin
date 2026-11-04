"""EventHub: server events fanned out to every listener (the /api/events streams and server-side code)."""
import asyncio


class EventHub:
    def __init__(self):
        self._queues = set()

    async def publish(self, type, **data):
        event = {"type": type, **data}
        for queue in self._queues:
            queue.put_nowait(event)

    async def stream(self, *first):
        """`first`, then every event published from now on, until the consumer stops iterating."""
        queue = asyncio.Queue()
        for event in first:
            queue.put_nowait(event)
        self._queues.add(queue)
        try:
            while True:
                yield await queue.get()
        finally:
            self._queues.discard(queue)
