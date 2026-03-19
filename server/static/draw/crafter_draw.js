const TILE = 36;
const SCALE = TILE / 8;

const sprites = {};
let loaded = false;

// include ALL needed sprites
const files = {
    cursor: "cursor.png",

    water: "water.png",
    grass: "grass.png",
    grass_shadow: "grass_shadow.png",
    stone: "stone.png",
    stone_shadow: "stone_shadow.png",
    plank: "plank.png",
    wall: "stone_wall.png",
    diamond: "diamond.png",

    tree_0: "tree_0.png",
    tree_1: "tree_1.png",
    tree_2: "tree_2.png",
    tree_3: "tree_3.png",
    tree_4: "tree_4.png",

    bush: "bush.png",
    berry_bush: "berry_bush.png",

    player: "player.png",
    enemy: "bad_guy.png",
    enemy_attack: "bad_guy_attack.png",
    enemy_attack2: "bad_guy_attack_fin.png",

    info_bar: "info_bar.png",
    score_bar: "score_bar.png",
    crafting_bar: "crafting_bar.png",

    stick_icon: "stick_icon.png",
    stone_icon: "stone_icon.png",

    wood_pickaxe: "wood_pickaxe.png",
    stone_pickaxe: "stone_pickaxe.png",
    wood_sword: "wood_sword.png",
    stone_sword: "stone_sword.png",

    // numbers
    num0: "0.png",
    num1: "1.png",
    num2: "2.png",
    num3: "3.png",
    num4: "4.png",
    num5: "5.png",
    num6: "6.png",
    num7: "7.png",
    num8: "8.png",
    num9: "9.png",
};

function load() {
    if (loaded) return;

    let count = 0;
    const total = Object.keys(files).length;

    for (const k in files) {
        const img = new Image();
        img.src = `/static/sprites/crafter/${files[k]}`;

        img.onload = () => {
            count++;
            if (count === total) loaded = true;
        };

        img.onerror = () => console.error("missing", img.src);

        sprites[k] = img;
    }
}

function drawNumber(ctx, n, x, y) {
    const img = sprites["num" + n];
    drawSprite(ctx, img, x, y);
}

function drawSprite(ctx, img, x, y) {
    const scale = TILE / 8; // since original sprites are 8px-based

    const w = img.width * scale;
    const h = img.height * scale;

    ctx.drawImage(img, x, y - (h - TILE), w, h);
}

function drawFlipped(ctx, img, x, y) {
    ctx.save();

    const scale = TILE / 8;
    const w = img.width * scale;

    ctx.scale(-1, 1);

    // flip around the sprite's left edge
    drawSprite(ctx, img, -x - w, y);

    ctx.restore();
}

function drawBrightened(ctx, img, x, y) {
    ctx.save();

    drawSprite(ctx, img, x, y);

    ctx.globalCompositeOperation = "lighter";
    ctx.globalAlpha = 0.5;
    drawSprite(ctx, img, x, y);

    ctx.globalAlpha = 1;
    ctx.globalCompositeOperation = "source-over";

    ctx.restore();
}


