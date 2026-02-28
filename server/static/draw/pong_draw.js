export default function draw(ctx, state) {
    const INTERNAL_WIDTH = 300;
    const INTERNAL_HEIGHT = 150;

    const SCALE_X = 800 / INTERNAL_WIDTH;
    const SCALE_Y = 400 / INTERNAL_HEIGHT;

    // Important: keep pixels sharp
    ctx.imageSmoothingEnabled = false;

    ctx.clearRect(0, 0, 800, 400);

    // background
    ctx.fillStyle = "black";
    ctx.fillRect(0, 0, 800, 400);

    // helper to scale coordinates
    function sx(x) { return x * SCALE_X; }
    function sy(y) { return y * SCALE_Y; }

    // ===== Center dashed line =====
    ctx.fillStyle = "white";
    for (let y = 0; y < INTERNAL_HEIGHT; y += 5) {
        ctx.fillRect(
            sx(INTERNAL_WIDTH / 2),
            sy(y),
            SCALE_X,
            sy(3)
        );
    }

    // ===== Paddles =====
    const PADDLE_WIDTH = 3;
    const PADDLE_HEIGHT = 25;

    // left paddle
    ctx.fillRect(
        sx(state.left.x - PADDLE_WIDTH),
        sy(state.left.y - PADDLE_HEIGHT / 2),
        sx(PADDLE_WIDTH),
        sy(PADDLE_HEIGHT)
    );

    // right paddle
    ctx.fillRect(
        sx(state.right.x),
        sy(state.right.y - PADDLE_HEIGHT / 2),
        sx(PADDLE_WIDTH),
        sy(PADDLE_HEIGHT)
    );

    // ===== Ball =====
    const BALL_SIZE = 3;

    ctx.fillRect(
        sx(state.ball.x - BALL_SIZE / 2),
        sy(state.ball.y - BALL_SIZE / 2),
        sx(BALL_SIZE),
        sy(BALL_SIZE)
    );

    // ===== Pixel Score Digits (same 3×5 font) =====
    const DIGITS = [
        ["111","101","101","101","111"], // 0
        ["010","110","010","010","111"], // 1
        ["111","001","111","100","111"], // 2
        ["111","001","111","001","111"], // 3
        ["101","101","111","001","001"], // 4
        ["111","100","111","001","111"], // 5
        ["111","100","111","101","111"], // 6
        ["111","001","001","001","001"], // 7
        ["111","101","111","101","111"], // 8
        ["111","101","111","001","111"], // 9
    ];

    function drawDigit(digit, gridX, gridY, scale = 2) {
        const pattern = DIGITS[digit];
        for (let row = 0; row < 5; row++) {
            for (let col = 0; col < 3; col++) {
                if (pattern[row][col] === "1") {
                    ctx.fillRect(
                        sx(gridX + col * scale),
                        sy(gridY + row * scale),
                        sx(scale),
                        sy(scale)
                    );
                }
            }
        }
    }

    const centerX = INTERNAL_WIDTH / 2;
    const gap = 10;
    const digitWidth = 3 * 2;

    drawDigit(state.score[0], centerX - gap - digitWidth, 10);
    drawDigit(state.score[1], centerX + gap, 10);
}