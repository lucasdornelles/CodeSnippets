from string import ascii_letters, digits

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, scoped_session
from database import User, Snippet, Tag, Bookmark
from login_required import login_required

from urllib import parse


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Prepare database session, CHANGE ECHO TO FALSE IN PRODUCTION
engine = create_engine('sqlite:///database.db', echo=False)
# Use scoped_session to tie session to thread
db_session = scoped_session(sessionmaker(bind=engine))

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/", methods=['GET'])
def index():
    # Initialize database and load tags list for autocomplete
    db_session()
    tags = [tag.name for tag in db_session.query(Tag).all()]
    # if there are tags on the request args search for snippets with tags
    if request.args.get("tags"):
        snippets = db_session.query(Snippet)
        for tag in request.args.get("tags").replace(' ', '').split(','):
            snippets = snippets.filter(Snippet.tags.any(func.lower(Tag.name) == tag.lower()))
        count = snippets.count()
        # If a user is logged in load user
        if session.get('user_id'):
            user = db_session.query(User).filter(User.id == session['user_id']).first()
        else:
            user = None
        # If page is in request args apply offset to query, else page = 1
        if request.args.get("page"):
            page = int(request.args.get("page"))
            offset = (int(page) - 1) * 10
            snippets = snippets.offset(offset)
        else:
            page = 1
        # order by number of tags
        snippets = snippets.order_by(Snippet.n_tags)
        snippets = snippets.limit(10).all()
        db_session.remove()
        return render_template("index.html", tags=tags, query_tags=request.args.get("tags").replace(' ', ''),
                               snippets=snippets, count=count, page=page, parse=parse, user=user)
    db_session.remove()
    return render_template("index.html", tags=tags)


@app.route("/mysnippets")
@login_required
def my_snippets():
    db_session()
    tags = [tag.name for tag in db_session.query(Tag).all()]
    snippets = db_session.query(Snippet)
    snippets = snippets.filter(Snippet.user_id == session["user_id"])
    if request.args.get("tags"):
        for tag in request.args.get("tags").replace(' ', '').split(','):
            snippets = snippets.filter(Snippet.tags.any(func.lower(Tag.name) == tag.lower()))
        count = snippets.count()
        if request.args.get("page"):
            page = int(request.args.get("page"))
            offset = (int(page) - 1) * 10
            snippets = snippets.offset(offset)
        else:
            page = 1
        # order by number of tags
        snippets = snippets.order_by(Snippet.n_tags)
        snippets = snippets.limit(10).all()
        db_session.remove()
        return render_template("mysnippets.html", tags=tags, query_tags=request.args.get("tags").replace(' ', ''),
                               snippets=snippets, count=count, page=page, parse=parse)
    count = snippets.count()
    if request.args.get("page"):
        page = int(request.args.get("page"))
        offset = (int(page) - 1) * 10
        snippets = snippets.offset(offset)
    else:
        page = 1
    snippets = snippets.limit(10).all()
    db_session.remove()
    return render_template("mysnippets.html", tags=tags, snippets=snippets, count=count, page=page, parse=parse)


@app.route("/mybookmarks")
@login_required
def my_bookmarks():
    db_session()
    tags = [tag.name for tag in db_session.query(Tag).all()]
    snippets = db_session.query(Snippet).filter(Bookmark.snippet_id == Snippet.id,
                                                Bookmark.user_id == session['user_id'])
    if request.args.get("tags"):
        for tag in request.args.get("tags").replace(' ', '').split(','):
            snippets = snippets.filter(Snippet.tags.any(func.lower(Tag.name) == tag.lower()))
        count = snippets.count()
        if request.args.get("page"):
            page = int(request.args.get("page"))
            offset = (int(page) - 1) * 10
            snippets = snippets.offset(offset)
        else:
            page = 1
        # order by number of tags
        snippets = snippets.order_by(Snippet.n_tags)
        snippets = snippets.limit(10).all()
        db_session.remove()
        return render_template("mybookmarks.html", tags=tags, query_tags=request.args.get("tags").replace(' ', ''),
                               snippets=snippets, count=count, page=page, parse=parse)
    count = snippets.count()
    if request.args.get("page"):
        page = int(request.args.get("page"))
        offset = (int(page) - 1) * 10
        snippets = snippets.offset(offset)
    else:
        page = 1
    snippets = snippets.limit(10).all()
    db_session.remove()
    return render_template("mybookmarks.html", tags=tags, snippets=snippets, count=count, page=page, parse=parse)


@app.route("/expand/<int:snippet_id>")
def expand(snippet_id):
    if not snippet_id:
        flash("No snippet id provided")
        return redirect(url_for('index'))
    db_session()
    snippet = db_session.query(Snippet).filter(Snippet.id == snippet_id).first()
    if not snippet:
        db_session.remove()
        flash("Something went wrong, probably provided the wrong snippet id")
        return redirect(url_for('index'))
    if session.get("user_id"):
        user = db_session.query(User).filter(User.id == session['user_id']).first()
    else:
        user = None
    snippet_user = snippet.user.name
    db_session.remove()
    return render_template("expand.html", snippet=snippet, user=user, snippet_user=snippet_user,
                           request_url=request.referrer)


