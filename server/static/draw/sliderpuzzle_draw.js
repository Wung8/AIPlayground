export default function draw(ctx, state) {
    const canvasWidth = 800;
    const canvasHeight = 400;

    const grid = state.grid;
    const N = Math.sqrt(grid.length);   // ← dynamic board size

    const PADDING = 8;

    // Compute tile size so board always fits inside canvas
    const maxBoardSize = Math.min(canvasHeight, canvasWidth);
    const TILE_SIZE = Math.floor(
        (maxBoardSize - (N + 1) * PADDING) / N
    );

    const BOARD_SIZE = N * TILE_SIZE + (N + 1) * PADDING;

    const offsetX = (canvasWidth - BOARD_SIZE) / 2;
    const offsetY = (canvasHeight - BOARD_SIZE) / 2;

    ctx.clearRect(0, 0, canvasWidth, canvasHeight);

    // Board background
    ctx.fillStyle = "rgb(120,80,40)";
    ctx.fillRect(offsetX, offsetY, BOARD_SIZE, BOARD_SIZE);

    const hole = grid.indexOf(0);

    for (let i = 0; i < N; i++) {
        for (let j = 0; j < N; j++) {

            const tileIndex = i * N + j;
            const value = grid[tileIndex];

            let offset_x = 0;
            let offset_y = 0;

            if (
                state.moving_tile !== null &&
                tileIndex === state.moving_tile &&
                state.animation_tick > 0
            ) {
                const t = state.animation_tick / state.animation;
                const dist = (TILE_SIZE + PADDING) * (t * t);

                const holeRow = Math.floor(hole / N);
                const holeCol = hole % N;

                offset_x = -(j - holeCol) * dist;
                offset_y = -(i - holeRow) * dist;
            }

            const x = offsetX + PADDING + j * (TILE_SIZE + PADDING) + offset_x;
            const y = offsetY + PADDING + i * (TILE_SIZE + PADDING) + offset_y;

            if (value !== 0) {

                // Shadow
                ctx.fillStyle = "rgb(60,40,20)";
                ctx.fillRect(x + 4, y + 4, TILE_SIZE, TILE_SIZE);

                // Tile
                ctx.fillStyle = "rgb(180,120,60)";
                ctx.fillRect(x, y, TILE_SIZE, TILE_SIZE);

                // Bevel highlight
                ctx.strokeStyle = "rgb(200,150,100)";
                ctx.lineWidth = Math.max(2, TILE_SIZE * 0.05);
                ctx.beginPath();
                ctx.moveTo(x, y + TILE_SIZE);
                ctx.lineTo(x, y);
                ctx.lineTo(x + TILE_SIZE, y);
                ctx.stroke();

                // Bevel shadow
                ctx.strokeStyle = "rgb(30,30,30)";
                ctx.beginPath();
                ctx.moveTo(x, y + TILE_SIZE);
                ctx.lineTo(x + TILE_SIZE, y + TILE_SIZE);
                ctx.lineTo(x + TILE_SIZE, y);
                ctx.stroke();

                // Number
                ctx.fillStyle = "rgb(30,30,30)";
                ctx.font = `${TILE_SIZE * 0.45}px Arial`;
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillText(value, x + TILE_SIZE / 2, y + TILE_SIZE / 2);
            }
        }
    }
}