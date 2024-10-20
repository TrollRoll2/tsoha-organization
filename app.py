from flask import Flask
from flask import redirect, render_template, request, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from os import getenv
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
import secrets

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.secret_key = getenv("SECRET_KEY")
db = SQLAlchemy(app)

def csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16) 
    return session['csrf_token']

def csrf_valid(token):
    if session.get('csrf_token') != token:
        return False
    return True

@app.context_processor
def csrf_function():
    return {'csrf_token': csrf_token()}

@app.route("/")
def index():
    if "user" in session:
        account_id = session["account_id"]
        sql = text("SELECT role FROM accounts WHERE id = :user_id")
        admincheck = db.session.execute(sql, {"user_id": account_id}).fetchone()
        if admincheck[0] == "admin":
            return render_template("index.html", admin="confirm")
        
    return render_template("index.html") 

@app.route("/accounts")
def accounts():
    if "user" not in session:
        return redirect(url_for("login_page"))

    try:
        account_id = session["account_id"]
        sql = text("SELECT role FROM accounts WHERE id = :user_id")
        admincheck = db.session.execute(sql, {"user_id": account_id}).fetchone()
        if admincheck[0] != "admin":
            return render_template("unauthorized.html")
        sql_accounts = text("SELECT * FROM accounts ORDER BY id")
        result = db.session.execute(sql_accounts)
        users = result.fetchall()
        return render_template("accounts.html", users=users)
    
    except:
        return render_template("error.html", message="Something seems to have broken. If this error occurs again, please contact an admin")
    
@app.route("/account/<int:id>")
def account(id):
    if "user" not in session:
        return redirect(url_for("login_page"))

    try:
        account_id = session["account_id"]
        sql = text("SELECT role FROM accounts WHERE id = :user_id")
        admincheck = db.session.execute(sql, {"user_id": account_id}).fetchone()
        if admincheck[0] != "admin":
            return render_template("unauthorized.html")
        sql_account = text("SELECT username FROM accounts WHERE id = :account_id")
        result = db.session.execute(sql_account, {"account_id":id})
        user = result.fetchone()
        sql_questions = text("SELECT id, question, approved FROM questions WHERE user_id = :account_id")
        result2 = db.session.execute(sql_questions, {"account_id":id})
        questions = result2.fetchall()
        sql_review = text("SELECT review, rating FROM reviews WHERE user_id = :account_id")
        result3 = db.session.execute(sql_review, {"account_id":id})
        review = result3.fetchone()
        return render_template("account_info.html", user=user, questions=questions, review=review)

    except:
        return render_template("error.html", message="Something seems to have broken. If this error occurs again, please contact an admin")


@app.route("/registration", methods=["POST", "GET"])
def registration_page():
    if request.method == "GET":
        return render_template("registration.html")

    if request.method == "POST":
        if not csrf_valid(request.form.get('csrf_token')):
            return render_template("error.html", message="CSRF token is invalid")

        username = request.form["username"]
        password = request.form["password"]

        if len(username) < 6:
            flash("Username must be at least 6 characters long.", "error")
            return redirect(url_for('registration_page'))
        
        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return redirect(url_for('registration_page'))

        hash_pass = generate_password_hash(password)

        try:
            sql_check = text("SELECT * FROM accounts WHERE username=:username")
            result_check = db.session.execute(sql_check, {"username": username})
            existing_user = result_check.fetchone()

            if existing_user:
                flash("Username is already taken.", "error")
                return redirect(url_for('registration_page'))
            
            sql = text("INSERT INTO accounts (username, password, role) VALUES (:username, :password, :role)")
            db.session.execute(sql, {"username":username, "password":hash_pass, "role":"member"})
            db.session.commit()
            session["user"] = username
            sql_login = text("SELECT id FROM accounts WHERE username=:username")
            result = db.session.execute(sql_login, {"username":username})
            user = result.fetchone()
            session["account_id"] = user.id
            return redirect("/")
        
        except:
            return render_template("error.html", message="Something seems to have broken. If this error occurs again, please contact an admin")

