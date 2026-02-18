export default function draw(ctx, state) {
    ctx.clearRect(0, 0, 800, 400);

    // background
    ctx.fillStyle = "#F5F8FE";
    ctx.fillRect(0, 0, 800, 400);

    // ground
    ctx.fillStyle = "#7CE396";
    ctx.fillRect(0, 320, 800, 80);

    // net
    ctx.fillStyle = "#F1D37C";
    ctx.fillRect(395, 280, 10, 40);

    // left slime
    ctx.beginPath();
    ctx.arc(state.left.x, state.left.y, 30, Math.PI, 2*Math.PI);
    ctx.fillStyle = "red";
    ctx.fill();

    // right slime
    ctx.beginPath();
    ctx.arc(state.right.x, state.right.y, 30, Math.PI, 2*Math.PI);
    ctx.fillStyle = "blue";
    ctx.fill();

    // ball
    ctx.beginPath();
    ctx.arc(state.ball.x, state.ball.y, 15, 0, 2*Math.PI);
    ctx.fillStyle = "orange";
    ctx.fill();

    // score
    ctx.fillStyle = "black";
    ctx.font = "24px Arial";
    ctx.fillText(state.score[0], 200, 75);
    ctx.fillText(state.score[1], 600, 75);
}