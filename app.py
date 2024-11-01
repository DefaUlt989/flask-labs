import os
from datetime import datetime

from flask import Flask, request, render_template, make_response, redirect, url_for, flash, abort
from flask_login import login_user, login_required, LoginManager, UserMixin, current_user, logout_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash


from forms import *
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asjhfoijasoifjasoijw'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_EXTENSIONS'] = ['jpg', 'png', 'jpeg']
app.config['UPLOAD_FOLDER'] = 'static/images/'

login_manager = LoginManager()
login_manager.init_app(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    blogs = db.relationship('Blog', backref='author', cascade="all, delete-orphan")
    is_active = db.Column(db.Boolean, default=True)


class Blog(db.Model):
    __tablename__ = 'blog'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image = db.Column(db.String(80))
    created = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Blog %r>' % self.title

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/logout", methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('base.html', active_page='home')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User()
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.username = form.username.data
        user.email = form.email.data
        user.password = generate_password_hash(form.password.data, method='scrypt')
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template("registration.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user or not check_password_hash(user.password, form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember.data)
        return redirect(url_for('index'))

    return render_template('login.html', form=form)

@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first()
    if user == None:
        abort(404)

    return render_template('profile.html', active_page='profile', user=user)

@app.route('/my-blogs/')
@login_required
def my_blogs():
    my_blogs = current_user.blogs
    return render_template('my_blogs.html', my_blogs=my_blogs, active_page='my_blogs')

@app.route('/my-blogs/<int:blog_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    if blog.author.id != current_user.id:
        flash('You do not have permission to edit this blog', 'error')
        return redirect(url_for('index'))

    edit_form = EditBlogForm()

    if edit_form.validate_on_submit():
        blog.title = edit_form.title.data
        blog.content = edit_form.content.data
        db.session.commit()
        flash('Blog update successful!', 'success')
        return redirect(url_for('edit_blog', blog_id=blog.id))

    if request.method == 'GET':
        edit_form.title.data = blog.title
        edit_form.content.data = blog.content

    return render_template('edit_blog.html', form=edit_form, blog=blog)

@app.route('/my-blogs/<int:blog_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    if blog.author.id != current_user.id:
        flash('You do not have permission to delete this blog', 'error')
        return redirect(url_for('index'))
    Blog.query.filter_by(id=blog_id).delete()
    db.session.commit()
    flash('Delete successful !', 'success')
    return redirect(url_for('my_blogs'))

@app.route('/create-blog', methods=['POST', 'GET'])
@login_required
def create_blog():
    form = BlogForm()
    if form.validate_on_submit():
        new_blog = Blog()
        new_blog.title = form.title.data
        new_blog.content = form.content.data
        new_blog.author_id = current_user.id
        image = form.image.data
        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            new_blog.image = f"images/{filename}"

        db.session.add(new_blog)
        db.session.commit()
        flash('Blog post created successfully!', 'success')
        return redirect(url_for('create_blog'))
    return render_template('create_blog.html', form=form)


@app.route('/blogs-all')
def blogs():
    blogs_list = Blog.query.all()
    return render_template('blogs_list.html', blogs=blogs_list, active_page='blog')


@app.route('/blog/<int:blog_id>')
def blog(blog_id):
    blog_data = Blog.query.get(blog_id)
    return render_template('blog.html', blog=blog_data, active_page='blog')


@app.route('/calculate', methods=['GET', 'POST'])
def calculator():
    form = Calculator()
    result = None
    history = request.cookies.get('history')
    history = json.loads(history) if history else []
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                num1 = float(form.obj_1.data)
                num2 = float(form.obj_2.data)
                operation = form.operand.data

                if operation == '+':
                    result = num1 + num2
                elif operation == '-':
                    result = num1 - num2
                elif operation == '*':
                    result = num1 * num2
                elif operation == '/':
                    if num2 != 0:
                        result = num1 / num2
                    else:
                        flash('Error: Division by zero')
                        result = "Error"
                else:
                    flash('Invalid operation')
                    result = "Error"

                if result != "Error":
                    history.append(f'{num1} {operation} {num2} = {result}')

                response = make_response(redirect(url_for('calculator')))
                response.set_cookie('history', json.dumps(history))
                response.set_cookie('result', str(result))
                return response

            except Exception as e:
                flash(str(e))
                result = "Error"

    stored_result = request.cookies.get('result')
    if stored_result:
        result = stored_result
        response = make_response(
            render_template('index.html', active_page='calculator', form=form, result=result, history=history))
        response.set_cookie('result', '', expires=0)
        return response

    return render_template('index.html', active_page='calculator', form=form, result=result, history=history)


if __name__ == '__main__':
    app.run(debug=True)