@app.route("/login", methods=["POST", "GET"])
def login_page():
    if request.method == "POST":
        if not csrf_valid(request.form.get('csrf_token')):
            return render_template("error.html", message="CSRF token is invalid")

        username = request.form["username"]
        password = request.form["password"]
        
        try:
            sql = text("SELECT id, password FROM accounts WHERE username=:username")
            result = db.session.execute(sql, {"username": username})
            user = result.fetchone()

            if user is None:
                flash("User not found", "error")
                return redirect(url_for('login_page'))

            if check_password_hash(user.password, password):
                session["user"] = username
                session["account_id"] = user.id
                return redirect("/")
            
            else:
                flash("Invalid password", "error")
                return redirect(url_for('login_page'))
        
        except:
            return render_template("error.html", message="Something seems to have broken. If this error occurs again, please contact an admin")


    if request.method == "GET":  
        return render_template("login.html")

@app.route("/logout")
def logout_page():
    del session["user"]
    del session["account_id"]
    return redirect("/")

@app.route("/user")
def user():
    if "user" in session:
        return render_template("user.html")
    else:
        return redirect("/")
    

@app.route("/user/questions", methods=["POST", "GET"])
def user_questions():
    if request.method == "POST":
        if not csrf_valid(request.form.get('csrf_token')):
            return render_template("error.html", message="CSRF token is invalid")

        question = request.form["question"]
        try:
            sql = text("DELETE FROM questions WHERE id=:question")
            result = db.session.execute(sql, {"question":question})
            db.session.commit()
            return redirect("/user/questions")
        
        except:
            return render_template("error.html", message="Something seems to have broken. If this error occurs again, please contact an admin")

    if request.method == "GET":
        if "user" in session:
            account_id = session["account_id"]
            sql = text("SELECT id, question FROM questions " \
                    "WHERE user_id = :account_id")
            result = db.session.execute(sql, {"account_id":account_id})
            questions = result.fetchall()
            return render_template("user_questions.html", questions=questions)
        else:
            return redirect("/")
    
@app.route("/user/review", methods=["POST", "GET"])
def user_review():
    if request.method == "POST":
        if not csrf_valid(request.form.get('csrf_token')):
            return render_template("error.html", message="CSRF token is invalid")
        
        account_id = session["account_id"]
        try:
            sql = text("DELETE FROM reviews WHERE user_id=:account_id")
            result = db.session.execute(sql, {"account_id":account_id})
            db.session.commit()
            return redirect("/user/review")
        
        except:            
            return render_template("error.html", message="Something seems to have broken. If this error occurs again, please contact an admin")

    if request.method == "GET":
        if "user" in session:
            account_id = session["account_id"]
            sql = text("SELECT review, rating, approved FROM reviews " \
                    "WHERE user_id = :account_id")
            result = db.session.execute(sql, {"account_id":account_id})
            review = result.fetchone()
            return render_template("user_review.html", review=review)
        else:
            return redirect("/")
    
@app.route("/question", methods=["POST", "GET"])
def question_page():
    if request.method == "POST":
        if not csrf_valid(request.form.get('csrf_token')):
            return render_template("error.html", message="CSRF token is invalid")

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
    sql = text("SELECT * FROM questions WHERE approved = TRUE")
    result = db.session.execute(sql)
    questions = result.fetchall()
    return render_template("question_board.html", questions=questions)

@app.route("/review", methods=["POST", "GET"])
def review_page():
    if "user" not in session:
        redirect(url_for("login_page"))

    if request.method == "POST":
        if not csrf_valid(request.form.get('csrf_token')):
            return render_template("error.html", message="CSRF token is invalid")

        account_id = session["account_id"]
        sql_check = text("SELECT * FROM reviews WHERE user_id = :user_id")
        already = db.session.execute(sql_check, {"user_id": account_id}).fetchone()
        if already:
            flash("You have already left a review.", "error")
            return redirect(url_for('review_page'))
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
    sql = text("SELECT review, rating, user_id FROM reviews WHERE approved = TRUE")
    result = db.session.execute(sql)
    reviews = result.fetchall()
    average = text("SELECT AVG(rating) FROM reviews WHERE approved = TRUE")
    result2 = db.session.execute(average)
    avrgresult = result2.fetchone()[0]
    return render_template("review_board.html", reviews=reviews, avrgresult=round(avrgresult, 2))

