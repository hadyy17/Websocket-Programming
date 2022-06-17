 1import { createBoard, playMove } from "./connect4.js";
 2
 3function showMessage(message) {
 4  window.setTimeout(() => window.alert(message), 50);
 5}
 6
 7function receiveMoves(board, websocket) {
 8  websocket.addEventListener("message", ({ data }) => {
 9    const event = JSON.parse(data);
10    switch (event.type) {
11      case "play":
12        // Update the UI with the move.
13        playMove(board, event.player, event.column, event.row);
14        break;
15      case "win":
16        showMessage(`Player ${event.player} wins!`);
17        // No further messages are expected; close the WebSocket connection.
18        websocket.close(1000);
19        break;
20      case "error":
21        showMessage(event.message);
22        break;
23      default:
24        throw new Error(`Unsupported event type: ${event.type}.`);
25    }
26  });
27}
28
29function sendMoves(board, websocket) {
30  // When clicking a column, send a "play" event for a move in that column.
31  board.addEventListener("click", ({ target }) => {
32    const column = target.dataset.column;
33    // Ignore clicks outside a column.
34    if (column === undefined) {
35      return;
36    }
37    const event = {
38      type: "play",
39      column: parseInt(column, 10),
40    };
41    websocket.send(JSON.stringify(event));
42  });
43}
44
45window.addEventListener("DOMContentLoaded", () => {
46  // Initialize the UI.
47  const board = document.querySelector(".board");
48  createBoard(board);
49  // Open the WebSocket connection and register event handlers.
50  const websocket = new WebSocket("ws://localhost:8001/");
51  receiveMoves(board, websocket);
52  sendMoves(board, websocket);
53});