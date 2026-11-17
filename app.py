"""
My system has 2 kinds of user: regular users, volunteers, admin.
Choose Register on the main page in order to register as a regular user.
Sign up at the main page to be a volunteer, after approved by an admin,
you can manage the applications. 
Log in as an admin: user name is yixhan password is yixhan123
Or run 'bootstrap_admin.py'
"""
from flask import Flask, abort, render_template, session, redirect, url_for, g, request
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from database import get_db, close_db
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from forms import RegistrationForm, LoginForm,applyForm, filterForm, volunteerForm, manageForm, reviewForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "this-is-my-secret-key"
app.teardown_appcontext(close_db) # whenever finish the route, close the db
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
CSRFProtect(app)

@app.before_request
def load_logged_in_user():
    g.user = session.get("user_id", None)
    
def login_required(view):
    @wraps(view)
    def wrapped_view(*args,**kwargs):
        if g.user is None:
            return redirect(url_for("login", next=request.url))
        return view(*args,**kwargs)
    return wrapped_view

def role_required(*allowed_roles):
    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if g.user is None:
                return redirect(url_for("login", next=request.url))
            if g.role not in allowed_roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped_view
    return decorator

@app.before_request
def load_role():
    g.role = "guest"
    g.is_volunteer = False
    if g.user is not None:
        db = get_db()
        user = db.execute("SELECT role FROM users WHERE user_id = ?", (g.user,)).fetchone()
        if user is None:
            session.clear()
            g.user = None
        else:
            g.role = user["role"]
            g.is_volunteer = g.role in ("volunteer", "admin")

