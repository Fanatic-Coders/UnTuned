from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
db = SQLAlchemy(app)

class Users(db.Model):
    name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(50), primary_key = True)
    password = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.INTEGER(10), nullable=False)
    address = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return self.email

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/cart')
def cart():
    return render_template('cart.html')


if __name__ == '__main__':
    app.run(debug=True)
