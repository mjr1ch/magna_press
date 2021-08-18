import asyncio
import random

class responder():
    
    def __init__(self, parent=None):	
        super().__init__()



    async def produce(self,queue, n):
        for x in range(n):
            # produce an item
            print('producing {}/{}'.format(x, n))
            # simulate i/o operation using sleep
            await asyncio.sleep(random.random())
            item = str(x)
            # put the item in the queue
            await queue.put(item)

    async def consume(self,queue):
        while True:
            # wait for an item from the producer
            item = await queue.get()

            # process the item
            print('consuming {}...'.format(item))
            # simulate i/o operation using sleep
            await asyncio.sleep(random.random())

            # Notify the queue that the item has been processed
            queue.task_done()

    async def run(self,n):
        queue = asyncio.Queue()
        # schedule the consumer
        self.consumer = asyncio.ensure_future(self.consume(queue))
        # run the producer and wait for completion
        await self.produce(queue, n)
        # wait until the consumer has processed all items
        await queue.join()
        # the consumer is still awaiting for an item, cancel it
        self.consumer.cancel()

    async def handle_echo(self,reader, writer):
        data = await reader.read(100)
        message = data.decode()
        addr = writer.get_extra_info('peername')
        print("Received %r from %r" % (message, addr))
        if (message == 'START_RUN'):
            data = await self.run(10) 
            print("Send: %i" % data)
            writer.write(data)
            await writer.drain()
        else: 
            print("Send: %r" % message)
            writer.write(message)
            await writer.drain()

        print("Close the client socket")
        writer.close()

    def launch_server(self):
        self.loop = asyncio.get_event_loop()
        #coro = asyncio.start_server(handle_echo, '192.168.7.2', 7777, loop=loop)
        self.coro = asyncio.start_server(self.handle_echo, '127.0.0.1', 7780, loop=self.loop)
        self.server = self.loop.run_until_complete(self.coro)

        # Serve requests until Ctrl+C is pressed
        print('Serving on {}'.format(self.server.sockets[0].getsockname()))
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            # Close the server
            self.server.close()
            self.loop.run_until_complete(self.server.wait_closed())
            self.loop.close()

def main():
    server = responder()
    server.launch_server()

if __name__ == '__main__':
    main()
