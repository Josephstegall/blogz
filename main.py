from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:thestl@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'jfejfkflsk3465grdkfslw3r2'



class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_entry = db.Column(db.String(3000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blog_title, blog_entry, owner):
        self.blog_entry = blog_entry
        self.blog_title = blog_title
        self.owner = owner
        
    def validation(self):
        if self.blog_entry and self.blog_title:
            return True
        else:
            return False

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(150))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return str(self.username)


@app.before_request
def require_login():
    allowed_routes = ['login', 'display_entries','home', 'signup',  
    'index', 'logout']
    if 'username' not in session and request.endpoint not in allowed_routes:
        return redirect ('/login')

@app.route('/') #directs to home page
def index():
    users = User.query.all()
    #all_entries = Blog.query.all()
    #existing_user = User.query.filter_by(username).first()

    return render_template('index.html', users=users) 

   
@app.route('/blog', methods=['POST', 'GET']) #displays ALL blog posts
def display_entries():

    all_entries = Blog.query.all()
    
    blogId = request.args.get('id')
    userId = request.args.get('userid')
    
    #single_post = User.query.filter_by(user=session['user']).first()
    if blogId:
        post = Blog.query.filter_by(id=blogId).first()
        return render_template('singlepost.html',title=post.blog_title, body=post.blog_entry, user=post.owner.username,user_id=post.owner_id)
    if (userId):
        entries = Blog.query.filter_by(owner_id=userId).all()
        return render_template('singleuser.html', entries=entries)
    
    else: 
        return render_template('blog.html', title="All Blog Posts!", all_entries=all_entries, userId=userId)

@app.route('/newpost', methods=['POST', 'GET']) #enter new entries here
def newpost():
    blog_title = ""
    post_name = ""

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        post_name = request.form['post']

        owner = User.query.filter_by(username=session['username']).first()

        new_entry = Blog(blog_title, post_name, owner)

        if new_entry.validation():
            
            db.session.add(new_entry)
            db.session.commit()
            single_entry = "/blog?id=" + str(new_entry.id)
            return redirect(single_entry)
        
        else:
            flash ("Fill out all the fields you slacker!!", "error")
            return render_template('newpost.html')
    else:
        return render_template ('newpost.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    username=""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session['username'] = username
            flash("Logged in",'error')
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')
        
        if username == "":
            flash('Username cannot be blank', 'error')
        if password == "":
            flash('Password cannot be blank','error')       

    return render_template("login.html", title= "Login", username=username)

@app.route('/signup', methods=['POST' , 'GET'])
def signup():
    username =""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if len(username) < 2:
            flash('Must enter a unique username longer than 3 characters', 'error')
        if len(password) < 2:
            flash('Must enter a password longer than 3 characters', 'error')
        if password != verify:
            flash('Check your verification for typos!','error')
            return render_template ('signup.html', title="Sign Up")

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect ('/newpost')
        else:
            flash('There is already someone with that username. Try again.', 'error')

    return render_template('signup.html', title="Sign Up To Post A Blog Entry!")


@app.route('/logout', methods=['POST','GET'])
def logout():
    if session['username']:
        del session['username']
        return redirect('/blog')
    else:
        return redirect ('/login')
    

if __name__ == '__main__':
    app.run()