from flask import Flask, render_template, url_for, flash, redirect, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, \
                        login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)

# DB stuff
###################################################################
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = '5up3r pas5'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String)


# login stuff
###################################################################
class LoginForm(FlaskForm):
    username = StringField('Логин',
                        validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить')
    submit = SubmitField('Войти')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
# @login_required
def index():
    if current_user.is_authenticated:
        return render_template("main.html")
    else:
        return redirect(url_for("login"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # how many times user tried to login
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    else:
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data.lower()).first()
            if user and user.password == form.password.data:
                login_user(user, remember=form.remember.data)
                print(str(user) + ' logged in', 'green')
                return redirect(url_for('index'))
            else:
                flash('Неправильный логин или пароль!', 'danger')
                return redirect(url_for('login'))
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
	app.run(debug=True)
