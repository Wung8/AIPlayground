export default function draw(ctx, state) {
    const grid = state.grid;

    const GRID_W = grid.length;
    const GRID_H = grid[0].length;

    // scale to fill 800x400
    const SCALE_X = 800 / GRID_W;
    const SCALE_Y = 400 / GRID_H;

    ctx.imageSmoothingEnabled = false;
    ctx.clearRect(0, 0, 800, 400);

    function color(arr) {
        return `rgb(${Math.floor(arr[0])},${Math.floor(arr[1])},${Math.floor(arr[2])})`;
    }

    // Draw background first
    ctx.fillStyle = color(state.colors.bg);
    ctx.fillRect(0, 0, 800, 400);

    // Draw maze tiles
    for (let x = 0; x < GRID_W; x++) {
        for (let y = 0; y < GRID_H; y++) {

            let fill = null;

            if (grid[x][y] === 1) {
                fill = color(state.colors.wall);
            }

            if (fill) {
                ctx.fillStyle = fill;
                ctx.fillRect(
                    Math.floor(x * SCALE_X),
                    Math.floor(y * SCALE_Y),
                    Math.ceil(SCALE_X),
                    Math.ceil(SCALE_Y)
                );
            }
        }
    }

    const [px, py] = state.player;
    const [gx, gy] = state.goal;

    const complete = (px === gx && py === gy);

    // Draw goal
    ctx.fillStyle = color(state.colors.goal);
    ctx.fillRect(
        Math.floor(gx * SCALE_X),
        Math.floor(gy * SCALE_Y),
        Math.ceil(SCALE_X),
        Math.ceil(SCALE_Y)
    );

    // Draw player (overwrites goal if complete)
    ctx.fillStyle = complete
        ? color(state.colors.complete)
        : color(state.colors.player);

    ctx.fillRect(
        Math.floor(px * SCALE_X),
        Math.floor(py * SCALE_Y),
        Math.ceil(SCALE_X),
        Math.ceil(SCALE_Y)
    );
}