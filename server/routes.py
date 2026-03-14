import os

from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_socketio import emit
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename

from server import app, socketio, db, bcrypt
from server.forms import LoginForm, RegistrationForm, UploadAgentForm
from server.models import User, Bot
from server.check_bot import check_bot

from server.environment_registry import ENVIRONMENTS, get_env, ENV_REGISTRY, render_env_doc_html
from server.gamerunner import GameRunner

from server import games


def format_environment_name(slug):
    env = get_env(slug)
    if env and env.get("title"):
        return env["title"]

    return slug.title()


def allowed_profile_photo(filename):
    ext = os.path.splitext(filename or "")[1].lower()
    return ext == ".png"


# pages
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/environments")
def environments():
    selected_slug = request.args.get("slug") or (ENVIRONMENTS[0]["slug"] if ENVIRONMENTS else "")
    return render_template(
        "environments.html",
        environments=ENVIRONMENTS,
        selected_slug=selected_slug,
    )


@app.route("/doc/<slug>")
def env_doc(slug):
    env = get_env(slug) or (ENVIRONMENTS[0] if ENVIRONMENTS else None)
    if not env:
        return "missing env", 404

    env_doc_html = render_env_doc_html(env["slug"])
    return render_template(
        "env_doc.html",
        env=env,
        environments=ENVIRONMENTS,
        env_doc_html=env_doc_html,
    )


@app.route("/play/<slug>", methods=["GET", "POST"])
def play(slug):
    env = get_env(slug) or (ENVIRONMENTS[0] if ENVIRONMENTS else None)
    environment = slug
    if not env:
        return "missing env", 404

    form = UploadAgentForm()

    # handle upload submit
    if request.method == "POST":
        if not current_user.is_authenticated:
            flash("Log in to upload your own bots!", "warning")
            return redirect(url_for("play", slug=slug, tab="mine"))

        if form.validate_on_submit():
            user_dir = os.path.join(app.root_path, "data", "user_uploads", str(current_user.username), slug)
            os.makedirs(user_dir, exist_ok=True)

            existing = [f for f in os.listdir(user_dir) if f.endswith(".py")]
            if len(existing) >= 3:
                flash("Maximum of 3 bots allowed per environment", "warning")
                return redirect(url_for("play", slug=slug, tab="mine"))

            f = form.agent_file.data

            filename = secure_filename(f.filename or "")
            if not filename.endswith(".py"):
                flash("Only .py files are allowed.", "danger")
                return redirect(url_for("play", slug=slug, tab="mine"))

            if Bot.query.filter_by(name=filename[:-3]).first() or filename[:-3].lower() == "human":
                flash("That filename is already in use.", "danger")
                return redirect(url_for("play", slug=slug, tab="mine"))
            
            file_str = f.read().decode("utf-8")
            passed, msg = check_bot(file_str)
            if not passed:
                flash(msg)
                return redirect(url_for("play", slug=slug, tab="mine"))
            
            f.stream.seek(0)

            bot = Bot(
                name=filename[:-3],
                user_id=current_user.id,
                environment=environment
            )
            db.session.add(bot)
            db.session.commit()

            f.save(os.path.join(user_dir, filename))

            flash("Bot uploaded!", "success")
            return redirect(url_for("play", slug=slug, tab="mine"))

        flash("Upload failed. Please choose a .py file.", "danger")
        return redirect(url_for("play", slug=slug, tab="mine"))

    # normal GET render
    bots = Bot.query.filter_by(environment=environment).all()

    if current_user.is_authenticated:
        my_bots = Bot.query.filter_by(environment=environment).filter_by(user_id=current_user.id).all()
    else:
        my_bots = []

    return render_template(
        "play.html",
        env=env,
        bots=bots,
        my_bots=my_bots,
        form=form,
        num_players=env["num_players"],
        has_difficulty_setting=env["has_difficulty_setting"]
    )


@app.route("/bot_search/<slug>", methods=["GET"])
def bot_search(slug):
    env = get_env(slug) or (ENVIRONMENTS[0] if ENVIRONMENTS else None)
    if not env:
        return jsonify({"results": []}), 404

    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify({"results": []})

    # search bots in this environment by whether their .py file contains the substring
    bots = Bot.query.filter_by(environment=slug).all()

    q_low = q.lower()
    out = []

    for b in bots:
        path = os.path.join(
            app.root_path,
            "data",
            "user_uploads",
            str(b.creator.username),
            slug,
            b.name + ".py"
        )

        try:
            if not os.path.exists(path):
                continue

            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()

            if q_low in txt.lower():
                out.append({
                    "name": b.name,
                    "elo": b.elo,
                    "by": b.creator.username,
                })
        except Exception:
            continue

    return jsonify({"results": out})