@app.route("/register", methods=["GET","POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        db = get_db()
        conflict_user = db.execute("""SELECT * FROM users
                WHERE user_id = ?;""",(user_id,)).fetchone()
        if conflict_user is not None:
            form.user_id.errors.append("User name already taken!")
        else:
            db.execute("""INSERT INTO users(user_id,password)
                       VALUES (?,?);""",
                       (user_id,generate_password_hash(password)))
            db.commit()
            return redirect( url_for("login") )
    return render_template("register.html", form=form)
    

@app.route("/login", methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        db = get_db()
        user = db.execute("""SELECT * FROM users
                          WHERE user_id = ?;""",(user_id,)).fetchone()
        if user is None:
            form.user_id.errors.append("No such user name!")
        elif not check_password_hash(user["password"], password):
            form.password.errors.append("Incorrect password!")
        else:
            session.clear()
            session["user_id"] = user_id
            next_page = request.args.get("next")
            if not next_page:
                next_page = url_for("index")
            return redirect(next_page)
    return render_template("login.html", form=form)
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect( url_for("index") )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/pets", methods=["GET", "POST"])
def pets():
    form = filterForm()
    
    if form.validate_on_submit():
        speciesFilter = form.speciesFilter.data  
        db = get_db()

        if speciesFilter == 'all':
            pets = db.execute("""SELECT * FROM pets
                              WHERE availability = 'available';""").fetchall()
        else:
            pets = db.execute("""SELECT * FROM pets
                                WHERE species = ? AND availability = 'available';""", (speciesFilter,)).fetchall()
    else:
        # Default to show all pets
        db = get_db()
        pets = db.execute("""SELECT * FROM pets
                          WHERE availability = 'available';""").fetchall()
        
    return render_template("pets.html", pets=pets,form=form)

@app.route("/pet/<int:pet_id>")
def pet(pet_id):
    db = get_db()
    pet = db.execute("""SELECT * FROM pets 
                         WHERE pet_id = ?;""",(pet_id,)).fetchone()
    reviews = db.execute("""SELECT * FROM reviews 
                         WHERE pet_id = ?;""",(pet_id,)).fetchall()
    if not reviews:
        message = "Has not been reviewed yet!"
    else:
        message = ""
    return render_template("pet.html", pet=pet,message=message,reviews=reviews)

@app.route("/favorite")
@login_required
def favorite():
    message=""
    if "favorite" not in session:
        session["favorite"] = {}
    names = {}
    db = get_db()
    for pet_id in session["favorite"]:
        pet = db.execute("""SELECT * FROM pets
                          WHERE pet_id = ?;""",(pet_id,)).fetchone()
        name = pet["name"]
        names[pet_id] = name
        
    # return values of query string
    '''flask.Request.args:
    A MultiDict with the parsed contents of the query string. (The part in the URL after the question mark).'''
    message = request.args.get('message')
    
    return render_template("favorite.html", favorite=session["favorite"], names=names, message=message)


@app.route("/add_to_favorite/<int:pet_id>")
@login_required
def add_to_favorite(pet_id):
    message=""
    
    if "favorite" not in session:
        session["favorite"] = {}
    if pet_id not in session["favorite"]:
        session["favorite"][pet_id] = pet_id
    else:
        message = "You have already liked this one!"
    session.modified = True
    return redirect( url_for("favorite",message=message))

@app.route("/remove_from_favorite/<int:pet_id>")
@login_required
def remove_from_favorite(pet_id):
    if "favorite" in session and pet_id in session["favorite"]:
        del session["favorite"][pet_id]
        session.modified = True
    return redirect(url_for("favorite"))

@app.route("/apply",methods=["GET", "POST"])
@login_required
def apply():
    
    db = get_db()
    conflict_apply = db.execute("""SELECT * FROM applications
            WHERE user_id = ? AND status !='Completed';""",(g.user,)).fetchone()
    
    if conflict_apply is not None:
        message = "You can only have one application at a time."
        return render_template("apply.html", message=message)
    
    form = applyForm()
    message =""    
        
    if form.validate_on_submit():
        firstName = form.firstName.data
        lastName = form.lastName.data
        address = form.address.data
        reason = form.reason.data
            
        favorites = session.get("favorite", None)
        
        for pet_id in favorites:
            # Get the pet details including the name
            pet = db.execute("""
                SELECT * FROM pets 
                WHERE pet_id = ?;
            """, (pet_id,)).fetchone()

            # Get the name from the pet details
            name = pet["name"]
            
            db.execute("""
                INSERT INTO applications (user_id, pet_id,name,firstName,lastName,address,reason)
                VALUES(?,?,?,?,?,?,?);""",(g.user,pet_id,name,firstName,lastName,address,reason)) 
            db.commit()
            message = "Thanks for applying!"
        return render_template("apply.html", form=None, message=message)
    
    return render_template("apply.html", form=form, message=message)

@app.route("/application",methods=["GET", "POST"])
@login_required
def application():
    db = get_db()
    applications = db.execute("""SELECT * FROM applications
                      WHERE user_id = ?;""",(g.user,)).fetchall()
    if not applications:
        caption = "Empty!"
    else:
        caption = ""
        
    form = reviewForm()
    if form.validate_on_submit():
        review = form.review.data
        # retrieve the values from the url
        pet_id = request.args.get('pet_id')
        name = request.args.get('name')
        db = get_db()
        db.execute("""INSERT INTO reviews (user_id, pet_id,name,review)
                    VALUES(?,?,?,?);""",(g.user,pet_id,name,review)) 
        db.commit()
        return redirect(url_for("application"))  
    
    has_reviewed = {}
    for application in applications:
        pet_id = application["pet_id"]
        review_exists = db.execute("""
            SELECT * FROM reviews
            WHERE user_id = ? AND pet_id = ?
            ;
        """, (g.user, pet_id)).fetchone()
        if review_exists is not None:
            has_reviewed[pet_id] = True
        else:
            has_reviewed[pet_id] = False

    return render_template("application.html", caption=caption, applications=applications, form=form, has_reviewed=has_reviewed)

@app.route("/delete_application/<string:user_id>", methods=["GET", "POST"])
@login_required
def delete_application(user_id): # Deletes the application with the given ID for the logged-in user.
    
    db = get_db()

    # Check if the application belongs to the logged-in user before deleting
    application = db.execute("""
        SELECT * FROM applications
        WHERE user_id = ? ;
    """, (g.user,)).fetchone()

    if application is None:         
        return redirect(url_for("application"))

    db.execute("""
        DELETE FROM applications
        WHERE user_id = ? AND status !='Completed';
    """, (g.user,))
    db.commit()

    message = "Application deleted successfully!"
    return redirect(url_for("application", message=message))

@app.route("/volunteer", methods=["GET", "POST"])
@login_required
def volunteer():
    db = get_db()
    if g.role in ("volunteer", "admin"):
        return render_template("volunteer.html", form=None,
                               message="You already have volunteer access.")
    existing = db.execute(
        "SELECT status FROM volunteer_applications WHERE user_id = ? ORDER BY application_id DESC LIMIT 1",
        (g.user,)
    ).fetchone()
    if existing and existing["status"] == "Pending":
        return render_template("volunteer.html", form=None,
                               message="Your volunteer application is pending review.")
    form = volunteerForm()
    if form.validate_on_submit():
        db.execute(
            "INSERT INTO volunteer_applications (user_id, reason) VALUES (?, ?)",
            (g.user, form.reason.data.strip())
        )
        db.commit()
        return redirect(url_for("volunteer"))
    return render_template("volunteer.html", form=form, message=None)

@app.route("/admin/volunteers")
@role_required("admin")
def manage_volunteers():
    db = get_db()
    applications = db.execute("""
        SELECT application_id, user_id, reason, status, created_at
        FROM volunteer_applications ORDER BY application_id DESC
    """).fetchall()
    return render_template("manage_volunteers.html", applications=applications)

@app.route("/admin/volunteers/<int:application_id>/<decision>", methods=["POST"])
@role_required("admin")
def decide_volunteer(application_id, decision):
    if decision not in ("approve", "reject"):
        abort(404)
    db = get_db()
    application = db.execute(
        "SELECT * FROM volunteer_applications WHERE application_id = ?",
        (application_id,)
    ).fetchone()
    if application is None:
        abort(404)
    if application["status"] != "Pending":
        abort(409)
    with db:
        result = db.execute("""
            UPDATE volunteer_applications SET status = ?, reviewed_by = ?,
                reviewed_at = CURRENT_TIMESTAMP
            WHERE application_id = ? AND status = 'Pending'
        """, ("Approved" if decision == "approve" else "Rejected", g.user, application_id))
        if result.rowcount != 1:
            abort(409)
        if decision == "approve":
            db.execute("UPDATE users SET role = 'volunteer' WHERE user_id = ? AND role = 'user'",
                       (application["user_id"],))
    return redirect(url_for("manage_volunteers"))

@app.route('/manage_applications',methods=["GET", "POST"])
@role_required("volunteer", "admin")
def manage_applications():
    form = manageForm()
    
    if form.validate_on_submit():
        application_filter = form.application_filter.data  
        db = get_db()

        if application_filter == 'Submitted':
            applications = db.execute("""SELECT * FROM applications
                              WHERE status = 'Submitted';""").fetchall()
        elif application_filter == 'Processing':
            applications = db.execute("""SELECT * FROM applications
                              WHERE status = 'Processing';""").fetchall()
        else:
            applications = db.execute("""SELECT * FROM applications
                              WHERE status = 'Completed';""").fetchall()
    else:
        # Default to show all submitted applications
        db = get_db()
        applications = db.execute("""SELECT * FROM applications
                              WHERE status = 'Submitted';""").fetchall()
        
    return render_template("manage.html", applications=applications,form=form)    


@app.route('/accept_visit',methods=["GET", "POST"])
@role_required("volunteer", "admin")
def accept_visit():
    apl_id = request.args.get('apl_id') # get 'apl_id' from url
    db = get_db()
    db.execute("""UPDATE applications 
                        SET status = 'Processing' 
                        WHERE status = 'Submitted'AND apl_id = ?;""",(apl_id,))
    db.commit()
    return redirect(url_for("manage_applications"))

@app.route('/finish',methods=["GET", "POST"])
@role_required("volunteer", "admin")
def finish():
    apl_id = request.args.get('apl_id') 
    db = get_db()
    db.execute("""UPDATE applications 
                        SET status = 'Completed' 
                        WHERE status = 'Processing' AND apl_id = ?;""",(apl_id,))
    db.commit()
    return redirect(url_for("manage_applications"))
    
@app.route('/confirm_adoption', methods=["POST"])
@role_required("volunteer", "admin")
def confirm_adoption():
    pet_id = request.form.get('pet_id')
    apl_id = request.form.get('apl_id')

    db = get_db()

    # Check whether the application is valid
    application = db.execute("""
        SELECT * FROM applications
        WHERE apl_id = ?
        AND pet_id = ?
        AND status = 'Processing';
    """, (apl_id, pet_id)).fetchone()

    if application is None:
        return "Invalid application", 400

    # Update pet availability
    cursor = db.execute("""
        UPDATE pets
        SET availability = 'adopted'
        WHERE availability = 'available'
        AND pet_id = ?;
    """, (pet_id,))

    if cursor.rowcount == 0:
        db.rollback()
        return "Pet is no longer available", 409

    # Update application status
    db.execute("""
        UPDATE applications
        SET status = 'Completed'
        WHERE apl_id = ?;
    """, (apl_id,))

    db.commit()

    return redirect(url_for("manage_applications")) 