@app.route("/admin")
def control_center():
    if "user" not in session:
        return redirect(url_for("login_page"))

    try:
        account_id = session["account_id"]
        sql = text("SELECT role FROM accounts WHERE id = :user_id")
        admincheck = db.session.execute(sql, {"user_id": account_id}).fetchone()
        if admincheck[0] == "admin":
            return render_template("admin.html")
        
        else:
            return render_template("unauthorized.html")
    
    except:        
        return render_template("error.html", message="Something seems to have broken. If this error occurs again, please contact an admin")
    
@app.route("/admin/reviews", methods=["POST", "GET"])
def admin_reviews():
    if "user" not in session:
        return redirect(url_for("login_page"))

    if request.method == "POST":
        if not csrf_valid(request.form.get('csrf_token')):
            return render_template("error.html", message="CSRF token is invalid")

        review_id = request.form["review_id"]
        action = request.form["action"]

        try:
            if action == "Delete question":
                sql = text("DELETE FROM reviews WHERE id=:review_id")
                result = db.session.execute(sql, {"review_id":review_id})

            elif action == "Approve review":
                sql = text("UPDATE reviews SET approved = TRUE WHERE id=:review_id")
                result = db.session.execute(sql, {"review_id":review_id})

            db.session.commit()
            return redirect("/admin/reviews")

        except:          
            return render_template("error.html", message="Something seems to have broken. If this error occurs again, please contact an admin")

    if request.method == "GET":

        try:
            account_id = session["account_id"]
            sql = text("SELECT role FROM accounts WHERE id = :user_id")
            admincheck = db.session.execute(sql, {"user_id": account_id}).fetchone()
            if admincheck[0] != "admin":
                return render_template("unauthorized.html")
            
            sql_reviews = text("SELECT * FROM reviews")
            result = db.session.execute(sql_reviews)
            reviews = result.fetchall()
            return render_template("admin_reviews.html", reviews=reviews)
        
        except:
            return render_template("error.html", message="Something seems to have broken. If this error occurs again, please contact an admin")
        
@app.route("/admin/questions", methods=["POST", "GET"])
def admin_questions():
    if "user" not in session:
        redirect(url_for("login_page"))

    if request.method == "POST":
        if not csrf_valid(request.form.get('csrf_token')):
            return render_template("error.html", message="CSRF token is invalid")

        question_id = request.form["question_id"]
        action = request.form["action"]

        try:
            if action == "Delete question":
                sql = text("DELETE FROM questions WHERE id=:question_id")
                result = db.session.execute(sql, {"question_id":question_id})

            elif action == "Approve question":
                sql = text("UPDATE questions SET approved = TRUE WHERE id=:question_id")
                result = db.session.execute(sql, {"question_id":question_id})

            db.session.commit()
            return redirect("/admin/questions")
        
        except:
            return render_template("error.html", message="Something seems to have broken. If this error occurs again, please contact an admin")

    if request.method == "GET":

        try:
            account_id = session["account_id"]
            sql = text("SELECT role FROM accounts WHERE id = :user_id")
            admincheck = db.session.execute(sql, {"user_id": account_id}).fetchone()
            if admincheck[0] != "admin":
                return render_template("unauthorized.html")
            
            sql_questions = text("SELECT * FROM questions")
            result = db.session.execute(sql_questions)
            questions = result.fetchall()
            return render_template("admin_questions.html", questions=questions)
        
        except:
            return render_template("error.html", message="Something seems to have broken. If this error occurs again, please contact an admin")