@app.route("/delete_bot/<int:bot_id>", methods=["POST"])
@login_required
def delete_bot(bot_id):
    bot = Bot.query.get_or_404(bot_id)

    # security: only allow deleting your own bot
    if bot.user_id != current_user.id:
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    # build file path
    path = os.path.join(
        app.root_path,
        "data",
        "user_uploads",
        bot.creator.username,
        bot.environment,
        bot.name + ".py"
    )

    # delete file if exists
    if os.path.exists(path):
        os.remove(path)

    # delete db entry
    db.session.delete(bot)
    db.session.commit()

    return jsonify({"success": True})


@app.route("/login", methods=["GET", "POST"])
def login():
    # prefixes prevent collisions since both forms share field names like "email", "password", "submit"
    login_form = LoginForm(prefix="login")
    register_form = RegistrationForm(prefix="reg")

    # login submit
    if login_form.submit.data and login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user, remember=login_form.remember.data)
            return redirect(url_for("home"))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")

    # register submit
    if register_form.submit.data and register_form.validate_on_submit():
        pw_hash = bcrypt.generate_password_hash(register_form.password.data).decode("utf-8")
        user = User(
            username=register_form.username.data,
            email=register_form.email.data,
            password=pw_hash
        )
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You are now able to log in", "success")
        return redirect(url_for("login"))

    return render_template(
        "login.html",
        title="Login - AI Playground",
        active="login",
        login_form=login_form,
        register_form=register_form,
    )


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/profile")
@login_required
def profile():
    bots = (
        Bot.query
        .filter_by(user_id=current_user.id)
        .order_by(Bot.date_posted.desc())
        .all()
    )

    bot_cards = []
    for bot in bots:
        bot_cards.append({
            "id": bot.id,
            "name": bot.name,
            "elo": bot.elo,
            "date_posted": bot.date_posted,
            "environment": bot.environment,
            "environment_display": format_environment_name(bot.environment),
        })

    return render_template("profile.html", bots=bot_cards)


@app.route("/profile/upload_photo", methods=["POST"])
@login_required
def upload_profile_photo():
    f = request.files.get("profile_photo")
    if not f or not f.filename:
        flash("Please choose a .png file.", "warning")
        return redirect(url_for("profile"))

    if not allowed_profile_photo(f.filename):
        flash("Profile photo must be a .png file.", "danger")
        return redirect(url_for("profile"))

    photos_dir = os.path.join(app.root_path, "data", "profile_photos")
    os.makedirs(photos_dir, exist_ok=True)

    filename = secure_filename(f"{current_user.username}.png")
    path = os.path.join(photos_dir, filename)

    f.save(path)

    current_user.image_file = filename
    db.session.commit()

    flash("Profile photo updated.", "success")
    return redirect(url_for("profile"))


@app.route("/profile_photos/<filename>")
def profile_photo(filename):
    photos_dir = os.path.join(app.root_path, "data", "profile_photos")
    return send_from_directory(photos_dir, filename)


# placeholders for navbar links
@app.route("/github")
def github():
    return "github placeholder"


@app.route("/discord")
def discord():
    return "discord placeholder"


@app.route("/contact")
def contact():
    return "contact placeholder"


@socketio.on("join_env")
def handle_connect(data):
    GameRunner(request.sid, data) # auto places itself in games
    print(f"{request.sid} connected")

@socketio.on("disconnect")
def handle_disconnect():
    games[request.sid].close()
    del games[request.sid]
    print(f"{request.sid} disconnected")


@socketio.on("input")
def handle_input(data):
    gamerunner = games.get(request.sid)
    if not gamerunner:
        socketio.emit("refresh_page", to=request.sid)
        return
    gamerunner.set_client_data(data)


@socketio.on("reset_game")
def handle_reset(data):
    if request.sid in games:
        games[request.sid].close()
    
    GameRunner(request.sid, data)


if __name__ == "__main__":
    socketio.run(app, debug=True)