from flask import (
    Flask,
    g,
    redirect,
    render_template,
    Response,
    request,
    url_for,
    session,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from passlib.hash import pbkdf2_sha256
import razorpay


app = Flask(__name__)

# Configuring mail and extracting Password from file
email = "gotocoders@gmail.com"
f = open("credentials.txt", "r")
password = f.read()
f.close()


mail = Mail(app)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = email
app.config["MAIL_PASSWORD"] = password
app.config["MAIL_USE_SSL"] = True
mail = Mail(app)


# Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///UnTuned_Database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "mai_nahi_bataunga"
db = SQLAlchemy(app)

# Tables
cartLink = db.Table(
    "cartLink",
    db.Column("email", db.String(50), db.ForeignKey("users.email")),
    db.Column("pid", db.Integer, db.ForeignKey("products.pid")),
)


class Users(db.Model):
    name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(150), nullable=False)

    # Defining relationship between users and products
    items = db.relationship(
        "Products", secondary=cartLink, backref=db.backref("link", lazy="dynamic")
    )

    def __repr__(self):
        return self.email


class Products(db.Model):
    pid = db.Column(db.Integer, primary_key=True)
    pname = db.Column(db.String(100), unique=True, nullable=False)
    pdesc = db.Column(db.Text, nullable=False)
    pprice = db.Column(db.Integer, nullable=False)
    pcategory = db.Column(db.String(20), nullable=False)
    # pimage = db.Column(db.Text, unique=True, nullable=False)
    imgid = db.Column(db.Integer, db.ForeignKey("images.imgid"))

    def __repr__(self):
        return f" {self.pid}, {self.pname} "


class Contact(db.Model):
    cid = db.Column(db.Integer, primary_key=True)
    cname = db.Column(db.String(40), nullable=False)
    cemail = db.Column(db.String(50), nullable=False)
    cphone = db.Column(db.Integer, nullable=False)
    cmessage = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f" {self.pid}, {self.pname} "


class Images(db.Model):
    imgid = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, unique=True, nullable=False)
    imgname = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f" {self.imgid}, {self.imgname}"


# Routes
@app.before_request
def before_request():
    g.user = None
    if "user_email" in session:
        user = Users.query.filter_by(email=session["user_email"]).first()
        g.user = user


@app.route("/")
def home():
    products = Products.query.all()
    return render_template("index.html", products=products)

@app.route('/category/<pcategory>')
def category(pcategory):
    if pcategory == 'all':
        return redirect(url_for('home'))
    else:
        products = Products.query.filter_by(pcategory=pcategory).all()
        return render_template("index.html", products=products)


@app.route("/getImg/<int:imgid>")
def getImage(imgid):
    pimg = Images.query.filter_by(imgid=imgid).first()
    return Response(pimg.img, mimetype=pimg.mimetype)


@app.route("/add_to_cart/<int:pid>", methods=["GET", "POST"])
def add_to_cart(pid):
    if request.method == "POST":
        if g.user is None:
            return redirect(url_for("login"))
        else:
            product = Products.query.filter_by(pid=pid).first()
            g.user.items.append(product)
            db.session.commit()
            return redirect(url_for("home"))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    loginFailed = 0
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # SELECT * FROM USER WHERE EMAIL=GIVEN_EMAIL : FIRST-FIRST_ENTITY
        user = Users.query.filter_by(email=email).first()
        if user and pbkdf2_sha256.verify(password, user.password) :
            session["user_email"] = user.email
            return redirect(url_for("home"))
        else:
            loginFailed = 1
            return render_template("login.html", loginFailed=loginFailed)

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form["phone"]
        address = request.form["address"]
        # securing user password with pbkdf2_sha256 hash method
        hashed_pass = pbkdf2_sha256.hash(password)

        user = Users(
            name=name, email=email, password=hashed_pass, phone=phone, address=address
        )
        db.session.add(user)
        db.session.commit()
        return render_template("login.html")

    return render_template("register.html")


@app.route("/contact", methods=["POST", "GET"])
def contact():
    messageSent = 0
    if request.method == "POST":
        cname = request.form["name"]
        cemail = request.form["email"]
        cphone = request.form["phone"]
        cmessage = request.form["message"]
        contact = Contact(cname=cname, cemail=cemail, cphone=cphone, cmessage=cmessage)
        db.session.add(contact)
        db.session.commit()

        msg = Message(
            "UnTuned Contact Response",
            sender=email,
            recipients=[cemail],
        )
        msg.body = f"""
        Hi {cname}, 

        Thank you for contacting us. 

        We've recieved your message and will get back to you within 24 hours.
        
        Best Regards,
        Team UnTuned
        """
        mail.send(msg)

        messageSent = 1

    return render_template("contact.html", messageSent=messageSent)


@app.route("/cart")
def cart():
    products_in_cart = 0
    if g.user is not None:
        if request.method == "POST":
            return redirect(url_for('pay'))
        
        products_in_cart = g.user.items
        
    return render_template("cart.html", products_in_cart=products_in_cart)



# Payment Integration
# To be hidden:
api = "rzp_test_xYIjFZqdWvjjiZ"
secret_key = "ohU35RgvOvYyYImzGubvIOqv"

@app.route('/pay', methods=["GET", "POST"])
def pay():
    order_amount = 500 * 100    # to be fetched from db
    client = razorpay.Client(auth = (api , secret_key))
    payment = client.order.create({'amount' : int(order_amount), 'currency' :'INR', 'payment_capture' : '1'})

    return render_template('pay.html', payment = payment)


@app.route("/logout")
def logout():
    session.pop("user_email", None)
    return redirect(url_for("home"))


@app.route("/account/<string:email>")
def account(email):
    return render_template("account.html")


@app.route("/upload", methods=["POST", "GET"])
def upload():
    if request.method == "POST":
        pname = request.form["pname"]
        pcategory = request.form["pcategory"]
        pprice = request.form["pprice"]
        pdesc = request.form["pdesc"]
        pimage = request.files["pimage"]

        # product = Products(pname=pname, pcategory=pcategory, pprice=pprice, pdesc=pdesc, pimage=pimage.read())

        # secure_filename(pimage.filename)

        # db.session.add(product)
        # db.session.commit()

        imgname = secure_filename(pimage.filename)
        mimetype = pimage.mimetype

        img = Images(img=pimage.read(), imgname=imgname, mimetype=mimetype)

        db.session.add(img)
        db.session.commit()

        product = Products(
            pname=pname,
            pcategory=pcategory,
            pprice=pprice,
            pdesc=pdesc,
            imgid=img.imgid,
        )

        db.session.add(product)
        db.session.commit()

    return render_template("upload.html")

@app.route("/success", methods=["POST", "GET"])
def success():
    return render_template("success.html")

if __name__ == "__main__":
    app.run(debug=True)
