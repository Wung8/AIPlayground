export default function draw(ctx, state) {
    const CANVAS_W = 800;
    const CANVAS_H = 400;

    const BASE_W = 900;
    const BASE_H = 600;

    // =====================================
    // Adjustable zoom (EDIT THIS VALUE)
    // 1.0 = normal
    // 1.1 = 10% bigger
    // 1.2 = 20% bigger, etc.
    // =====================================
    const ZOOM = 1.15; 

    // Base scale (fit height)
    const baseScale = CANVAS_H / BASE_H;

    // Final scale
    const scale = baseScale * ZOOM;

    const fieldW = BASE_W * scale;
    const fieldH = BASE_H * scale;

    const offsetX = (CANVAS_W - fieldW) / 2;
    const offsetY = (CANVAS_H - fieldH) / 2; // center vertically too

    // Clear canvas
    ctx.clearRect(0, 0, CANVAS_W, CANVAS_H);

    // Fill background
    ctx.fillStyle = "rgb(93,127,102)";
    ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);

    // Save and scale
    ctx.save();
    ctx.translate(offsetX, offsetY);
    ctx.scale(scale, scale);

    // =====================
    // Diagonal grass stripes
    // =====================
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
    // Top strip
    ctx.fillRect(0, 0, BASE_W, 100);

    // Bottom strip
    ctx.fillRect(0, 500, BASE_W, 100);

    // Left strip
    ctx.fillRect(-100, 0, 150, 600);

    // Right strip
    ctx.fillRect(850, 0, 150, 600);

    // =====================
    // Field lines
    // =====================
    ctx.strokeStyle = "rgb(120,152,128)";
    ctx.lineWidth = 2;

    ctx.strokeRect(50, 100, 800, 400);

    ctx.beginPath();
    ctx.moveTo(450, 100);
    ctx.lineTo(450, 500);
    ctx.stroke();

    ctx.strokeRect(50, 150, 75, 300);
    ctx.strokeRect(775, 150, 75, 300);

    ctx.beginPath();
    ctx.arc(450, 300, 75, 0, Math.PI * 2);
    ctx.stroke();

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
        if (i < 2) {
            color = p.kicking
                ? "rgb(75,125,200)"
                : "rgb(94,156,243)";
        } else {
            color = p.kicking
                ? "rgb(150,100,70)"
                : "rgb(195,135,95)";
        }

        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(
            p.x,
            p.y,
            p.kicking ? 17 : 15,
            0,
            Math.PI * 2
        );
        ctx.fill();
    });

    // score
    ctx.font = "32px Arial";
    ctx.textAlign = "center"; 
    ctx.textBaseline = "middle";
    ctx.fillStyle = "rgb(94,156,243)";
    ctx.fillText(state.score[0], 400, 75);
    ctx.fillStyle = "rgb(195,135,95)"
    ctx.fillText(state.score[1], 500, 75);
    ctx.fillStyle = "white"
    ctx.fillText("-", 450, 75);

    ctx.restore();
}
