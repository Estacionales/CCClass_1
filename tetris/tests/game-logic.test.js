import { test } from "node:test";
import assert from "node:assert/strict";
import { createEmptyBoard, clearLines, applyBomb } from "../game-logic.js";

test("줄이 꽉 차면 지워진다: a fully filled row is cleared", () => {
  const board = createEmptyBoard(4, 3);
  // fill the bottom row completely, leave the rest empty
  board[2] = ["#f00", "#f00", "#f00", "#f00"];

  const cleared = clearLines(board);

  assert.equal(cleared, 1);
  assert.equal(board.length, 3, "row count is preserved (empty row shifted in at top)");
  assert.ok(
    board.every((row) => !row.every((cell) => cell)),
    "no row remains fully filled after clearing"
  );
  assert.deepEqual(board[2], [0, 0, 0, 0], "cleared row is replaced with an empty row");
});

test("줄이 꽉 차면 지워진다: a partially filled row is left untouched", () => {
  const board = createEmptyBoard(4, 3);
  board[2] = ["#f00", "#f00", "#f00", 0];

  const cleared = clearLines(board);

  assert.equal(cleared, 0);
  assert.deepEqual(board[2], ["#f00", "#f00", "#f00", 0]);
});

test("폭탄은 주변만 지운다: bomb only clears the 3x3 blast area", () => {
  const board = createEmptyBoard(6, 6).map((row) => row.map(() => "#0f0"));
  const cx = 3;
  const cy = 3;

  const cleared = applyBomb(board, cx, cy, 1);

  assert.equal(cleared, 9, "a full 3x3 blast area was filled before the bomb, so 9 cells clear");
  for (let y = 0; y < 6; y++) {
    for (let x = 0; x < 6; x++) {
      const withinBlast = Math.abs(x - cx) <= 1 && Math.abs(y - cy) <= 1;
      if (withinBlast) {
        assert.equal(board[y][x], 0, `(${x},${y}) inside blast radius should be cleared`);
      } else {
        assert.equal(board[y][x], "#0f0", `(${x},${y}) outside blast radius should be untouched`);
      }
    }
  }
});

test("폭탄은 주변만 지운다: blast area is clipped at the board edges", () => {
  const board = createEmptyBoard(4, 4).map((row) => row.map(() => "#00f"));

  const cleared = applyBomb(board, 0, 0, 1);

  // only the 2x2 corner exists on the board for a radius-1 blast at (0,0)
  assert.equal(cleared, 4);
  assert.equal(board[0][0], 0);
  assert.equal(board[0][1], 0);
  assert.equal(board[1][0], 0);
  assert.equal(board[1][1], 0);
  assert.equal(board[2][2], "#00f", "cells outside the clipped blast remain untouched");
});
