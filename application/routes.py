from os import removedirs
from application import app, db, api
from flask import render_template, request, Response, json, jsonify, redirect, flash, url_for, session
from application.models import User, Course, Enrollment
from application.forms import LoginForm, RegisterForm
from flask_restx import Resource

apiData = None

##################################
@api.route('/api', '/api/')
class GetAndPost(Resource):
    def get(self):
        return jsonify(User.objects.all())

@api.route('/api/<idx>')
class GetUpdateDelete(Resource):
    def get(self, idx):
        return jsonify(User.objects(user_id = idx))

##################################

@app.route("/")
@app.route("/index")
@app.route("/home")
def home():
    # username = session.get('name')
    return render_template('index.html', index=True)

@app.route("/login", methods = ["GET", "POST"])
def login():
    if session.get('user_id'):
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        email    = form.email.data
        password = form.password.data
        user = User.objects(email=email).first()
        if user and user.check_password(password):
            flash(f'{user.first_name}, You are logged in', 'success')
            session['user_id'] = user.user_id
            session['name'] = user.first_name
            return redirect(url_for('home'))
        else:
            flash('Password or Email is incorrect', 'danger')
    return render_template('login.html', form = form, login=True)


@app.route("/courses/")
@app.route("/courses/<term>")
def courses(term = "2019"):
    courseData = Course.objects.order_by('-courseID')
    return render_template('courses.html', courseData=courseData, courses="true",  term = term)


@app.route("/register", methods = ["GET", "POST"])
def register():
    if session.get('user_id'):
        return redirect(url_for('home'))

    form = RegisterForm()
    if form.validate_on_submit():
        user_id = User.objects.count() 
        user_id += 1
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        password = form.password.data

        user = User(user_id = user_id, email = email, first_name = first_name, last_name = last_name)
        user.set_password(password)
        user.save()
        flash('you are registered', 'success')
        return redirect('/index')
    return render_template('register.html', form = form, register="true")

@app.route("/enrollment", methods=["GET", "POST"])
def enrollment():
    if session.get('user_id'):
        user_id = session.get('user_id')
    else:
        flash(f'You need to be logged in to enroll', 'warn')
        return redirect ('/login')

    courseID = request.form.get('courseID')
    courseTitle = request.form.get('title')
    # user_id = 1
    if courseID:
        if Enrollment.objects(user_id = user_id, courseID = courseID):
            flash(f'You are already enrolled in {courseTitle}', 'danger')
            return redirect('courses')
        else:
            enroll = Enrollment(user_id = user_id, courseID = courseID)
            enroll.save()
            flash(f'You are enrolled in {courseTitle}', 'success')

    classes = list(User.objects.aggregate(*[
            {
                '$lookup': {
                    'from': 'enrollment', 
                    'localField': 'user_id', 
                    'foreignField': 'user_id', 
                    'as': 'r1'
                }
            }, {
                '$unwind': {
                    'path': '$r1', 
                    'includeArrayIndex': 'r1_id', 
                    'preserveNullAndEmptyArrays': False
                }
            }, {
                '$lookup': {
                    'from': 'course', 
                    'localField': 'r1.courseID', 
                    'foreignField': 'courseID', 
                    'as': 'r2'
                }
            }, {
                '$unwind': {
                    'path': '$r2', 
                    'preserveNullAndEmptyArrays': False
                }
            }, {
                '$match': {
                    'user_id': user_id
                }
            }, {
                '$sort': {
                    'courseID': 1
                }
            }
        ]))
    return render_template('enrollment.html', classes = classes, enrollment = True)

# @app.route("/api/")
# @app.route("/api/<idx>")
# def api(idx = None):
#     if (idx == None):
#         jdata = apiData
#     else:
#         jdata = apiData[int(idx)]
#     return Response(json.dumps(jdata), mimetype = "application/json" )

@app.route("/user")
def user():
    # User(user_id = 1, first_name = "joe", last_name = "schmoe", email = "joe@example.com", password = "password123").save()
    # User(user_id = 2, first_name = "mary", last_name = "hoese", email = "mary@example.com", password = "password123").save()
    users = User.objects.all()
    return render_template("users.html", users = users)

@app.route('/logout')
def logout():
    if session.get('user_id'):
        session.pop('user_id', None)
        session.pop('name', None)
    return redirect('/login')