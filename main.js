 1import { createBoard, playMove } from "./connect4.js";
 2
 3function initGame(websocket) {
 4  websocket.addEventListener("open", () => {
 5    // Send an "init" event according to who is connecting.
 6    const params = new URLSearchParams(window.location.search);
 7    let event = { type: "init" };
 8    if (params.has("join")) {
 9      // Second player joins an existing game.
10      event.join = params.get("join");
11    } else if (params.has("watch")) {
12      // Spectator watches an existing game.
13      event.watch = params.get("watch");
14    } else {
15      // First player starts a new game.
16    }
17    websocket.send(JSON.stringify(event));
18  });
19}
20
21function showMessage(message) {
22  window.setTimeout(() => window.alert(message), 50);
23}
24
25function receiveMoves(board, websocket) {
26  websocket.addEventListener("message", ({ data }) => {
27    const event = JSON.parse(data);
28    switch (event.type) {
29      case "init":
30        // Create links for inviting the second player and spectators.
31        document.querySelector(".join").href = "?join=" + event.join;
32        document.querySelector(".watch").href = "?watch=" + event.watch;
33        break;
34      case "play":
35        // Update the UI with the move.
36        playMove(board, event.player, event.column, event.row);
37        break;
38      case "win":
39        showMessage(`Player ${event.player} wins!`);
40        // No further messages are expected; close the WebSocket connection.
41        websocket.close(1000);
42        break;
43      case "error":
44        showMessage(event.message);
45        break;
46      default:
47        throw new Error(`Unsupported event type: ${event.type}.`);
48    }
49  });
50}
51
52function sendMoves(board, websocket) {
53  // Don't send moves for a spectator watching a game.
54  const params = new URLSearchParams(window.location.search);
55  if (params.has("watch")) {
56    return;
57  }
58
59  // When clicking a column, send a "play" event for a move in that column.
60  board.addEventListener("click", ({ target }) => {
61    const column = target.dataset.column;
62    // Ignore clicks outside a column.
63    if (column === undefined) {
64      return;
65    }
66    const event = {
67      type: "play",
68      column: parseInt(column, 10),
69    };
70    websocket.send(JSON.stringify(event));
71  });
72}
73
74window.addEventListener("DOMContentLoaded", () => {
75  // Initialize the UI.
76  const board = document.querySelector(".board");
77  createBoard(board);
78  // Open the WebSocket connection and register event handlers.
79  const websocket = new WebSocket("ws://localhost:8001/");
80  initGame(websocket);
81  receiveMoves(board, websocket);
82  sendMoves(board, websocket);
83});