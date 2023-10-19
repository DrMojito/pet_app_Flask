from flask import (Flask,
                   render_template,
                   url_for,
                   request,
                   flash,
                   session,
                   redirect,
                   abort,
                   g)
import sqlite3
import os

from FDataBase import FDataBase


DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'asdfo7w4013qwfasdf23wwerg'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route("/")
def index():
    db = get_db()
    dbase = FDataBase(db)
    return render_template('index.html', menu=dbase.getMenu(), posts = dbase.getPostsAnonce())


@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    db=get_db()
    dbase=FDataBase(db)
    
    if request.method == 'POST':
        if len(request.form["title"]) > 4 and len(request.form['text']) > 10:
            res = dbase.addPost(request.form["title"], request.form["text"])
            if not res:
                flash("Error add post", category = 'error')
            else:
                flash("Posts added", category = "success")
        else:
            flash("Error add post", category = 'error')
    return render_template('add_post.html', menu=dbase.getMenu(), title="Add post")


@app.route("/post/<int:id_post>")
def showPost(id_post):
    db = get_db()
    dbase = FDataBase(db)
    title, post = dbase.getPost(id_post)
    if not title:
        abort(404)

    return render_template('post.html',
                           menu=dbase.getMenu(),
                           title=title,
                           post=post)

@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html',
                           title="Page not found",
                           menu=dbase.getMenu())



if __name__ == "__main__":
    app.run(debug=True)