export default function draw(ctx, state) {
    ctx.setTransform(1, 0, 0, 1, 0, 0); 
    load();
    if (!loaded) return;

    ctx.imageSmoothingEnabled = false;
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

    ctx.fillStyle = "rgb(20,20,20)";
    ctx.fillRect(0, 0, 800, 400);

    ctx.translate((800-400*9/12)/2, TILE);
    ctx.fillStyle = "rgb(40,40,40)";
    ctx.fillRect(0, -TILE, 400*9/12, 400);

    const tiles = state.tiles;
    const pre = state.pre_tick;

    // --- tiles ---
    for (let y = 0; y < tiles.length; y++) {

        // --- draw ground first ---
        for (let x = 0; x < tiles[y].length; x++) {

            const hasEnemy = state.enemies.some(e => e.x === x && e.y === y);
            const isPlayer = (state.player.x === x && state.player.y === y);

            const tile = tiles[y][x];
            if (!tile) continue;

            const px = x * TILE;
            const py = y * TILE;

            if (tile.water)
                drawSprite(ctx, sprites.water, px, py, TILE, TILE);

            if (tile.grass)
                drawSprite(ctx, 
                    (tile.tree || tile.bush || tile.plank || hasEnemy || isPlayer)
                        ? sprites.grass_shadow
                        : sprites.grass,
                    px, py, TILE, TILE
                );

            if (tile.stone)
                drawSprite(ctx, 
                    (hasEnemy || isPlayer)
                        ? sprites.stone_shadow
                        : sprites.stone,
                    px, py, TILE, TILE
                );
        }

        // --- draw objects second ---
        for (let x = 0; x < tiles[y].length; x++) {
            const tile = tiles[y][x];
            if (!tile) continue;

            const px = x * TILE;
            const py = y * TILE;

            if (tile.plank) {
                if (pre && tile.damage)
                    drawBrightened(ctx, sprites.plank, px, py, TILE, TILE);
                else
                    drawSprite(ctx, sprites.plank, px, py, TILE, TILE);
            }

            if (tile.wall) {
                if (pre && tile.damage)
                    drawBrightened(ctx, sprites.wall, px, py, TILE, TILE);
                else
                    drawSprite(ctx, sprites.wall, px, py, TILE, TILE);
            }

            if (tile.diamond) {
                if (pre && tile.damage)
                    drawBrightened(ctx, sprites.diamond, px, py, TILE, TILE);
                else
                    drawSprite(ctx, sprites.diamond, px, py, TILE, TILE);
            }

            if (tile.tree) {
                const key = `tree_${tile.tree_id}`;
                if (pre && tile.damage)
                    drawBrightened(ctx, sprites[key], px, py, TILE, TILE);
                else
                    drawSprite(ctx, sprites[key], px, py, TILE, TILE);
            }

            if (tile.bush) {
                const bush = tile.berry ? "berry_bush" : "bush";
                if (pre && tile.damage)
                    drawBrightened(ctx, sprites[bush], px, py, TILE, TILE);
                else
                    drawSprite(ctx, sprites[bush], px, py, TILE, TILE);
            }
        }

        // --- enemies on this row ---
        state.enemies.forEach(e => {
            if (e.y !== y) return;

            let sprite = sprites.enemy;
            if (e.attacking === 1) sprite = sprites.enemy_attack;
            if (e.attacking === 2) sprite = sprites.enemy_attack2;

            const ex = e.x * TILE;
            const ey = e.y * TILE;

            if (pre && e.damaged) {
                if (e.dir === -1) {
                    ctx.save();
                    const scale = TILE / 8;
                    const w = sprite.width * scale;
                    ctx.scale(-1, 1);
                    drawBrightened(ctx, sprite, -ex - w, ey);
                    ctx.scale(1, 1);
                    ctx.restore();
                } else {
                    drawBrightened(ctx, sprite, ex, ey);
                }
            } else {
                if (e.dir === -1) {
                    drawFlipped(ctx, sprite, ex, ey);
                } else {
                    drawSprite(ctx, sprite, ex, ey);
                }
            }
        });

        // --- player on this row ---
        const p = state.player;
        if (p.y === y) {
            const px = p.x * TILE;
            const py = p.y * TILE;

            if (pre && p.damaged)
                if (p.disp_dir[0] === -1) {
                    ctx.save();
                    const scale = TILE / 8;
                    const w = sprites.player.width * scale;
                    ctx.scale(-1, 1);
                    drawBrightened(ctx, sprites.player, -px - w, py);
                    ctx.scale(1, 1);
                    ctx.restore();
                } else {
                    drawBrightened(ctx, sprites.player, px, py);
                }
            else
                if (p.disp_dir[0] === -1) {
                    drawFlipped(ctx, sprites.player, px, py);
                } else {
                    drawSprite(ctx, sprites.player, px, py);
                }
        }
    }

    const cx = (state.player.x + state.player.dir[0]) * TILE;
    const cy = (state.player.y + state.player.dir[1]) * TILE;

    const target = tiles[state.player.y + state.player.dir[1]]
                ? tiles[state.player.y + state.player.dir[1]][state.player.x + state.player.dir[0]]
                : null;

    // check if it's a block (same mask idea)
    const isBlock = target && (
        target.tree || target.wall || target.diamond
    );

    if (isBlock) {
        drawSprite(ctx, sprites.cursor, cx, cy - TILE/8*3, TILE, TILE);
    } else {
        drawSprite(ctx, sprites.cursor, cx, cy, TILE, TILE);
    }

    // --- sleep dim ---
    if (state.sleep > 0) {
        ctx.fillStyle = `rgba(0,0,0,${state.sleep / 10})`;
        ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    }

    // --- UI ---
    const UI_Y = 9 * TILE;

    // info bar
    drawSprite(ctx, sprites.info_bar, 0, UI_Y);

    const infoLocs = [
        [13,72],[29,72],[45,72],[60,72],
        [29,80],[45,80],[60,80],
    ].map(([x,y]) => [x*SCALE, y*SCALE]);

    const values = [
        Math.ceil(state.player.health),
        state.hunger || 0,
        state.thirst || 0,
        Math.ceil(state.energy || 0),
        state.inventory?.wood || 0,
        state.inventory?.stone || 0,
        state.inventory?.planks || 0
    ];

    for (let i = 0; i < values.length; i++) {
        const [x,y] = infoLocs[i];
        drawNumber(ctx, values[i], x, y-TILE);
    }

    // tools
    if (state.player_pickaxe)
        drawSprite(ctx, sprites.stone_pickaxe, 4*SCALE, 79*SCALE-TILE);

    if (state.player_sword)
        drawSprite(ctx, sprites.stone_sword, 11*SCALE, 79*SCALE-TILE);

    // crafting
    if (state.crafting) {
        ctx.fillStyle = "rgba(0,0,0,0.3)";
        ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);

        drawSprite(ctx, sprites.crafting_bar, 23*SCALE, 58*SCALE-TILE);

        state.crafting_slots?.forEach((item, i) => {
            const icon = item === 0 ? sprites.stick_icon : sprites.stone_icon;
            drawSprite(ctx, icon, (26 + 9*i)*SCALE, 55*SCALE-TILE);
        });
    }

    // score bar
    drawSprite(ctx, sprites.score_bar, 0, -TILE);

    const score = String(state.score || 0).padStart(7, "0");
    for (let i = 0; i < 7; i++) {
        drawNumber(ctx, parseInt(score[i]), (33 + 4*i)*SCALE, -TILE);
    }

}