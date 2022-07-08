  1#!/usr/bin/env python
  2
  3import asyncio
  4import json
  5import secrets
  6
  7import websockets
  8
  9from connect4 import PLAYER1, PLAYER2, Connect4
 10
 11
 12JOIN = {}
 13
 14WATCH = {}
 15
 16
 17async def error(websocket, message):
 18    """
 19    Send an error message.
 20
 21    """
 22    event = {
 23        "type": "error",
 24        "message": message,
 25    }
 26    await websocket.send(json.dumps(event))
 27
 28
 29async def replay(websocket, game):
 30    """
 31    Send previous moves.
 32
 33    """
 34    # Make a copy to avoid an exception if game.moves changes while iteration
 35    # is in progress. If a move is played while replay is running, moves will
 36    # be sent out of order but each move will be sent once and eventually the
 37    # UI will be consistent.
 38    for player, column, row in game.moves.copy():
 39        event = {
 40            "type": "play",
 41            "player": player,
 42            "column": column,
 43            "row": row,
 44        }
 45        await websocket.send(json.dumps(event))
 46
 47
 48async def play(websocket, game, player, connected):
 49    """
 50    Receive and process moves from a player.
 51
 52    """
 53    async for message in websocket:
 54        # Parse a "play" event from the UI.
 55        event = json.loads(message)
 56        assert event["type"] == "play"
 57        column = event["column"]
 58
 59        try:
 60            # Play the move.
 61            row = game.play(player, column)
 62        except RuntimeError as exc:
 63            # Send an "error" event if the move was illegal.
 64            await error(websocket, str(exc))
 65            continue
 66
 67        # Send a "play" event to update the UI.
 68        event = {
 69            "type": "play",
 70            "player": player,
 71            "column": column,
 72            "row": row,
 73        }
 74        websockets.broadcast(connected, json.dumps(event))
 75
 76        # If move is winning, send a "win" event.
 77        if game.winner is not None:
 78            event = {
 79                "type": "win",
 80                "player": game.winner,
 81            }
 82            websockets.broadcast(connected, json.dumps(event))
 83
 84
 85async def start(websocket):
 86    """
 87    Handle a connection from the first player: start a new game.
 88
 89    """
 90    # Initialize a Connect Four game, the set of WebSocket connections
 91    # receiving moves from this game, and secret access tokens.
 92    game = Connect4()
 93    connected = {websocket}
 94
 95    join_key = secrets.token_urlsafe(12)
 96    JOIN[join_key] = game, connected
 97
 98    watch_key = secrets.token_urlsafe(12)
 99    WATCH[watch_key] = game, connected
100
101    try:
102        # Send the secret access tokens to the browser of the first player,
103        # where they'll be used for building "join" and "watch" links.
104        event = {
105            "type": "init",
106            "join": join_key,
107            "watch": watch_key,
108        }
109        await websocket.send(json.dumps(event))
110        # Receive and process moves from the first player.
111        await play(websocket, game, PLAYER1, connected)
112    finally:
113        del JOIN[join_key]
114        del WATCH[watch_key]
115
116
117async def join(websocket, join_key):
118    """
119    Handle a connection from the second player: join an existing game.
120
121    """
122    # Find the Connect Four game.
123    try:
124        game, connected = JOIN[join_key]
125    except KeyError:
126        await error(websocket, "Game not found.")
127        return
128
129    # Register to receive moves from this game.
130    connected.add(websocket)
131    try:
132        # Send the first move, in case the first player already played it.
133        await replay(websocket, game)
134        # Receive and process moves from the second player.
135        await play(websocket, game, PLAYER2, connected)
136    finally:
137        connected.remove(websocket)
138
139
140async def watch(websocket, watch_key):
141    """
142    Handle a connection from a spectator: watch an existing game.
143
144    """
145    # Find the Connect Four game.
146    try:
147        game, connected = WATCH[watch_key]
148    except KeyError:
149        await error(websocket, "Game not found.")
150        return
151
152    # Register to receive moves from this game.
153    connected.add(websocket)
154    try:
155        # Send previous moves, in case the game already started.
156        await replay(websocket, game)
157        # Keep the connection open, but don't receive any messages.
158        await websocket.wait_closed()
159    finally:
160        connected.remove(websocket)
161
162
163async def handler(websocket):
164    """
165    Handle a connection and dispatch it according to who is connecting.
166
167    """
168    # Receive and parse the "init" event from the UI.
169    message = await websocket.recv()
170    event = json.loads(message)
171    assert event["type"] == "init"
172
173    if "join" in event:
174        # Second player joins an existing game.
175        await join(websocket, event["join"])
176    elif "watch" in event:
177        # Spectator watches an existing game.
178        await watch(websocket, event["watch"])
179    else:
180        # First player starts a new game.
181        await start(websocket)
182
183
184async def main():
185    async with websockets.serve(handler, "", 8001):
186        await asyncio.Future()  # run forever
187
188
189if __name__ == "__main__":
190    asyncio.run(main())