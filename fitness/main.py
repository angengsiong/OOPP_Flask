from flask import Flask, request
from flask import redirect
from flask import render_template, url_for, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import DateField, FloatField, IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length
from flask_mail import Mail, Message
from flask_moment import Moment
from datetime import datetime



app = Flask(__name__)
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'wangyang'
db = SQLAlchemy(app)

app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USE_TLS'] = True
app.config.from_pyfile('config.cfg')
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
moment = Moment(app)
mail = Mail(app)


class WeightHeightForm(FlaskForm):
    weight = FloatField("Weight", validators=[DataRequired()])
    height = FloatField("Height", validators=[DataRequired()])
    sleep = IntegerField("Sleep", validators=[DataRequired()])


class User(db.Model):

    # user id
    id = db.Column(db.Integer, primary_key=True)
    # user weight
    weight = db.Column(db.Float, nullable=False)
    # user height
    height = db.Column(db.Float, nullable=False)
    # user bmi
    bmi = db.Column(db.Float, nullable=False)
    # date
    date = db.Column(db.Date, nullable=False)
    # sleeping hour
    sleep = db.Column(db.Integer, nullable=False)


class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    calorie = db.Column(db.Float, nullable=False)


class Mail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(100), nullable=False)


class Messager(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(200))
    name = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class TextForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 20)])
    body = TextAreaField('Message', validators=[DataRequired(), Length(1, 200)])
    submit = SubmitField()


class MailForm(FlaskForm):
    mail = StringField('mail', validators=[DataRequired(), Email()])
    submit = SubmitField()


# create database

db.create_all()


@app.route('/', methods=['GET'])  # Completed
def index():
    records = User.query.order_by(User.date).all()
    weight = [r.weight for r in records]
    height = [r.height for r in records]
    bmi = [r.bmi for r in records]
    sleep = [r.sleep for r in records]
    labels = [r.date.strftime('%Y/%m') for r in records]
    warning = True if len(weight) >= 2 and weight[-1] - weight[-2] > 1 else False
    return render_template('index.html', weight=weight, height=height,
                           bmi=bmi, sleep=sleep, labels=labels, warning=warning)


@app.route('/update', methods=['GET', 'POST'])  # COMPLETED
def update():
    form = WeightHeightForm()
    if form.validate_on_submit():
        # write records to database
        weight = form.weight.data
        height = form.height.data
        sleep = form.sleep.data
        bmi = weight / (height * height)
        date = datetime.date.today()
        user = User(weight=weight, height=height, bmi=bmi, date=date, sleep=sleep)
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    return render_template('update.html', form=form)


@app.route('/news', methods=['GET', 'POST'])  # completed
def news():
    form = MailForm()
    if form.validate_on_submit():
        mail = request.form.get("mail")
        user = Mail(mail=mail)
        email = Mail.query.filter_by(mail=mail).first()
        if not email:
            db.session.add(user)
            db.session.commit()
            flash("You have successfully subscribed!")
            msg = Message('Thank you for subscribing to our newsletter', sender='181192P@mymail.nyp.edu.sg')
            msg.recipients = [mail]
            msg.body = "Lets Start Your Fitness Journey Now!"
            mail.send(msg)
        else:
            flash("You have already subscribed!")
    return render_template('news.html', form=form)


@app.route('/plan', methods=['GET', 'POST'])
def plan():
    if request.method == 'GET':
        return render_template('plan.html')
    else:
        calorie = request.form.get('total')
        user = Plan(calorie=calorie)
        db.session.add(user)
        db.session.commit()
        return render_template('plan.html')


@app.route('/comment', methods=['GET', 'POST'])  # completed
def comment():
    messages = Messager.query.order_by(Messager.timestamp.desc()).all()
    form = TextForm()
    if form.validate_on_submit():
        name = form.name.data
        body = form.body.data
        message = Messager(body=body, name=name)
        db.session.add(message)
        db.session.commit()
        flash("You have successfully post your comment!")
        return redirect(url_for('comment'))
    return render_template('comment.html', form=form, messages=messages)


@app.route('/sender', methods=['GET', 'POST'])  # completed
def sender():
    if request.method == 'GET':
        return render_template('sender.html')
    else:
        body = request.form.get('body')
        mails = Mail.query.all()
        usermails = [m.mail for m in mails]
        message = Message("This month's newsletter", sender='181192P@mymail.nyp.edu.sg')
        for usermail in usermails:
            message.recipients = [usermail]
            message.body = body
            mail.send(message)
        return render_template('sender.html', news=news)


app.run()
