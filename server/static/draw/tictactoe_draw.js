export default function draw(ctx, state) {

    const SIZE = 300;
    const CELL = SIZE / 3;

    const offsetX = (800 - SIZE) / 2;
    const offsetY = (400 - SIZE) / 2;

    ctx.clearRect(0, 0, 800, 400);

    // Paper background
    ctx.fillStyle = "rgb(230,225,210)";
    ctx.fillRect(0, 0, 800, 400);

    const { grid, cursor, turn, sketch } = state;

    function sketchLine(x1, y1, x2, y2, key, thickness = 2) {
        const j1 = sketch[key + "_1"] || [0, 0];
        const j2 = sketch[key + "_2"] || [0, 0];

        ctx.lineWidth = thickness;
        ctx.strokeStyle = "rgb(60,60,60)";
        ctx.lineCap = "round";

        ctx.beginPath();
        ctx.moveTo(x1 + j1[0], y1 + j1[1]);
        ctx.lineTo(x2 + j2[0], y2 + j2[1]);
        ctx.stroke();
    }

    // -------------------
    // Grid
    // -------------------
    for (let i = 0; i <= 3; i++) {
        let x = offsetX + i * CELL;
        let y = offsetY + i * CELL;

        sketchLine(x, offsetY, x, offsetY + SIZE, `v${i}`);
        sketchLine(offsetX, y, offsetX + SIZE, y, `h${i}`);
    }

    // -------------------
    // Marks
    // -------------------
    for (let r = 0; r < 3; r++) {
        for (let c = 0; c < 3; c++) {

            const val = grid[r][c];
            const cx = offsetX + c * CELL + CELL / 2;
            const cy = offsetY + r * CELL + CELL / 2;

            const idx = r * 3 + c;

            if (val === "x") {
                const size = CELL / 3;

                sketchLine(
                    cx - size, cy - size,
                    cx + size, cy + size,
                    `x${idx}a`, 3
                );

                sketchLine(
                    cx - size, cy + size,
                    cx + size, cy - size,
                    `x${idx}b`, 3
                );
            }

            if (val === "o") {
                const jitter = sketch[`o${idx}`] || [0, 0];

                ctx.lineWidth = 2;
                ctx.strokeStyle = "rgb(60,60,60)";
                ctx.beginPath();
                ctx.arc(
                    cx + jitter[0],
                    cy + jitter[1],
                    CELL / 3,
                    0,
                    Math.PI * 2
                );
                ctx.stroke();
            }
        }
    }

    // -------------------
    // Cursor
    // -------------------
    const [row, col] = cursor;

    const x1 = offsetX + col * CELL;
    const y1 = offsetY + row * CELL;
    const x2 = x1 + CELL;
    const y2 = y1 + CELL;

    const cursorColor =
        turn === "x"
            ? "rgba(200,80,80,0.15)"
            : "rgba(80,120,200,0.15)";

    ctx.fillStyle = cursorColor;
    ctx.fillRect(x1, y1, CELL, CELL);

    sketchLine(x1, y1, x2, y1, "c1");
    sketchLine(x2, y1, x2, y2, "c2");
    sketchLine(x2, y2, x1, y2, "c3");
    sketchLine(x1, y2, x1, y1, "c4");

    // -------------------
    // Turn text
    // -------------------
    ctx.fillStyle = "rgb(70,70,70)";
    ctx.font = "28px Arial";
    ctx.textAlign = "left";
    ctx.fillText(
        turn === "x" ? "X's Turn" : "O's Turn",
        40,
        50
    );
}