@app.route("/edit/<int:snippet_id>", methods=["GET", "POST"])
@login_required
def edit(snippet_id):
    if request.method == "GET":
        if not snippet_id:
            flash("No snippet id provided")
            return redirect(url_for('index'))
        db_session()
        tags = [tag.name for tag in db_session.query(Tag).all()]
        snippet = db_session.query(Snippet).filter(Snippet.id == snippet_id). \
            filter(Snippet.user_id == session["user_id"]).first()
        if not snippet:
            db_session.remove()
            flash("Something went wrong, probably provided the wrong snippet id or the snippet is not yours")
            return redirect(url_for('index'))
        return render_template("edit.html", snippet=snippet, tags=tags)
    else:
        # Update snippet
        if not snippet_id:
            flash("No snippet id provided")
            return redirect(url_for('index'))
        if len(request.form.get("name")) < 4:
            flash("Snippet name must be at least 4 characters long")
            return redirect(request.referrer)
        db_session()
        snippet = db_session.query(Snippet).filter(Snippet.id == snippet_id). \
            filter(Snippet.user_id == session["user_id"]).first()
        if not snippet:
            db_session.remove()
            flash("Something went wrong, probably provided the wrong snippet id or the snippet is not yours")
            return redirect(url_for('index'))
        snippet.name = request.form.get("name")
        snippet.snippet = request.form.get("codeSnippet")
        snippet.description = request.form.get("description")
        snippet.mode = request.form.get("mode")
        snippet.tags = []
        tags = {tag.name.lower(): tag for tag in db_session.query(Tag).all()}
        sn_tags = []
        new_tags = []
        request_tags = request.form.get("tags").replace(' ', '').split(',')
        if '' in request_tags:
            db_session.remove()
            flash("Please provide at least one tag")
            return redirect(request.referrer)
        for form_tag in request_tags:
            if form_tag.lower() in tags.keys():
                sn_tags.append(tags[form_tag.lower()])
            else:
                new_tags.append(Tag(form_tag))

        if new_tags:
            db_session.add_all(new_tags)
            for tag in new_tags:
                sn_tags.append(tag)
        snippet.add_tags(sn_tags)
        db_session.commit()
        db_session.remove()
        flash("Snippet updated")
        return redirect(url_for('index'))


@app.route("/delete/<snippet_id>")
@login_required
def delete_snippet(snippet_id):
    if not snippet_id:
        flash("No snippet id provided")
        return redirect(url_for('index'))
    db_session()
    snippet = db_session.query(Snippet).filter(Snippet.id == snippet_id). \
        filter(Snippet.user_id == session["user_id"]).first()
    if not snippet:
        db_session.remove()
        flash("Something went wrong, probably provided the wrong snippet id or the snippet is not yours")
        return redirect(url_for('index'))
    db_session.delete(snippet)
    db_session.commit()
    db_session.remove()
    flash("Snippet deleted")
    return redirect(url_for('index'))


@app.route("/compose", methods=["GET", "POST"])
@login_required
def compose():
    if request.method == "POST":
        if len(request.form.get("name")) < 4:
            flash("Snippet name must be at least 4 characters long")
            return redirect(request.referrer)
        request_tags = request.form.get("tags").replace(' ', '').split(',')
        if '' in request_tags:
            flash("Please provide at least one tag")
            return redirect(request.referrer)
        db_session()
        tags = {tag.name.lower(): tag for tag in db_session.query(Tag).all()}
        snippet = Snippet(name=request.form.get("name"), snippet=request.form.get("codeSnippet"),
                          description=request.form.get("description"), mode=request.form.get("mode"),
                          user=db_session.query(User).filter(User.id == session["user_id"]).first())
        sn_tags = []
        new_tags = []
        for form_tag in request_tags:
            if form_tag.lower() in tags.keys():
                sn_tags.append(tags[form_tag.lower()])
            else:
                new_tags.append(Tag(form_tag))

        if new_tags:
            db_session.add_all(new_tags)
            for tag in new_tags:
                sn_tags.append(tag)
        snippet.add_tags(sn_tags)
        db_session.add(snippet)
        db_session.commit()
        db_session.remove()
        flash("Snippet saved")

        return redirect(url_for('index'))

    else:
        db_session()
        tags = [tag.name for tag in db_session.query(Tag).all()]
        db_session.remove()
        return render_template("compose.html", tags=tags)


@app.route("/bookmark/<snippet_id>/<action>")
@login_required
def bookmark_action(snippet_id, action):
    db_session()
    snippet = db_session.query(Snippet).filter(Snippet.id == snippet_id).first()
    user = db_session.query(User).filter(User.id == session['user_id']).first()
    if action == 'add':
        if snippet not in user.user_bookmarks:
            user.user_bookmarks.append(snippet)
        db_session.commit()
        db_session.remove()
        flash("Snippet add to bookmarks")
        return redirect(request.referrer)
    elif action == 'remove':
        if snippet in user.user_bookmarks:
            user.user_bookmarks.remove(snippet)
        db_session.commit()
        db_session.remove()
        flash("Snippet removed from bookmarks")
        return redirect(request.referrer)
    else:
        db_session.remove()
        flash("Something went wrong while trying to bookmark snippet :(")
        return redirect(request.referrer)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    db_session()
    user = db_session.query(User).filter(User.id == session['user_id']).first()
    if request.method == "POST":
        user.about = request.form.get("about")
        db_session.commit()
        db_session.remove()
        flash("Updated 'About me'")
        return redirect(request.referrer)
    db_session.remove()
    return render_template("profile.html", user=user)


