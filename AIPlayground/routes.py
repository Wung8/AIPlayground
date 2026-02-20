from flask import render_template, request, redirect, url_for, flash
from flask_socketio import emit
from flask_login import login_user, logout_user, current_user, login_required

from AIPlayground import app, socketio, db, bcrypt
from AIPlayground.forms import LoginForm, RegistrationForm
from AIPlayground.models import User

from AIPlayground.data.environments import ENVIRONMENTS, get_env
from AIPlayground.slimevolleyball import SlimeVolleyballEnv  # assume you moved logic here
from AIPlayground.soccer import SoccerEnv


BOTS = [
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

@app.route("/play/<slug>")
def play(slug):
    env = get_env(slug) or (ENVIRONMENTS[0] if ENVIRONMENTS else None)
    if not env:
        return "missing env", 404
    return render_template("play.html", env=env, bots=BOTS)

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
