from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "k4g1w4h1m1t5ud35u"

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner_id):
        self.title = title
        self.body = body
        self.owner_id = owner_id

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if password != verify:
            flash('Passwords do not match')
            return redirect('/register')

        existing_user = User.query.filter_by(username=username).first()

        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            flash('Username already exists.')
            return redirect('/register')
    
    return render_template('register.html')

@app.route('/', methods=['POST', 'GET'])
def index():
    user_list = User.query.all()
    return render_template('index.html', user_list=user_list)

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    post_list = Blog.query.all()
    user_list = User.query.all()
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner_id = User.query.filter_by(username = session['username']).first()
        owner_id = owner_id.id
        
        if title == "" or body == "":
            return render_template('newpost.html', returned_title=title, returned_body=body, error="Please ensure all boxes are filled in.", page_title="Add a Post")

        new_post = Blog(title, body, owner_id)
        db.session.add(new_post)
        db.session.commit()

        id = str(len(post_list) + 1)
                
        return redirect('blog?id=' + id)
    
    elif request.method == 'GET':
        id = str(request.args.get('id'))
        if id != "None":
            single_post = Blog.query.get(id)
            return render_template('blog.html', post_list=post_list, single_post=single_post, user_list=user_list, id=id, page_title="My Blog")
        else:
            return render_template('blog.html', post_list=post_list, user_list=user_list, id="all", page_title="My Blog")

@app.route('/singleuser')
def singleuser():
    user_id = (request.args.get('id'))
    post_list = Blog.query.filter_by(id=user_id).all()
    user_name = User.query.filter_by(id=user_id).first()

    return render_template('singleuser.html', post_list=post_list, user_name=user_name, page_title="Single User")

@app.route('/newpost')
def newpost():
    return render_template('newpost.html', page_title="Add a Post")

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()