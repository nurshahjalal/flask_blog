import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, logout_user, current_user, login_required
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, UpdatePostForm
from flaskblog.models import User, Post
"""
posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]
"""


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    # This is ascending order posts meaning older post always on top
    # posts = Post.query.paginate(page=page, per_page=2)

    # This is descending order posts meaning latest post always on top
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=2)

    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hash_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        # get the user
        user = User.query.filter_by(email=form.email.data).first()
        # check the user and password
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # login_user takes two args - user, and remember
            login_user(user, remember=form.remember.data)
            # get the next parameter from browser using get method
            # args is dictionary , get method won't throw error if next_page == none
            next_page = request.args.get('next')
            # this is Ternary Operator- in a single line
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_image(form_picture):
    path_to_save = os.path.join(app.root_path, "static/profile_pics/")
    print(path_to_save)
    # save image with random number
    random_hex = secrets.token_hex(8)
    # getting the extension of user's requested pic file
    _, pic_ext = os.path.splitext(form_picture.filename)
    pic_filename = random_hex + pic_ext
    # setting the save path
    # saving_destination = os.path.join(app.root_path, "static/profile_pics/" + pic_filename)
    saving_destination = path_to_save + pic_filename
    print(saving_destination)

    # resize the pics
    output_size = (125, 125)
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(saving_destination)

    return pic_filename


@app.route("/account", methods=['GET', 'POST'])
# @login_required is for to go to account user needs to log in
@login_required
def account():
    form = UpdateAccountForm()
    # if user wants to update username and email or any of them
    if form.validate_on_submit():
        # save profile pics if user wants to change
        if form.picture_file.data:
            # change the  profile image
            profile_image = save_image(form.picture_file.data)
            # Save the  profile image to DB under current user
            current_user.image_file = profile_image

        # replacing the current username with requested username
        current_user.username = form.username.data
        # replacing the current email with requested email
        current_user.email = form.email.data
        # commit to DB
        db.session.commit()
        # flash message to HTML page
        flash("Your Account has been updated", "success")
        return redirect(url_for('account'))

    # this is for prepopulated form
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been published", 'success')
        return redirect(url_for('home'))
    return render_template("create_post.html", title="New Post", form=form)


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)

    form = UpdatePostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your Post has been updated", 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template("update_post.html", title="Update Post", form=form)


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted", "success")
    return redirect(url_for("home"))\



@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)

    # query the current user
    user = User.query.filter_by(username=username).first_or_404()

    # get the specific user posts
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=2)

    return render_template('user_posts.html', posts=posts, user=user)
