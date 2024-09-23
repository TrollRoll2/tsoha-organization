from flask import Flask
from flask import redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from os import getenv
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.secret_key = getenv("SECRET_KEY")
db = SQLAlchemy(app)

@app.route("/")
def index():
    return render_template("index.html") 

@app.route("/registration", methods=["POST", "GET"])
def registration_page():
    if request.method == "GET":
        return render_template("registration.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hash_pass = generate_password_hash(password)
        try:
            sql = text("INSERT INTO accounts (username, password, role) VALUES (:username, :password, :role)")
            db.session.execute(sql, {"username":username, "password":hash_pass, "role":"member"})
            db.session.commit()
            session["user"] = username
            sql_login = text("SELECT id FROM accounts WHERE username=:username")
            result = db.session.execute(sql_login, {"username":username})
            user = result.fetchone()
            session["account_id"] = user.id
            return redirect("/")
        
        except Exception as e:
            print(f"Error occurred: {e}")
            return render_template("error.html")


@app.route("/login", methods=["POST", "GET"])
def login_page():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        sql = text("SELECT id, password FROM accounts WHERE username=:username")
        result = db.session.execute(sql, {"username":username})
        user = result.fetchone()
        if user:
            if check_password_hash(user.password, password):
                session["user"] = username
                session["account_id"] = user.id
                return redirect("/")

        else:
            return render_template("error.html")


    if request.method == "GET":  
        return render_template("login.html")

@app.route("/logout")
def logout_page():
    del session["user"]
    return redirect("/")

@app.route("/user")
def user():
    if "user" in session:
        return render_template("user.html")
    else:
        return redirect("/")
    

@app.route("/user/questions")
def user_questions():
    if "user" in session:
        account_id = session["account_id"]
        sql = text("SELECT id, question FROM questions " \
                   "WHERE user_id = :account_id")
        result = db.session.execute(sql, {"account_id":account_id})
        questions = result.fetchall()
        return render_template("user_questions.html", questions=questions)
    else:
        return redirect("/")
    
@app.route("/user/review")
def user_review():
    if "user" in session:
        account_id = session["account_id"]
        sql = text("SELECT review, rating FROM reviews " \
                   "WHERE user_id = :account_id")
        result = db.session.execute(sql, {"account_id":account_id})
        review = result.fetchone()
        return render_template("user_review.html", review=review)
    else:
        return redirect("/")
    
@app.route("/question", methods=["POST", "GET"])
def question_page():
    if request.method == "POST":
        question = request.form["question"]
        account = session["account_id"]
        sql = text("INSERT INTO questions (question, user_id) VALUES (:question, :user_id)")
        db.session.execute(sql, {"question":question, "user_id":account})
        db.session.commit()
        return redirect(url_for("question_board"))

    else:
        return render_template("question.html")
    
@app.route("/questions")
def question_board():
    sql = text("SELECT * FROM questions")
    result = db.session.execute(sql)
    questions = result.fetchall()
    return render_template("question_board.html", questions=questions)

@app.route("/review", methods=["POST", "GET"])
def review_page():
    if "user" not in session:
        redirect(url_for("login_page"))

    if request.method == "POST":
        account_id = session["account_id"]
        sql_check = text("SELECT * FROM reviews WHERE user_id = :user_id")
        already = db.session.execute(sql_check, {"user_id": account_id}).fetchone()
        if already:
            return render_template("review.html", error="You have already left a review. Users can only submit 1 review.")
        review = request.form["review"]
        rating = request.form["rating"]
        account = session["account_id"]
        sql = text("INSERT INTO reviews (review, rating, user_id) VALUES (:review, :rating, :user_id)")
        db.session.execute(sql, {"review":review, "rating":rating, "user_id":account})
        db.session.commit()
        return redirect(url_for("review_board"))

    else:
        return render_template("review.html")
    
@app.route("/reviews")
def review_board():
    sql = text("SELECT review, rating, user_id FROM reviews")
    result = db.session.execute(sql)
    reviews = result.fetchall()
    return render_template("review_board.html", reviews=reviews)