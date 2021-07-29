from flask import (
    Flask,
    g, 
    redirect, 
    render_template, 
    request, 
    url_for, 
    session
)
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'mai_nahi_bataunga'
db = SQLAlchemy(app)

class Users(db.Model):
    name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(50), primary_key = True)
    password = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return self.email


@app.before_request
def before_request():
    g.user = None
    if 'user_email' in session:
        user = Users.query.filter_by(email=session['user_email']).first()
        g.user = user

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    loginFailed = 0
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']

        # SELECT * FROM USER WHERE EMAIL=GIVEN_EMAIL : FIRST-FIRST_ENTITY
        user = Users.query.filter_by(email=email).first()
        if user and user.password == password:
            session['user_email'] = user.email
            return redirect(url_for('home'))
        else:
            loginFailed = 1
            return render_template('login.html' , loginFailed=loginFailed)

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        address = request.form['address']
        user = Users(name=name, email=email, password=password, phone=phone, address=address)
        db.session.add(user)
        db.session.commit()
        return render_template('login.html')

    return render_template('register.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/cart')
def cart():
    a = 5
    return render_template('cart.html' , a=a)

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
