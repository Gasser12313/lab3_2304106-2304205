import os
import re
import uuid

import bcrypt
import pymysql
from dotenv import load_dotenv
from flask import Flask, abort, redirect, render_template, request, session

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["MAX_CONTENT_LENGTH"] = 3 * 1024 * 1024   # Bonus: refuse any request bigger than 3 MB


def run(sql, params=(), fetch=None, database=None):
    """Run one SQL statement. The values always go in `params` (never glued into the SQL).
    By default it uses the Lab 2 database (DB_NAME = registration)."""
    with pymysql.connect(
        host=os.getenv("DB_HOST"), user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"), database=database or os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor, autocommit=True,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            if fetch == "one":
                return cur.fetchone()
            if fetch == "all":
                return cur.fetchall()


def lib(sql, params=(), fetch=None):
    """Same as run(), but on the Lab 3 database `library` (DB_LIBRARY)."""
    return run(sql, params, fetch, os.getenv("DB_LIBRARY", "library"))


EMAIL = re.compile(r"[^@\s]+@[^@\s]+")   # one @, with something before and after it, no spaces


def title_errors(title):
    if title.strip() == "":
        return ["Title is required"]
    if len(title) > 200:
        return ["Title is too long (200 characters at most)"]
    return []


def current_filter():
    """Bonus: which list to show. Only these three values are accepted."""
    f = request.args.get("filter", "all")
    return f if f in ("all", "open", "done") else "all"


def back():
    """Redirect to the list and keep the chosen filter."""
    f = current_filter()
    return redirect("/todos" if f == "all" else "/todos?filter=" + f)


def show_todos(add_errors=[], add_title="", edit_id=None, edit_title="", edit_errors=[]):
    rows = run("SELECT todo_id, title, is_done, created_at FROM todos "
               "WHERE user_id = %s ORDER BY todo_id DESC", (session["user_id"],), "all")
    # Bonus: count open to-dos and filter the list (done here, so the SQL stays the same)
    open_count = sum(1 for r in rows if not r["is_done"])
    total = len(rows)
    flt = current_filter()
    if flt == "open":
        rows = [r for r in rows if not r["is_done"]]
    elif flt == "done":
        rows = [r for r in rows if r["is_done"]]
    return render_template("todos.html", todos=rows, add_errors=add_errors, add_title=add_title,
                           edit_id=edit_id, edit_title=edit_title, edit_errors=edit_errors,
                           flt=flt, open_count=open_count, total=total)


@app.route("/")
def index():
    return redirect("/todos" if "user_id" in session else "/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", errors=[], form={})

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm_password", "")

    errors = []
    if name == "":
        errors.append("Name is required")
    if email == "":
        errors.append("Email is required")
    elif not EMAIL.fullmatch(email):
        errors.append("Email must contain @ (like name@example.com)")
    if password == "":
        errors.append("Password is required")
    if confirm == "":
        errors.append("Confirm password is required")
    if password and confirm and password != confirm:
        errors.append("Passwords do not match")
    if errors:  # show the form again, do not touch the database
        return render_template("register.html", errors=errors, form={"name": name, "email": email})

    # bcrypt only reads the first 72 bytes of a password
    password_hash = bcrypt.hashpw(password.encode()[:72], bcrypt.gensalt()).decode()
    try:
        run("INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s)",
            (email, name, password_hash))
    except pymysql.err.IntegrityError:  # UNIQUE (email) failed: error 1062
        return render_template("register.html", errors=["Email Already Exists"],
                               form={"name": name, "email": email})

    user = run("SELECT user_id, name, password_hash FROM users WHERE email = %s", (email,), "one")
    session["user_id"] = user["user_id"]
    session["name"] = user["name"]
    return redirect("/todos")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", errors=[], form={})

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    errors = []
    if email == "":
        errors.append("Email is required")
    if password == "":
        errors.append("Password is required")
    if errors:
        return render_template("login.html", errors=errors, form={"email": email})

    user = run("SELECT user_id, name, password_hash FROM users WHERE email = %s", (email,), "one")
    # same message whether the e-mail or the password is wrong
    if user is None or not bcrypt.checkpw(password.encode()[:72], user["password_hash"].encode()):
        return render_template("login.html", errors=["Invalid email or password"], form={"email": email})

    session["user_id"] = user["user_id"]
    session["name"] = user["name"]
    return redirect("/todos")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/login")


@app.route("/todos")
def todos():
    if "user_id" not in session:
        return redirect("/login")
    return show_todos()


@app.route("/todos/add", methods=["POST"])
def add_todo():
    if "user_id" not in session:
        return redirect("/login")
    title = request.form.get("title", "")
    errors = title_errors(title)
    if errors:
        return show_todos(add_errors=errors, add_title=title)
    run("INSERT INTO todos (user_id, title) VALUES (%s, %s)", (session["user_id"], title.strip()))
    return back()


@app.route("/todos/<int:todo_id>/edit", methods=["POST"])
def edit_todo(todo_id):
    if "user_id" not in session:
        return redirect("/login")
    title = request.form.get("title", "")
    errors = title_errors(title)
    if errors:
        return show_todos(edit_id=todo_id, edit_title=title, edit_errors=errors)
    run("UPDATE todos SET title = %s WHERE todo_id = %s AND user_id = %s",
        (title.strip(), todo_id, session["user_id"]))
    return back()


@app.route("/todos/<int:todo_id>/done", methods=["POST"])
def done_todo(todo_id):
    if "user_id" not in session:
        return redirect("/login")
    is_done = 1 if request.form.get("is_done") == "1" else 0
    run("UPDATE todos SET is_done = %s WHERE todo_id = %s AND user_id = %s",
        (is_done, todo_id, session["user_id"]))
    return back()


@app.route("/todos/<int:todo_id>/delete", methods=["POST"])
def delete_todo(todo_id):
    if "user_id" not in session:
        return redirect("/login")
    run("DELETE FROM todos WHERE todo_id = %s AND user_id = %s", (todo_id, session["user_id"]))
    return back()


# ======================= Lab 3: the library (books and authors) =======================
@app.before_request
def library_needs_login():
    # the site is private: the library pages need a logged-in user, like the to-do list
    if request.path.startswith(("/books", "/authors")) and "user_id" not in session:
        return redirect("/login")


PRICE = re.compile(r"\d{1,8}(\.\d{1,2})?")   # 12 or 12.5 or 12.50 (not negative, 2 decimals at most)


def book_errors(title, price, author_id):
    errors = []
    if title == "":
        errors.append("Title is required")
    elif len(title) > 150:
        errors.append("Title is too long (150 characters at most)")
    if price == "":
        errors.append("Price is required")
    elif not PRICE.fullmatch(price):
        errors.append("Price must be a number like 12.50")
    if not (author_id.isascii() and author_id.isdigit()):
        errors.append("Author is required")
    return errors


def author_errors(name, country):
    errors = []
    if name == "":
        errors.append("Name is required")
    elif len(name) > 100:
        errors.append("Name is too long (100 characters at most)")
    if country == "":
        errors.append("Country is required")
    elif len(country) > 50:
        errors.append("Country is too long (50 characters at most)")
    return errors


def book_form():
    return (request.form.get("title", "").strip(), request.form.get("price", "").strip(),
            request.form.get("author_id", "").strip())


def author_form():
    return request.form.get("name", "").strip(), request.form.get("country", "").strip()



# ---------- Bonus: images (a cover for each book, a photo for each author) ----------
# The file goes in static/uploads/<books|authors>/ and only its NEW random name is stored in the database.
UPLOAD_DIR = os.path.join(app.root_path, "static", "uploads")
MAX_IMAGE = 2 * 1024 * 1024   # 2 MB per image


def image_type(data):
    """Look at the first bytes of the file (not at its name): jpg, png, gif, webp or None."""
    if data.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return "gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


def read_image():
    """Read the optional file field `image`. Returns (data, extension, errors).
    No file chosen is fine: (None, None, [])."""
    file = request.files.get("image")
    if file is None or file.filename == "":
        return None, None, []
    data = file.read(MAX_IMAGE + 1)
    if len(data) > MAX_IMAGE:
        return None, None, ["Image is too big (2 MB at most)"]
    ext = image_type(data)
    if ext is None:
        return None, None, ["Image must be a JPG, PNG, GIF or WEBP file"]
    return data, ext, []


def save_image(kind, data, ext):
    """Write the file with a random name (never the name the user sent) and return that name."""
    folder = os.path.join(UPLOAD_DIR, kind)
    os.makedirs(folder, exist_ok=True)
    name = uuid.uuid4().hex + "." + ext
    with open(os.path.join(folder, name), "wb") as f:
        f.write(data)
    return name


def delete_image(kind, name):
    if name and not name.startswith("seed_"):   # the sample pictures of problem2_DML.sql stay on the disk
        try:
            os.remove(os.path.join(UPLOAD_DIR, kind, os.path.basename(name)))
        except OSError:
            pass


# ---------- books ----------
def show_books(errors=[], form={}):
    books = lib("SELECT book_id, title, price, author_id, cover FROM book ORDER BY book_id", fetch="all")
    authors = lib("SELECT author_id, name FROM author ORDER BY name", fetch="all")
    names = {a["author_id"]: a["name"] for a in authors}   # only to show the name next to the id
    return render_template("books.html", books=books, authors=authors, names=names, errors=errors, form=form)


@app.route("/books")
def books():
    return show_books()


@app.route("/books/add", methods=["POST"])
def add_book():
    title, price, author_id = book_form()
    data, ext, image_errors = read_image()
    errors = book_errors(title, price, author_id) + image_errors
    if not errors:
        cover = save_image("books", data, ext) if data else None
        try:
            lib("INSERT INTO book (title, price, author_id, cover) VALUES (%s, %s, %s, %s)",
                (title, price, author_id, cover))
            return redirect("/books")
        except pymysql.err.IntegrityError:  # foreign key: this author does not exist (error 1452)
            delete_image("books", cover)    # the book was not saved, so the file is not needed
            errors = ["This author does not exist"]
    return show_books(errors, {"title": title, "price": price, "author_id": author_id})


@app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
def edit_book(book_id):
    book = lib("SELECT book_id, title, price, author_id, cover FROM book WHERE book_id = %s", (book_id,), "one")
    if book is None:
        abort(404)
    authors = lib("SELECT author_id, name FROM author ORDER BY name", fetch="all")
    if request.method == "GET":
        form = {"title": book["title"], "price": "%.2f" % book["price"], "author_id": book["author_id"]}
        return render_template("book_edit.html", book=book, authors=authors, errors=[], form=form)

    title, price, author_id = book_form()
    data, ext, image_errors = read_image()
    errors = book_errors(title, price, author_id) + image_errors
    if not errors:
        cover = book["cover"]                       # keep the old cover ...
        if data:
            cover = save_image("books", data, ext)  # ... unless a new one was chosen
        elif request.form.get("remove_image"):
            cover = None                            # ... or the "remove" box was ticked
        try:
            lib("UPDATE book SET title = %s, price = %s, author_id = %s, cover = %s WHERE book_id = %s",
                (title, price, author_id, cover, book_id))
            if cover != book["cover"]:
                delete_image("books", book["cover"])
            return redirect("/books")
        except pymysql.err.IntegrityError:
            if cover != book["cover"]:
                delete_image("books", cover)
            errors = ["This author does not exist"]
    form = {"title": title, "price": price, "author_id": author_id}
    return render_template("book_edit.html", book=book, authors=authors, errors=errors, form=form)


@app.route("/books/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    book = lib("SELECT cover FROM book WHERE book_id = %s", (book_id,), "one")
    lib("DELETE FROM book WHERE book_id = %s", (book_id,))
    if book:
        delete_image("books", book["cover"])
    return redirect("/books")


# ---------- authors ----------
def show_authors(errors=[], form={}):
    authors = lib("SELECT author_id, name, country, photo FROM author ORDER BY author_id", fetch="all")
    return render_template("authors.html", authors=authors, errors=errors, form=form)


@app.route("/authors")
def authors():
    return show_authors()


@app.route("/authors/add", methods=["POST"])
def add_author():
    name, country = author_form()
    data, ext, image_errors = read_image()
    errors = author_errors(name, country) + image_errors
    if errors:
        return show_authors(errors, {"name": name, "country": country})
    photo = save_image("authors", data, ext) if data else None
    lib("INSERT INTO author (name, country, photo) VALUES (%s, %s, %s)", (name, country, photo))
    return redirect("/authors")


@app.route("/authors/<int:author_id>/edit", methods=["GET", "POST"])
def edit_author(author_id):
    author = lib("SELECT author_id, name, country, photo FROM author WHERE author_id = %s", (author_id,), "one")
    if author is None:
        abort(404)
    if request.method == "GET":
        form = {"name": author["name"], "country": author["country"]}
        return render_template("author_edit.html", author=author, errors=[], form=form)

    name, country = author_form()
    data, ext, image_errors = read_image()
    errors = author_errors(name, country) + image_errors
    if errors:
        return render_template("author_edit.html", author=author, errors=errors,
                               form={"name": name, "country": country})
    photo = author["photo"]
    if data:
        photo = save_image("authors", data, ext)
    elif request.form.get("remove_image"):
        photo = None
    lib("UPDATE author SET name = %s, country = %s, photo = %s WHERE author_id = %s",
        (name, country, photo, author_id))
    if photo != author["photo"]:
        delete_image("authors", author["photo"])
    return redirect("/authors")


@app.route("/authors/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):
    author = lib("SELECT photo FROM author WHERE author_id = %s", (author_id,), "one")
    covers = lib("SELECT cover FROM book WHERE author_id = %s", (author_id,), "all")   # their books go too ...
    lib("DELETE FROM author WHERE author_id = %s", (author_id,))   # ... (ON DELETE CASCADE)
    if author:
        delete_image("authors", author["photo"])
    for b in covers:                                               # so remove their cover files as well
        delete_image("books", b["cover"])
    return redirect("/authors")


@app.errorhandler(404)
@app.errorhandler(413)
@app.errorhandler(500)
def error_page(e):  # friendly page instead of a raw error
    message = "That file is too big (2 MB at most per image)." if e.code == 413 \
        else "Something went wrong. Please try again."
    return render_template("error.html", message=message), e.code


if __name__ == "__main__":
    app.run(port=5000)
