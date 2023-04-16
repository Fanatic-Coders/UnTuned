from bson.objectid import ObjectId
from flask import Response, session, request, render_template, redirect, url_for, g, Flask
from flask_mail import Mail, Message
from gridfs import GridFS
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
from pymongo import MongoClient
import random, razorpay

# Database connection

client = MongoClient('mongodb://localhost:27017/')
db = client['UnTunedDB']
users_col = db['users']
products_col = db['products']
contact_col = db['contact']
images_col = db['images']


# Configuring mail and extracting Passwords from file
email = "gotocoders@gmail.com"
f = open("credentials.txt", "r")
password = f.readline().strip()
api = f.readline().strip()
secret_key = f.readline().strip()
db_secret_key = f.readline().strip()
f.close()


# App and mail configuration
app = Flask(__name__)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = email
app.config["MAIL_PASSWORD"] = password
mail = Mail(app)




# Routes
@app.before_request
def before_request():
    g.user = None
    if "user_email" in session:
        user = users_col.find_one({"email": session["user_email"]})
        g.user = user




@app.route("/")
def home():
    products = products_col.find()
    for product in products:
        product["pdesc"] = ' '.join(product["pdesc"].split())
    return render_template("index.html", products=products)





@app.route('/category/<pcategory>')
def category(pcategory):
    if pcategory == 'all':
        return redirect(url_for('home'))
    else:
        products = products_col.find({"pcategory": pcategory})
        return render_template("index.html", products=products)







@app.route("/getImg/<imgid>")
def getImage(imgid):
    pimg = images_col.find_one({"imgid": imgid})
    return Response(pimg["img"], mimetype=pimg["mimetype"])








@app.route("/add_to_cart/<pid>", methods=["GET", "POST"])
def add_to_cart(pid):
    if request.method == "POST":
        if g.user is None:
            return redirect(url_for("login"))
        else:
            product = products_col.find_one({"pid": pid})
            users_col.update_one({"email": g.user["email"]}, {"$push": {"items": product}})
            return redirect(url_for("home"))







@app.route("/contact", methods=["POST", "GET"])
def contact():
    messageSent = 0
    if request.method == "POST":
        cname = request.form["name"]
        cemail = request.form["email"]
        cphone = request.form["phone"]
        cmessage = request.form["message"]
        contact = {"cname": cname, "cemail": cemail, "cphone": cphone, "cmessage": cmessage}
        contact_col.insert_one(contact)

        msg = Message(
            "UnTuned Contact Response",
            sender=email,
            recipients=[cemail],
        )
        msg.body = f"""
        Hi {cname}, 

        Thank you for contacting us. 

        We've received your message and will get back to you within 24 hours.
        
        Best Regards,
        Team UnTuned
        """
        mail.send(msg)

        messageSent = 1

    return render_template("contact.html", messageSent=messageSent)








@app.route("/cart")
def cart():
    client = razorpay.Client(auth = (api , secret_key))
    payment = client.order.create({'amount': random.randint(5,1000), 'currency' :'INR', 'payment_capture' : '1'})

    products_in_cart = 0
    if g.user is not None:
        if request.method == "POST":
            return redirect(url_for('pay'))
        
        user_email = session["user_email"]
        user = db.users.find_one({"email": user_email})
        if user is not None:
            product_ids = user.get("items")
            products_in_cart = []
            for product_id in product_ids:
                product = db.products.find_one({"_id": ObjectId(product_id)})
                products_in_cart.append(product)

    return render_template("cart.html", products_in_cart=products_in_cart, payment=payment)
   




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
        user = db.users.find_one({"email": email})
        if email == "admin@untuned.com":
            if user and check_password_hash(user["password"], password):
                session["user_email"] = user["email"]
                return redirect(url_for("upload"))
        if user and check_password_hash(user["password"], password):
            session["user_email"] = user["email"]
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
        # securing user password with generate_password_hash method
        hashed_pass = generate_password_hash(password)

        user = {
            "name": name,
            "email": email,
            "password": hashed_pass,
            "phone": phone,
            "address": address
        }
        db.users.insert_one(user)
        return render_template("login.html")

    return render_template("register.html")





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

        imgname = secure_filename(pimage.filename)
        mimetype = pimage.mimetype

        fs = GridFS(db)
        file_id = fs.put(pimage.read(), filename=imgname, contentType=mimetype)

        product = products_col(
            pname=pname,
            pcategory=pcategory,
            pprice=pprice,
            pdesc=pdesc,
            imgid=file_id,
        )

        db.session.add(product)
        db.session.commit()

    return render_template("upload.html")






@app.route("/success", methods=["POST", "GET"])
def success():
    return render_template("success.html")






if __name__ == "__main__":
    app.run(debug=True)