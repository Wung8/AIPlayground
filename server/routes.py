import importlib.util
import sys
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

    return render_template("play.html", env=env, bots=bots, my_bots=my_bots, form=form, num_players=env["num_players"])

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
    slug = data.get("env_slug")

    if slug == "soccer":
        games[request.sid] = [SoccerEnv(), ["human" for i in range(4)]]
    elif slug == "slimevolleyball":
        games[request.sid] = [SlimeVolleyballEnv(), ["human" for i in range(4)]]
    else:
        print("Unknown environment:", slug)
        return

    games[request.sid][0].reset()
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
    game, agents = games.get(request.sid)
    if not game:
        return

    actions = {}
    inputs = game.getInputs()
    for n, agent in enumerate(agents):
        pnum = f"p{n+1}"
        if pnum not in inputs: 
            continue
        if agent == "human":
            actions[pnum] = "keyboard"
        else:
            inp = inputs.get(pnum)
            actions[pnum] = agent.getAction(inp)
    
    _, _, done = game.step(
        actions=actions, 
        keyboard=data['action'], 
        display=False
    )
    state = game.getState()

    emit("state", state)

    if done:
        game.reset()

def load_bot(bot, slug):
    path = os.path.join(
        app.root_path,
        "data",
        "user_uploads",
        str(bot.creator.username),
        slug,
        bot.name + ".py"
    )

    if not os.path.exists(path):
        print("Bot file missing:", path)
        return None

    module_name = f"bot_{bot.id}"

    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module.Agent()

@socketio.on("reset_game")
def handle_reset(data):
    slug = data.get("env_slug")
    p1_name = (data.get("p1_name") or "").strip()
    p2_name = (data.get("p2_name") or "").strip()

    # Recreate environment
    if slug == "soccer":
        game = SoccerEnv()
    elif slug == "slimevolleyball":
        game = SlimeVolleyballEnv()
    else:
        return

    agents = []

    # === Load P1 bot ===
    if p1_name and p1_name.lower() != "human":
        bot = Bot.query.filter_by(name=p1_name).first()
        if bot:
            agent = load_bot(bot, slug)
            agents.append(agent)
        else:
            emit("bot_error", {"message": f"P1 bot '{p1_name}' not found"})
    else:
        agents.append("human")

    # === Load P2 bot ===
    if p2_name and p2_name.lower() != "human":
        bot = Bot.query.filter_by(name=p2_name).first()
        if bot:
            agent = load_bot(bot, slug)
            agents.append(agent)
        else:
            emit("bot_error", {"message": f"P2 bot '{p2_name}' not found"})
    else:
        agents.append("human")
    
    game.reset()
    games[request.sid] = [game, agents]


if __name__ == "__main__":
    socketio.run(app, debug=True)
