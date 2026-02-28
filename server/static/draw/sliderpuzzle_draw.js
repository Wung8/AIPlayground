export default function draw(ctx, state) {
    const N = 5;

    // Fit board into 400px height cleanly
    const TILE_SIZE = 60;
    const PADDING = 8;
    const BOARD_SIZE = N * TILE_SIZE + (N + 1) * PADDING;

    const offsetX = (800 - BOARD_SIZE) / 2;
    const offsetY = (400 - BOARD_SIZE) / 2;

    ctx.clearRect(0, 0, 800, 400);

    // Background
    //ctx.fillStyle = "rgb(75,55,50)";
    //ctx.fillRect(0, 0, 800, 400);

    ctx.fillStyle = "rgb(120,80,40)";
    ctx.fillRect(offsetX, offsetY, BOARD_SIZE, BOARD_SIZE);

    const grid = state.grid;
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

                offset_x = -(tileIndex % 5 - hole % 5) * dist;
                offset_y = -(Math.floor(tileIndex / 5) - Math.floor(hole / 5)) * dist;
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
                ctx.lineWidth = 3;
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
                ctx.fillText(value, x + TILE_SIZE / 2 - 2, y + TILE_SIZE / 2 + 2);
            }
        }
    }

}