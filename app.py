#!/usr/bin/env python

import asyncio

import websockets

# simple connection between server and localhost
# async def handler(websocket):
#     while True:
#         message = await websocket.recv()
#         print(message)


# To remove the exception part
# async def handler(websocket):
#     while True:
#         try:
#             message = await websocket.recv()
#         except websockets.ConnectionClosedOK:
#             break
#         print(message)


#  Works same as above but in smaller line of codes
async def handler(websocket):
    async for message in websocket:
        print(message)


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())