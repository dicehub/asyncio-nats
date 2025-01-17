import asyncio
import os
import signal
import nats


async def run(loop):

    is_done = asyncio.Future(loop=loop)

    async     def closed_cb():
        print("Connection to NATS is closed.")
        is_done.set_result(True)

    opts = {
        "servers": ["nats://127.0.0.1:4222"],
        "io_loop": loop,
        "closed_cb": closed_cb
    }

    with (await nats.connect(**opts)) as nc:
        print("Connected to NATS at {}...".format(nc.connected_url.netloc))

        async         def subscribe_handler(msg):
            subject = msg.subject
            reply = msg.reply
            data = msg.data.decode()
            print("Received a message on '{subject} {reply}': {data}".format(
                subject=subject, reply=reply, data=data))

        await nc.subscribe("discover", cb=subscribe_handler)
        await nc.flush()

        for i in range(0, 10):
            await nc.publish("discover", b"hello world")
            await asyncio.sleep(0.1, loop=loop)

    await asyncio.wait_for(is_done, 60.0, loop=loop)
    loop.stop()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run(loop))
    finally:
        loop.close()
