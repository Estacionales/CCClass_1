import {
  COLS,
  ROWS,
  ITEM_TYPES,
  ITEM_ICONS,
  BOMB_RADIUS,
  SLOW_DURATION_MS,
  SLOW_FACTOR,
  createEmptyBoard,
  createPiece,
  collides,
  merge,
  clearLines,
  applyBomb,
  applyLineClear,
  rotateMatrix,
  scoreForClear,
  nextDropInterval,
} from "./game-logic.js";

const CELL = 30;

const canvas = document.getElementById("board");
const ctx = canvas.getContext("2d");
const scoreEl = document.getElementById("score");
const messageEl = document.getElementById("message");
const itemMessageEl = document.getElementById("itemMessage");

let board = createEmptyBoard();
let score = 0;
let gameOver = false;
let dropInterval = 800;
let dropCounter = 0;
let lastTime = 0;
let current = createPiece();
let slowUntil = 0;
let effects = [];
let itemMessageTimer = null;

function showItemMessage(text) {
  itemMessageEl.textContent = text;
  itemMessageEl.classList.remove("show");
  // restart the fade animation
  void itemMessageEl.offsetWidth;
  itemMessageEl.classList.add("show");
  clearTimeout(itemMessageTimer);
  itemMessageTimer = setTimeout(() => {
    itemMessageEl.classList.remove("show");
  }, 1400);
}

function spawnEffect(effect) {
  const durations = { bomb: 400, lineClear: 300, slow: SLOW_DURATION_MS };
  effects.push({ ...effect, start: lastTime, duration: durations[effect.type] });
}

function triggerItem(piece) {
  const { itemType, x, y } = piece;
  if (itemType === ITEM_TYPES.BOMB) {
    const cleared = applyBomb(board, x, y, BOMB_RADIUS);
    score += cleared * 10;
    spawnEffect({ type: "bomb", x, y });
    showItemMessage(`${ITEM_ICONS.bomb} 폭탄 발동!`);
  } else if (itemType === ITEM_TYPES.LINE_CLEAR) {
    const cleared = applyLineClear(board, y);
    if (cleared) score += 50;
    spawnEffect({ type: "lineClear", y });
    showItemMessage(`${ITEM_ICONS.lineClear} 한 줄 삭제!`);
  } else if (itemType === ITEM_TYPES.SLOW) {
    slowUntil = lastTime + SLOW_DURATION_MS;
    spawnEffect({ type: "slow" });
    showItemMessage(`${ITEM_ICONS.slow} 슬로우 발동!`);
  }
  scoreEl.textContent = score;
}

function rotate() {
  if (current.isItem || current.type === "O") return;
  const rotated = rotateMatrix(current.matrix);
  if (!collides(board, current, 0, 0, rotated)) {
    current.matrix = rotated;
  } else if (!collides(board, current, -1, 0, rotated)) {
    current.x -= 1;
    current.matrix = rotated;
  } else if (!collides(board, current, 1, 0, rotated)) {
    current.x += 1;
    current.matrix = rotated;
  }
}

function moveLeft() {
  if (!collides(board, current, -1, 0)) current.x--;
}

function moveRight() {
  if (!collides(board, current, 1, 0)) current.x++;
}

function softDrop() {
  if (!collides(board, current, 0, 1)) {
    current.y++;
    dropCounter = 0;
  } else {
    lockPiece();
  }
}

function hardDrop() {
  while (!collides(board, current, 0, 1)) current.y++;
  lockPiece();
}

function lockPiece() {
  if (current.isItem) {
    triggerItem(current);
  } else {
    merge(board, current);
    const cleared = clearLines(board);
    if (cleared > 0) {
      score += scoreForClear(cleared);
      dropInterval = nextDropInterval(dropInterval, cleared);
      scoreEl.textContent = score;
    }
  }
  current = createPiece();
  if (collides(board, current)) {
    gameOver = true;
    messageEl.textContent = "Game Over";
  }
}

function drawCell(x, y, color) {
  ctx.fillStyle = color;
  ctx.fillRect(x * CELL, y * CELL, CELL, CELL);
  ctx.strokeStyle = "#222";
  ctx.strokeRect(x * CELL, y * CELL, CELL, CELL);
}

function drawItemPiece(piece) {
  const x = piece.x * CELL;
  const y = piece.y * CELL;
  const pulse = 1 + 0.08 * Math.sin(lastTime / 120);
  ctx.save();
  ctx.translate(x + CELL / 2, y + CELL / 2);
  ctx.scale(pulse, pulse);
  ctx.fillStyle = piece.color;
  ctx.shadowColor = piece.color;
  ctx.shadowBlur = 12;
  ctx.beginPath();
  ctx.roundRect(-CELL / 2 + 2, -CELL / 2 + 2, CELL - 4, CELL - 4, 6);
  ctx.fill();
  ctx.shadowBlur = 0;
  ctx.font = `${CELL * 0.7}px sans-serif`;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(ITEM_ICONS[piece.itemType], 0, 1);
  ctx.restore();
}

function drawEffects() {
  effects = effects.filter((e) => lastTime - e.start < e.duration);
  for (const e of effects) {
    const progress = (lastTime - e.start) / e.duration;
    if (e.type === "bomb") {
      const cx = (e.x + 0.5) * CELL;
      const cy = (e.y + 0.5) * CELL;
      const radius = (BOMB_RADIUS + 0.5) * CELL * (0.4 + progress * 1.2);
      ctx.save();
      ctx.globalAlpha = Math.max(0, 1 - progress);
      ctx.fillStyle = "#ff5522";
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    } else if (e.type === "lineClear") {
      ctx.save();
      ctx.globalAlpha = Math.max(0, 1 - progress);
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(0, e.y * CELL, canvas.width, CELL);
      ctx.restore();
    } else if (e.type === "slow") {
      ctx.save();
      ctx.globalAlpha = 0.12;
      ctx.fillStyle = "#3399ff";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.restore();
      ctx.save();
      ctx.fillStyle = "#3399ff";
      ctx.font = "16px sans-serif";
      ctx.textAlign = "left";
      ctx.textBaseline = "top";
      ctx.fillText("SLOW", 8, 8);
      ctx.restore();
    }
  }
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      if (board[r][c]) drawCell(c, r, board[r][c]);
    }
  }
  if (current.isItem) {
    drawItemPiece(current);
  } else {
    current.matrix.forEach((row, r) => {
      row.forEach((val, c) => {
        if (val) drawCell(current.x + c, current.y + r, current.color);
      });
    });
  }
  drawEffects();
}

function update(time = 0) {
  if (gameOver) return;
  const delta = time - lastTime;
  lastTime = time;
  dropCounter += delta;
  const effectiveInterval = time < slowUntil ? dropInterval * SLOW_FACTOR : dropInterval;
  if (dropCounter > effectiveInterval) {
    if (!collides(board, current, 0, 1)) {
      current.y++;
    } else {
      lockPiece();
    }
    dropCounter = 0;
  }
  draw();
  requestAnimationFrame(update);
}

document.addEventListener("keydown", (e) => {
  if (gameOver) return;
  switch (e.key) {
    case "ArrowLeft":
      moveLeft();
      break;
    case "ArrowRight":
      moveRight();
      break;
    case "ArrowDown":
      softDrop();
      break;
    case "ArrowUp":
      rotate();
      break;
    case " ":
      hardDrop();
      break;
    default:
      return;
  }
  e.preventDefault();
});

requestAnimationFrame(update);
