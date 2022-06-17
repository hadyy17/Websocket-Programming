import websocket

1#!/usr/bin/env python
 2
 3import asyncio
 4import itertools
 5import json
 6
 7import websockets
 8
 9from connect import PLAYER1, PLAYER2, Connect4
10
11
12async def handler(websocket):
13    # Initialize a Connect Four game.
14    game = Connect4()
15
16    # Players take alternate turns, using the same browser.
17    turns = itertools.cycle([PLAYER1, PLAYER2])
18    player = next(turns)
19
20    async for message in websocket:
21        # Parse a "play" event from the UI.
22        event = json.loads(message)
23        assert event["type"] == "play"
24        column = event["column"]
25
26        try:
27            # Play the move.
28            row = game.play(player, column)
29        except RuntimeError as exc:
30            # Send an "error" event if the move was illegal.
31            event = {
32                "type": "error",
33                "message": str(exc),
34            }
35            await websocket.send(json.dumps(event))
36            continue
37
38        # Send a "play" event to update the UI.
39        event = {
40            "type": "play",
41            "player": player,
42            "column": column,
43            "row": row,
44        }
45        await websocket.send(json.dumps(event))
46
47        # If move is winning, send a "win" event.
48        if game.winner is not None:
49            event = {
50                "type": "win",
51                "player": game.winner,
52            }
53            await websocket.send(json.dumps(event))
54
55        # Alternate turns.
56        player = next(turns)
57
58
59async def main():
60    async with websockets.serve(handler, "", 8001):
61        await asyncio.Future()  # run forever
62
63
64if __name__ == "__main__":
65    asyncio.run(main())