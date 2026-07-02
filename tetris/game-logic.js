// Pure game-logic module: no DOM access, shared by the browser UI (script.js)
// and the Node test suite (tests/game-logic.test.js).

export const COLS = 10;
export const ROWS = 20;

export const SHAPES = {
  I: [
    [0, 0, 0, 0],
    [1, 1, 1, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
  ],
  O: [
    [1, 1],
    [1, 1],
  ],
  T: [
    [0, 1, 0],
    [1, 1, 1],
    [0, 0, 0],
  ],
  S: [
    [0, 1, 1],
    [1, 1, 0],
    [0, 0, 0],
  ],
  Z: [
    [1, 1, 0],
    [0, 1, 1],
    [0, 0, 0],
  ],
  J: [
    [1, 0, 0],
    [1, 1, 1],
    [0, 0, 0],
  ],
  L: [
    [0, 0, 1],
    [1, 1, 1],
    [0, 0, 0],
  ],
};

export const COLORS = {
  I: "#00f0f0",
  O: "#f0f000",
  T: "#a000f0",
  S: "#00f000",
  Z: "#f00000",
  J: "#0000f0",
  L: "#f0a000",
};

export const ITEM_TYPES = {
  BOMB: "bomb",
  LINE_CLEAR: "lineClear",
  SLOW: "slow",
};

export const ITEM_COLORS = {
  [ITEM_TYPES.BOMB]: "#ff5522",
  [ITEM_TYPES.LINE_CLEAR]: "#00ffaa",
  [ITEM_TYPES.SLOW]: "#3399ff",
};

export const ITEM_ICONS = {
  [ITEM_TYPES.BOMB]: "\u{1F4A3}", // 💣
  [ITEM_TYPES.LINE_CLEAR]: "⚡", // ⚡
  [ITEM_TYPES.SLOW]: "\u{1F40C}", // 🐌
};

export const ITEM_CHANCE = 0.12;
export const BOMB_RADIUS = 1;
export const SLOW_DURATION_MS = 6000;
export const SLOW_FACTOR = 1.8;

export function createEmptyBoard(cols = COLS, rows = ROWS) {
  return Array.from({ length: rows }, () => Array(cols).fill(0));
}

export function randomPieceType(rng = Math.random) {
  const types = Object.keys(SHAPES);
  return types[Math.floor(rng() * types.length)];
}

export function randomItemType(rng = Math.random) {
  const types = Object.values(ITEM_TYPES);
  return types[Math.floor(rng() * types.length)];
}

export function createPiece(rng = Math.random, cols = COLS) {
  if (rng() < ITEM_CHANCE) {
    const itemType = randomItemType(rng);
    const matrix = [[1]];
    return {
      type: "ITEM",
      isItem: true,
      itemType,
      matrix,
      color: ITEM_COLORS[itemType],
      x: Math.floor((cols - matrix[0].length) / 2),
      y: 0,
    };
  }
  const type = randomPieceType(rng);
  const matrix = SHAPES[type].map((row) => row.slice());
  return {
    type,
    isItem: false,
    matrix,
    color: COLORS[type],
    x: Math.floor((cols - matrix[0].length) / 2),
    y: 0,
  };
}

export function collides(board, piece, offsetX = 0, offsetY = 0, matrix = piece.matrix) {
  const rows = board.length;
  const cols = board[0].length;
  for (let r = 0; r < matrix.length; r++) {
    for (let c = 0; c < matrix[r].length; c++) {
      if (!matrix[r][c]) continue;
      const boardX = piece.x + c + offsetX;
      const boardY = piece.y + r + offsetY;
      if (boardX < 0 || boardX >= cols || boardY >= rows) return true;
      if (boardY >= 0 && board[boardY][boardX]) return true;
    }
  }
  return false;
}

export function merge(board, piece) {
  piece.matrix.forEach((row, r) => {
    row.forEach((val, c) => {
      if (val && piece.y + r >= 0) {
        board[piece.y + r][piece.x + c] = piece.color;
      }
    });
  });
}

// Clears every fully-filled row, shifting the remaining rows down and
// padding empty rows in at the top. Mutates `board` in place.
export function clearLines(board) {
  const cols = board[0].length;
  let cleared = 0;
  for (let r = board.length - 1; r >= 0; r--) {
    if (board[r].every((cell) => cell)) {
      board.splice(r, 1);
      board.unshift(Array(cols).fill(0));
      cleared++;
      r++;
    }
  }
  return cleared;
}

// Bomb item: clears only the (2*radius+1)^2 square centered on (cx, cy),
// leaving everything outside that blast area untouched.
export function applyBomb(board, cx, cy, radius = BOMB_RADIUS) {
  const rows = board.length;
  const cols = board[0].length;
  let cleared = 0;
  for (let y = cy - radius; y <= cy + radius; y++) {
    if (y < 0 || y >= rows) continue;
    for (let x = cx - radius; x <= cx + radius; x++) {
      if (x < 0 || x >= cols) continue;
      if (board[y][x]) cleared++;
      board[y][x] = 0;
    }
  }
  return cleared;
}

// Line-clear item: removes a single specific row regardless of whether
// it is full, shifting rows above it down by one.
export function applyLineClear(board, row) {
  if (row < 0 || row >= board.length) return 0;
  const cols = board[0].length;
  board.splice(row, 1);
  board.unshift(Array(cols).fill(0));
  return 1;
}

export function rotateMatrix(matrix) {
  const n = matrix.length;
  const result = [];
  for (let r = 0; r < n; r++) {
    result.push([]);
    for (let c = 0; c < n; c++) {
      result[r][c] = matrix[n - 1 - c][r];
    }
  }
  return result;
}

export function scoreForClear(cleared) {
  const points = [0, 100, 300, 500, 800];
  return points[cleared] || cleared * 100;
}

export function nextDropInterval(current, cleared) {
  return Math.max(100, current - cleared * 20);
}
