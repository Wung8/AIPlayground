export default function draw(ctx, state) {

    const SIZE = 360; // half of 720 to fit in 400px canvas
    const CELL = SIZE / 9;

    const offsetX = (800 - SIZE) / 2;
    const offsetY = (400 - SIZE) / 2;

    ctx.clearRect(0, 0, 800, 400);

    // Background (OpenCV used 235 gray)
    ctx.fillStyle = "rgb(235,235,235)";
    ctx.fillRect(offsetX, offsetY, SIZE, SIZE);

    const grid = state.grid;
    const original = state.original;
    const [r, c] = state.cursor;

    let hovered_num = grid[r][c];
    if (hovered_num === 0) hovered_num = null;

    // -----------------------
    // 3x3 Box Shading
    // -----------------------
    for (let box_r = 0; box_r < 3; box_r++) {
        for (let box_c = 0; box_c < 3; box_c++) {
            if ((box_r + box_c) % 2 === 0) {
                ctx.fillStyle = "rgb(220,220,220)";
                ctx.fillRect(
                    offsetX + box_c * 3 * CELL,
                    offsetY + box_r * 3 * CELL,
                    3 * CELL,
                    3 * CELL
                );
            }
        }
    }

    // Row/Column highlight
    const primary = "rgb(100,180,160)";     // converted from BGR(160,180,100)
    const secondary = "rgb(170,210,200)";   // from BGR(200,210,170)

    ctx.fillStyle = secondary;
    for (let i = 0; i < 9; i++) {
        ctx.fillRect(offsetX + c * CELL, offsetY + i * CELL, CELL, CELL);
        ctx.fillRect(offsetX + i * CELL, offsetY + r * CELL, CELL, CELL);
    }

    // Same number highlight
    if (hovered_num !== null) {
        ctx.fillStyle = "rgb(200,150,200)"; // BGR(200,150,200) symmetric
        for (let i = 0; i < 9; i++) {
            for (let j = 0; j < 9; j++) {
                if (grid[i][j] === hovered_num) {
                    ctx.fillRect(offsetX + j * CELL, offsetY + i * CELL, CELL, CELL);
                }
            }
        }
    }

    // Primary cursor
    ctx.fillStyle = primary;
    ctx.fillRect(offsetX + c * CELL, offsetY + r * CELL, CELL, CELL);

    // -----------------------
    // Grid Lines
    // -----------------------
    ctx.strokeStyle = "rgb(80,80,80)";
    for (let i = 0; i <= 9; i++) {
        ctx.lineWidth = (i % 3 === 0) ? 3 : 1;

        // horizontal
        ctx.beginPath();
        ctx.moveTo(offsetX, offsetY + i * CELL);
        ctx.lineTo(offsetX + SIZE, offsetY + i * CELL);
        ctx.stroke();

        // vertical
        ctx.beginPath();
        ctx.moveTo(offsetX + i * CELL, offsetY);
        ctx.lineTo(offsetX + i * CELL, offsetY + SIZE);
        ctx.stroke();
    }

    // -----------------------
    // Numbers
    // -----------------------
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.font = `${CELL * 0.6}px Arial`;

    function hasConflict(row, col) {
        const val = grid[row][col];
        if (val === 0) return false;

        for (let i = 0; i < 9; i++) {
            if (i !== col && grid[row][i] === val) return true;
            if (i !== row && grid[i][col] === val) return true;
        }

        const box_r = Math.floor(row / 3) * 3;
        const box_c = Math.floor(col / 3) * 3;

        for (let i = box_r; i < box_r + 3; i++) {
            for (let j = box_c; j < box_c + 3; j++) {
                if ((i !== row || j !== col) && grid[i][j] === val)
                    return true;
            }
        }

        return false;
    }

    for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
            const val = grid[i][j];
            if (val !== 0) {

                let color;

                if (original[i][j] !== 0) {
                    color = "rgb(20,20,20)";
                } else {
                    if (hasConflict(i, j)) {
                        color = "rgb(200,40,40)";  // from BGR(40,40,200)
                    } else {
                        color = "rgb(0,60,200)";   // from BGR(200,60,0)
                    }
                }

                ctx.fillStyle = color;
                ctx.fillText(
                    val,
                    offsetX + j * CELL + CELL / 2,
                    offsetY + i * CELL + CELL / 2
                );
            }
        }
    }

    // Solved overlay
    if (state.solved) {
        ctx.fillStyle = "rgba(255,255,120,0.25)";
        ctx.fillRect(offsetX, offsetY, SIZE, SIZE);
    }
}