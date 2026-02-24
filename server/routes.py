import os

from flask import render_template, request, redirect, url_for, flash
from flask_socketio import emit
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename

from server import app, socketio, db, bcrypt
from server.forms import LoginForm, RegistrationForm, UploadAgentForm
from server.models import User, Bot

from server.data.environments import ENVIRONMENTS, get_env
from server.static.environments.slimevolleyball import SlimeVolleyballEnv  # assume you moved logic here
from server.static.environments.soccer import SoccerEnv


AGENTS = [
    {"name": "epicbot", "elo": 1400, "by": "someone"},
    {"name": "basicbot25", "elo": 1000, "by": "wung8"},
    {"name": "another_bot2000", "elo": 600, "by": "wung8"},
]

# store one game per client (later: one per env per client)
games = {}

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
    return render_template("env_doc.html", env=env, environments=ENVIRONMENTS)

@app.route("/play/<slug>", methods=["GET", "POST"])
def play(slug):
    env = get_env(slug) or (ENVIRONMENTS[0] if ENVIRONMENTS else None)
    if not env:
        return "missing env", 404

    form = UploadAgentForm()

    # handle upload submit
    if request.method == "POST":
        if not current_user.is_authenticated:
            flash("Log in to upload your own bots!", "warning")
            return redirect(url_for("play", slug=slug, tab="mine"))

        if form.validate_on_submit():
            user_dir = os.path.join(app.root_path, "data", "user_uploads", str(current_user.id), slug)
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

            if os.path.exists(os.path.join(user_dir, filename)):
                flash("That filename is already in use.", "danger")
                return redirect(url_for("play", slug=slug, tab="mine"))

            f.save(os.path.join(user_dir, filename))

            bot = Bot(
                name=filename[:-3],
                user_id=current_user.id,
            )
            db.session.add(bot)
            db.session.commit()

            flash("Bot uploaded!", "success")
            return redirect(url_for("play", slug=slug, tab="mine"))

        flash("Upload failed. Please choose a .py file.", "danger")
        return redirect(url_for("play", slug=slug, tab="mine"))

    # normal GET render
    bots = Bot.query.all()

    if current_user.is_authenticated:
        my_bots = Bot.query.filter_by(user_id=current_user.id).all()
    else:
        my_bots = []

    return render_template("play.html", env=env, bots=bots, my_bots=my_bots, form=form)

'''
@login_required
@app.route("upload/<slug>")
def upload_agent(slug):
    env = get_env(slug) or (ENVIRONMENTS[0] if ENVIRONMENTS else None)
    if not env:
        return "missing env", 404
    
    form = UploadAgentForm()
    if not form.validate_on_submit():
        flash("Upload failed. Please choose a .py file.", "danger")
        return redirect(url_for("upload", slug=slug, tab="mine"))
    
    user_dir = os.path.join(app.root_path, "data", "user_uploads", str(current_user.id), slug)
    os.makedirs(user_dir, exist_ok=True)

    existing = [f for f in os.listdir(user_dir) if f.endswith(".py")]
    if len(existing) >= 3:
        flash("You already have 3 bots for this environment.", "warning")
        return redirect(url_for("play", slug=slug, tab="mine"))

    f = form.agent_file.data
    filename = secure_filename(f.filename or "")
    if not filename.endswith(".py"):
        flash("Only .py files are allowed.", "danger")
        return redirect(url_for("play", slug=slug, tab="mine"))
    if len(filename) < 6:
        flash("Filename must be at least 3 characters long.", "danger")
        return redirect(url_for("play", slug=slug, tab="mine"))
    if os.path.exists(os.path.join(user_dir, filename)):
        flash("That filename is already in use.", "danger")
        return redirect(url_for("play", slug=slug, tab="mine"))

    f.save(os.path.join(user_dir, filename))
    flash("Bot uploaded.", "success")
    return redirect(url_for("play", slug=slug, tab="mine"))
'''

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
            flash('Login Unsuccessful. Please check email and password', 'danger')

    # register submit
    if register_form.submit.data and register_form.validate_on_submit():
        pw_hash = bcrypt.generate_password_hash(register_form.password.data).decode("utf-8")
        user = User(username=register_form.username.data, email=register_form.email.data, password=pw_hash)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You are now able to log in', 'success')
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
    return redirect(url_for('login'))

@app.route("/profile", methods=["GET", "POST"])
def profile():
    return render_template("profile.html")

# placeholders for navbar links you already show
@app.route("/acm")
def acm():
    return "acm page placeholder"

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
    slug = data.get("env_slug")

    if slug == "soccer":
        games[request.sid] = SoccerEnv()
    elif slug == "slimevolleyball":
        games[request.sid] = SlimeVolleyballEnv()
    else:
        print("Unknown environment:", slug)
        return

    games[request.sid].reset()
    print(f"{request.sid} joined {slug}")


@socketio.on("disconnect")
def handle_disconnect():
    if request.sid in games:
        del games[request.sid]
    print("Client disconnected")


@socketio.on("input")
def handle_input(data):
    """
    data = {
        "action": 0/1/2/3
    }
    """
    game = games.get(request.sid)
    if not game:
        return

    obs = game.getInputs()
    obs, reward, done = game.step(
        actions={"p1":"keyboard", "p2":"keyboard", "p3":"keyboard", "p4":"keyboard"}, 
        keyboard=data['action'], 
        display=False
    )
    state = game.getState()

    emit("state", state)

    if done:
        game.reset()


if __name__ == "__main__":
    socketio.run(app, debug=True)
