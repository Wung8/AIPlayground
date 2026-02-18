// backend/static/play_slime.js

const socket = io();
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

const keys = {};

document.addEventListener("keydown", (e) => {
  keys[e.key] = true;
});
document.addEventListener("keyup", (e) => {
  keys[e.key] = false;
});

function draw(state) {
  ctx.clearRect(0, 0, 800, 400);

  ctx.fillStyle = "#F5F8FE";
  ctx.fillRect(0, 0, 800, 400);

  ctx.fillStyle = "#7CE396";
  ctx.fillRect(0, 320, 800, 80);

  ctx.fillStyle = "#F1D37C";
  ctx.fillRect(395, 280, 10, 40);

  ctx.beginPath();
  ctx.arc(state.left.x, state.left.y, 30, Math.PI, 2 * Math.PI);
  ctx.fillStyle = "red";
  ctx.fill();

  ctx.beginPath();
  ctx.arc(state.right.x, state.right.y, 30, Math.PI, 2 * Math.PI);
  ctx.fillStyle = "blue";
  ctx.fill();

  ctx.beginPath();
  ctx.arc(state.ball.x, state.ball.y, 15, 0, 2 * Math.PI);
  ctx.fillStyle = "orange";
  ctx.fill();

  ctx.fillStyle = "black";
  ctx.font = "24px Arial";
  ctx.fillText(state.score[0], 200, 75);
  ctx.fillText(state.score[1], 600, 75);
}

let lastTime = 0;
const maxAllowedTime = 1000 * 1;
const fps = 20;
const frameDuration = 1000 / fps;

function gameLoop(currentTime) {
  if (currentTime - lastTime >= frameDuration) {
    if (currentTime - lastTime > maxAllowedTime) lastTime = currentTime;

    socket.emit("input", {
      action: keys,
      env_slug: window.__ENV_SLUG__ || "slimevolleyball",
    });

    lastTime += frameDuration;
  }
  requestAnimationFrame(gameLoop);
}

socket.on("state", (state) => {
  draw(state);
});

gameLoop(performance.now());

// optional hooks
const btnReset = document.getElementById("btnReset");
if (btnReset) {
  btnReset.addEventListener("click", () => socket.emit("reset", { env_slug: window.__ENV_SLUG__ }));
}
