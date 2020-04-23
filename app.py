from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
import datetime

"""
this is a tutorial from youtube Corey Schafer
https://www.youtube.com/watch?v=QnDWIZuWYW0
"""

"""
This is a sample blog post Flask app - has different pages - home, about, form
and user post
"""
app = Flask("__name__")
app.config['SECRET_KEY'] = 'vfe7a66f045e1b19c675eed94d01433ff'

posts = [
    {
        'author': 'Noam Chintus',
        'title': 'End Of World',
        'content': 'Where are we going with this',
        'date_posted': str(datetime.date)
    },

    {
        'author': 'Steve Martin',
        'title': 'New Beginning',
        'content': 'We See the light end of tunnel',
        'date_posted': str(datetime.date)
    },
]


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # using flash for one time message, second arg is the catagory of the message
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', form=form, title='Register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # log in validation
    if form.email.data == 'admin@blog.com' and form.password.data == 'test123':
        flash('Log in successful !', 'success')
        return redirect(url_for('home'))
    else:
        flash('Please check username and password', 'danger')
    return render_template('login.html', form=form, title='Login')


if __name__ == "__main__":
    app.run(debug=True)

