from flask import Flask
from flask import redirect
from flask import render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import DateField,FloatField,StringField
from wtforms.validators import DataRequired,Email
from flask_mail import Mail, Message


app = Flask(__name__)
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'wangyang'
db = SQLAlchemy(app)

app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT']  = 587
app.config['MAIL_USE_SSL']  = False
app.config['MAIL_USE_TLS']  = True
app.config.from_pyfile('config.cfg')
mail = Mail(app)


class WeightHeightForm(FlaskForm):
    weight = FloatField("Weight", validators=[DataRequired()])
    height = FloatField("Height", validators=[DataRequired()])
    date = DateField("Date", validators=[DataRequired()])

class MailForm(FlaskForm):
    mail = StringField("mail", validators=[Email()])

class Mail(db.Model):
    """
    user data in  database
    """
    # user id
    id = db.Column(db.Integer, primary_key=True)
    # user email
    mail = db.Column(db.String, nullable=False)

class User(db.Model):
    """
    user data in  database
    """
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


# create database
db.create_all()


@app.route('/', methods=['GET'])
def index():
    records = User.query.order_by(User.date).all()
    weight = [r.weight for r in records]
    height = [r.height for r in records]
    bmi = [r.bmi for r in records]
    labels = [r.date.strftime('%Y/%m/%d') for r in records]
    warning = True if len(weight) >= 2 and weight[-1] - weight[-2] > 1 else False
    return render_template('index.html', weight=weight, height=height,
                           bmi=bmi,labels=labels, warning=warning)

@app.route('/update', methods=['GET', 'POST'])
def update():
    form = WeightHeightForm()
    if form.validate_on_submit():
        # write records to database
        weight = form.weight.data
        height = form.height.data
        bmi = weight / (height * height)
        date = form.date.data
        user = User(weight=weight, height=height, bmi=bmi, date=date)
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    return render_template('update.html', form=form)

@app.route('/question')
def question():
    return render_template('question.html')

@app.route('/news', methods=['GET', 'POST'])
def news():
    form = MailForm()
    if form.validate_on_submit():
        # write records to database
        mail = form.mail.data
        user = Mail(mail=mail)
        db.session.add(user)
        db.session.commit()
        return redirect('/subscribed')
    return render_template('news.html', form=form)

@app.route('/subscribed')
def subscribed():
    msg = Message('Thank you for subscribing to our newsletter',sender='181192P@mymail.nyp.edu.sg')
    msg.recipients=['1527638985@qq.com']
    mail.send(msg)
    return render_template('subscribed.html')

@app.route('/plan')
def plan():
    return render_template('plan.html')


app.run()
