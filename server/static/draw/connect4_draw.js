const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

const WIDTH = 800;
const HEIGHT = 400;

canvas.width = WIDTH;
canvas.height = HEIGHT;

const COLS = 7;
const ROWS = 6;

const CELL_W = 66;
const CELL_H = 66;
const OFFSET_X = (WIDTH - COLS * CELL_W) / 2;

// Colors (match your Python style)
const boardColor = "rgb(61,66,92)";
const emptyColor = "rgb(45,45,55)";
const xColor = "rgb(120,200,255)";
const oColor = "rgb(255,200,120)";

function blend(c1, c2) {
    return c1.map((v, i) => Math.floor((v + c2[i]) / 2));
}

function drawCircle(x, y, r, color) {
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
}

export default function draw(ctx, state) {
    const grid = state.grid;
    const player = state.player;
    const pending = state.pending_move;


    // Background
    ctx.fillStyle = boardColor;
    ctx.fillRect(0, 0, WIDTH, HEIGHT);

    // Draw board
    for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
            const x = OFFSET_X + c * CELL_W + CELL_W / 2;
            const y = r * CELL_H + CELL_H / 2;
            const radius = Math.min(CELL_W, CELL_H) / 3;

            // empty slot
            drawCircle(x, y, radius, emptyColor);

            const val = grid[r][c];

            if (val === "x") {
                drawCircle(x, y, radius, xColor);
            } else if (val === "o") {
                drawCircle(x, y, radius, oColor);
            }
        }
    }

    // Ghost piece (hover)
    let dropRow = ROWS;
    for (let r = 0; r < ROWS; r++) {
        if (grid[r][pending] !== ".") {
            dropRow = r;
            break;
        }
    }

    if (dropRow !== 0) {
        let r = dropRow === ROWS ? ROWS - 1 : dropRow - 1;

        const x = OFFSET_X + pending * CELL_W + CELL_W / 2;
        const y = r * CELL_H + CELL_H / 2;
        const radius = Math.min(CELL_W, CELL_H) / 3;

        const base = player === "o" ? [255,200,120] : [120,200,255];
        const empty = [45,45,55];
        const blended = blend(base, empty);

        drawCircle(x, y, radius, `rgb(${blended.join(",")})`);
    }

    // Player text
    //ctx.fillStyle = "white";
    //ctx.font = "20px sans-serif";
    //ctx.fillText(`Player: ${player}`, 10, 25);


    }

    // Example hook (you probably already have something like this)
    window.renderGame = function(state) {
        draw(state);
    };
