export function draw(ctx, state) {
    const W = 900;
    const H = 600;

    ctx.clearRect(0, 0, W, H);

    // =====================
    // Background
    // =====================
    ctx.fillStyle = "rgb(93,127,102)";
    ctx.fillRect(0, 0, W, H);

    // Diagonal grass stripes
    for (let i = 0; i < 21; i++) {
        const offset = 65;
        ctx.strokeStyle = "rgb(96,130,105)";
        ctx.lineWidth = 30;
        ctx.beginPath();
        ctx.moveTo(i * offset, 0);
        ctx.lineTo(i * offset - 600, 600);
        ctx.stroke();
    }

    // Field masking
    ctx.fillStyle = "rgb(93,127,102)";
    ctx.fillRect(0, 0, 900, 100);
    ctx.fillRect(0, 0, 50, 600);
    ctx.fillRect(850, 0, 50, 600);
    ctx.fillRect(0, 500, 900, 100);

    // =====================
    // Field lines
    // =====================
    ctx.strokeStyle = "rgb(120,152,128)";
    ctx.lineWidth = 2;

    // Outer box
    ctx.strokeRect(50, 100, 800, 400);

    // Mid line
    ctx.beginPath();
    ctx.moveTo(450, 100);
    ctx.lineTo(450, 500);
    ctx.stroke();

    // Goal boxes
    ctx.strokeRect(50, 150, 75, 300);
    ctx.strokeRect(775, 150, 75, 300);

    // Center circle
    ctx.beginPath();
    ctx.arc(450, 300, 75, 0, Math.PI * 2);
    ctx.stroke();

    // Goal posts
    const posts = [
        [50, 225],
        [50, 375],
        [850, 225],
        [850, 375]
    ];

    ctx.fillStyle = "rgb(120,152,128)";
    posts.forEach(([x, y]) => {
        ctx.beginPath();
        ctx.arc(x, y, 13, 0, Math.PI * 2);
        ctx.fill();
    });

    // =====================
    // Ball
    // =====================
    ctx.fillStyle = "white";
    ctx.beginPath();
    ctx.arc(state.ball.x, state.ball.y, 11, 0, Math.PI * 2);
    ctx.fill();

    // =====================
    // Players
    // =====================
    state.players.forEach((p, i) => {
        let color;

        // Left team (blue)
        if (i < 2) {
            color = p.kicking ? "rgb(75,125,200)" : "rgb(94,156,243)";
        }
        // Right team (red)
        else {
            color = p.kicking ? "rgb(150,100,70)" : "rgb(195,135,95)";
        }

        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.kicking ? 17 : 15, 0, Math.PI * 2);
        ctx.fill();
    });
}