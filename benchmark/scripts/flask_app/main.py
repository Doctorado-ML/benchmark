import os
from flask import (
    Blueprint,
    current_app,
    render_template,
    url_for,
    flash,
    redirect,
    request,
    abort,
)
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.urls import url_parse
from benchmark.Utils import Files, Folders
from .forms import LoginForm
from benchmark.ResultsBase import StubReport
from .models import User

main = Blueprint("main", __name__)


@main.route("/")
@main.route("/index")
def index():
    # Get a list of files in a directory
    files = {}
    compare = False
    # names = Files.get_all_results(hidden=False)
    # for name in names:
    #     report = StubReport(os.path.join(Folders.results, name))
    #     report.report()
    #     files[name] = {
    #         "duration": report.duration,
    #         "score": report.score,
    #         "title": report.title,
    #     }
    # candidate = current_app.config["FRAMEWORKS"].copy()
    # candidate.remove(current_app.config["FRAMEWORK"])
    # return render_template(
    #     "select.html",
    #     files=files,
    #     candidate=candidate[0],
    #     framework=current_app.config["FRAMEWORK"],
    #     compare=compare.capitalize() == "True",
    # )
    return render_template("index.html")


@main.route("/results")
@login_required
def results():
    return render_template("results.html")


@main.route("/datasets")
@login_required
def datasets():
    pass


@main.route("/config")
@login_required
def config():
    pass


@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("main.login"))
        login_user(user, remember=form.remember_me.data)
        flash("Logged in successfully.")
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("main.index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))