@app.route("/changepass", methods=["POST"])
@login_required
def change_password():
    db_session()
    user = db_session.query(User).filter(User.id == session['user_id']).first()
    if request.method == "POST":
        if not user.check_password(request.form.get("password")):
            flash("Invalid password")
            db_session.remove()
            return redirect(request.referrer)
        elif not request.form.get("new_password"):
            flash("no new password")
            db_session.remove()
            return redirect(request.referrer)
        elif len(request.form.get("new_password")) < 6:
            flash("password must be 6 or more characters long")
            db_session.remove()
            return redirect(request.referrer)
        elif not request.form.get("new_password") == request.form.get("confirm_password"):
            flash("couldn't confirm password")
            db_session.remove()
            return redirect(request.referrer)
        user.update_password(password=request.form.get("new_password"))
        db_session.commit()
        db_session.remove()
        flash("Updated password")
        return redirect(request.referrer)


@app.route("/user/<user_id>")
def user_profile(user_id):
    if not user_id:
        flash("No user id provided")
        return redirect(url_for('index'))
    db_session()
    user = db_session.query(User).filter(User.id == user_id).first()
    if not user:
        flash("Wrong user id")
        return redirect(url_for('index'))
    db_session.remove()
    return render_template("userprofile.html", user=user)


@app.route("/user/<user_id>/snippets")
def user_snippets(user_id):
    if not user_id:
        return "error"
    db_session()
    tags = [tag.name for tag in db_session.query(Tag).all()]
    snippets = db_session.query(Snippet).filter(Snippet.user_id == user_id)
    username = db_session.query(User).filter(User.id == user_id).first().name
    if session.get('user_id'):
        user = db_session.query(User).filter(User.id == session['user_id']).first()
    else:
        user = None
    if request.args.get("tags"):
        for tag in request.args.get("tags").replace(' ', '').split(','):
            snippets = snippets.filter(Snippet.tags.any(func.lower(Tag.name) == tag.lower()))
        count = snippets.count()
        if request.args.get("page"):
            page = int(request.args.get("page"))
            offset = (int(page) - 1) * 10
            snippets = snippets.offset(offset)
        else:
            page = 1
        # order by number of tags
        snippets = snippets.order_by(Snippet.n_tags)
        snippets = snippets.limit(10).all()
        db_session.remove()
        return render_template("usersnippets.html", tags=tags, snippets=snippets, user=user, count=count, page=page,
                               query_tags=request.args.get("tags").replace(' ', ''), parse=parse, username=username,
                               user_id=user_id)
    count = snippets.count()
    if request.args.get("page"):
        page = int(request.args.get("page"))
        offset = (int(page) - 1) * 10
        snippets = snippets.offset(offset)
    else:
        page = 1
    snippets = snippets.limit(10).all()
    db_session.remove()
    return render_template("usersnippets.html", tags=tags, snippets=snippets, user=user,
                           count=count, page=page, parse=parse, username=username, user_id=user_id)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("username"):
            flash("no username")
            return render_template("register.html")
        elif not 3 < len(request.form.get("username")) < 40:
            flash("username must be between 4 and 40 characters long")
            return render_template("register.html")
        elif set(request.form.get("username")).difference(ascii_letters + digits):
            flash("username can't have special characters")
            return render_template("register.html")
        elif not request.form.get("password"):
            flash("no password")
            return render_template("register.html")
        elif len(request.form.get("password")) < 6:
            flash("password must be 6 or more characters long")
            return render_template("register.html")
        elif not request.form.get("password") == request.form.get("confirm_password"):
            flash("couldn't confirm password")
            return render_template("register.html")
        db_session()
        if db_session.query(User).filter(User.name == request.form.get("username")).first():
            flash("username already in use")
            return render_template("register.html")

        user = User(name=request.form.get("username"), password=request.form.get("password"))
        db_session.add(user)
        db_session.commit()
        session["user_id"] = user.id
        db_session.remove()
        flash("Successfully registered")

        return redirect(url_for('index'))

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            flash("no username")
            return render_template("login.html")
        elif not request.form.get("password"):
            flash("no password")
            return render_template("login.html")

        # Query database for username
        db_session()
        user = db_session.query(User).filter(User.name == request.form.get("username")).first()
        db_session.remove()
        if not user or not user.check_password(request.form.get("password")):
            flash("invalid username and/or password")
            return render_template("login.html")

        session["user_id"] = user.id
        flash("Successfully logged in")

        return redirect(url_for('index'))

    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()
    flash("Successfully logged out")

    # Redirect user to login form
    return redirect(url_for('index'))
