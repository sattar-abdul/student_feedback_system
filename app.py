from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:@localhost/student_feedback_sys' # username= root, password= none
db = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
class Students(db.Model):
    # roll_no, name, dob
    roll_no = db.Column(db.String(4), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    dob = db.Column(db.Date, nullable=False)

class Professors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    dept = db.Column(db.String(200), nullable=False)
    qid1 = db.Column(db.Integer, default=0)
    qid2 = db.Column(db.Integer, default=0)
    qid3 = db.Column(db.Integer, default=0)
    qid4 = db.Column(db.Integer, default=0)
    qid5 = db.Column(db.Integer, default=0)
    responses = db.relationship('Response', back_populates='professor', lazy=True)


class Questions(db.Model):
    # qid, question
    qid = db.Column(db.String(200), primary_key=True)
    question = db.Column(db.String(200), nullable=False)


@app.route('/', methods=['GET', 'POST'])
def homepage():
    question = "Log in as:"
    options = ["Student", "Professor", "Admin"]
    return render_template('index.html', question=question, options=options)



# login as student or professor or admin
@app.route('/result', methods=['POST'])
def result_page():
    choice = request.form.get('choice', '')
    if choice == 'Student':
        return redirect(url_for('std_login'))
    elif choice == 'Professor':
        return redirect(url_for('pro_login'))
    elif choice == 'Admin':
        return redirect(url_for('admin_login'))
    else:
        return 'Invalid choice'

@app.route('/std_login')
def std_login():
    return render_template('std_login.html')

@app.route('/pro_login')
def pro_login():
    return render_template('pro_login.html')

@app.route('/admin_login')
def admin_login():
    return render_template('admin_login.html')

@app.route('/admin_login_auth', methods=['GET', 'POST'])
def admin_login_auth():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Perform authentication logic here
        if username == 'admin' and password == '123': # user id and password for Admin
                question = "Choose what to do:"
                options = ["Add Student Data", "Manage Students", "Add Professor Data", "Manage Professors", "Manage Feedbacks", "Log Out"]
                return render_template('admin_homepage.html', question=question, options=options)
        else:
            return 'Invalid credentials. Go back to login'

    return render_template('admin_login.html')

@app.route('/result1', methods=['POST'])
def result1():
    choice = request.form.get('choice', '')
    if choice == 'Add Student Data':
        return redirect(url_for('add_student_data'))
    elif choice == 'Manage Students':
        return redirect(url_for('delete_student_data'))
    elif choice == 'Add Professor Data':
        return redirect(url_for('add_professor_data'))
    elif choice == 'Manage Professors':
        return redirect(url_for('delete_professor_data'))
    elif choice == 'Manage Feedbacks':
        return redirect(url_for('manage_feedbacks'))
    elif choice == 'Log Out':
        flash('You have been logged out.', 'info')
        return redirect(url_for('admin_login'))
    else:
        return 'Invalid choice'

@app.route('/add_student_data')
def add_student_data():
    return render_template('add_student_data.html')
@app.route('/delete_student_data')
def delete_student_data():
    students = Students.query.all()
    return render_template('delete_student_data.html', students=students)
@app.route('/add_professor_data')
def add_professor_data():
    return render_template('add_professor_data.html')
@app.route('/delete_professor_data')
def delete_professor_data():
    professors = Professors.query.all()
    return render_template('delete_professor_data.html', professors=professors)
@app.route('/manage_feedbacks')
def manage_feedbacks():
    questions = Questions.query.all()
    return render_template('manage_feedbacks.html', questions=questions)

@app.route('/result2', methods=['POST'])
def result2():
    if request.method == 'POST':
        roll_no = request.form['roll no']
        name = request.form['name']
        dob_str = request.form['dob']
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()

        # Create a new Student instance
        new_student = Students(roll_no=roll_no, name=name, dob=dob)

        # Add the new student to the database
        db.session.add(new_student)
        db.session.commit()

        return render_template('popupmessage.html', popmessage=f"Student name: {name} with Roll No:{roll_no} added Successfully", bodymessage="To add more students:")

@app.route('/result3', methods=['POST'])
def result3():
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        dept = request.form['dept']

        # Create a new Professor instance
        new_professor = Professors(id=id, name=name, dept=dept)

        # Add the new professor to the database
        db.session.add(new_professor)
        db.session.commit()

        return render_template('popupmessage.html', popmessage=f"Professor name: {name} with ID:{id} added Successfully", bodymessage="To add more Professor:")

# dislpay student details
@app.route('/')
def display_students():
    students = Students.query.all()
    return render_template('display_students.html', students=students)

# deleting student
@app.route('/delete_student/<string:roll_no>', methods=['POST'])
def delete_student(roll_no):
    student = Students.query.get_or_404(roll_no)
    db.session.delete(student)
    db.session.commit()
    return redirect('/delete_student_data')

# Display Professor details //fix
@app.route('/')
def display_professors():
    professors = Professors.query.all()
    return render_template('delete_professor_data.html', professors=professors)

# Deleting professor //fix
@app.route('/delete_professor/<int:id>', methods=['POST'])
def delete_professor(id):
    professor = Professors.query.get_or_404(id)
    db.session.delete(professor)
    db.session.commit()
    return redirect('/delete_professor_data')

# student login
@app.route('/std_login1', methods=['GET', 'POST'])
def std_login1():
    if request.method == 'POST':
        name = request.form['username']
        roll_no = request.form['password']

        # Query the database for the student with the given name
        student = Students.query.filter_by(name=name).first()

        # Check if the student exists and the roll_no matches
        if student and student.roll_no == roll_no:
            session['user_id'] = student.roll_no
            return redirect(url_for('std_homepage', student_name=student.name))
        else:
            flash('Invalid credentials. Please try again.', 'error')

    return render_template('std_login.html')

# Welcome page after successful login (student)
@app.route('/std_homepage/<string:student_name>', methods=['GET', 'POST'])
def std_homepage(student_name):
    question = "Choose what to do:"
    options = ["Give Feedback", "Log Out"]
    return render_template('std_homepage.html', student_name=student_name, question=question, options=options)

#options on student page
@app.route('/result4', methods=['POST'])
def result4():
    choice = request.form.get('choice', '')
    student_name = request.args.get('student_name')
    if choice == 'Log Out':
        return redirect(url_for('std_logout'))
    if choice == 'Give Feedback':
        return redirect(url_for('feedback_form'))
    else:
        return 'Invalid choice'

@app.route('/std_logout')
def std_logout():
    session.pop('user_id', None)  #Clear the user ID from the session
    flash('You have been logged out.', 'info')
    return render_template('std_login.html')



#pro login
@app.route('/pro_login1', methods=['GET', 'POST'])
def pro_login1():
    if request.method == 'POST':
        name = request.form['username']
        id = request.form['password']
        # Query the database for the professor with the given name
        professor = Professors.query.filter_by(name=name).first()

        # Check if the student exists and the roll_no matches
        if professor and (professor.id) == int(id):
            session['user_id'] = professor.id
            return redirect(url_for('pro_homepage', professor_name=professor.name))
        else:
            flash('Invalid credentials. Please try again.', 'error')

    return render_template('pro_login.html')

# Welcome page after successful login (professor)
@app.route('/pro_homepage/<string:professor_name>', methods=['GET', 'POST'])
def pro_homepage(professor_name):
    question = "Choose what to do:"
    options = ["Show Rating","Log Out"]
    return render_template('pro_homepage.html', professor_name=professor_name, question=question, options=options)

#options on professor page
@app.route('/result5', methods=['POST'])
def result5():
    choice = request.form.get('choice', '')
    if choice == 'Log Out':
        return redirect(url_for('pro_logout'))
    if choice == 'Show Rating':
        # Get the professor_id from the session
        professor_id = session.get('user_id')
        if professor_id:
            return redirect(url_for('show_ratings', professor_id=professor_id))
        else:
            flash('Error: Professor ID not found.', 'error')
            return redirect(url_for('pro_homepage'))
    else:
        return 'Invalid choice'

@app.route('/pro_logout')
def pro_logout():
    session.pop('user_id', None)  #Clear the user ID from the session
    flash('You have been logged out.', 'info')
    return render_template('pro_login.html')

@app.route('/edit_question/<string:qid>', methods=['GET', 'POST'])
def edit_question(qid):
    question = Questions.query.get_or_404(qid)

    if request.method == 'POST':
        new_question_text = request.form['new_question']
        question.question = new_question_text
        db.session.commit()
        return redirect(url_for('manage_feedbacks'))

    return render_template('edit_question.html', question=question)

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, server_default="0")
    professor_id = db.Column(db.Integer, db.ForeignKey('professors.id'), nullable=False)
    qid1 = db.Column(db.Integer, nullable=False)
    qid2 = db.Column(db.Integer, nullable=False)
    qid3 = db.Column(db.Integer, nullable=False)
    qid4 = db.Column(db.Integer, nullable=False)
    qid5 = db.Column(db.Integer, nullable=False)
    professor = db.relationship('Professors', back_populates='responses')







@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if request.method == 'POST':
        professor_id = request.form.get('professor_id')
        qid1 = request.form.get('qid1')
        qid2 = request.form.get('qid2')
        qid3 = request.form.get('qid3')
        qid4 = request.form.get('qid4')
        qid5 = request.form.get('qid5')

        # Create a new response instance
        new_response = Response(
            professor_id=professor_id,
            qid1=qid1,
            qid2=qid2,
            qid3=qid3,
            qid4=qid4,
            qid5=qid5
        )

        # Add the new response to the database
        db.session.add(new_response)
        db.session.commit()

        flash('Feedback submitted successfully, You have been logged out', 'success')
        return redirect(url_for('std_login'))
    else:
        flash('Failed to submit feedback. Please try again.', 'error')
        return redirect(url_for('std_login'))


@app.route('/feedback_form')
def feedback_form():
    professors = Professors.query.all()
    questions = Questions.query.all()
    return render_template('feedback_form.html', professors=professors, questions=questions)


@app.route('/show_ratings/<int:professor_id>')
def show_ratings(professor_id):
    # Query the professor by the given professor_id
    professor = Professors.query.get_or_404(professor_id)

    # Access the responses through the professor's responses attribute
    responses = professor.responses

    # Calculate the average rating for each question
    question_ratings = {}
    for response in responses:
        question_ratings.setdefault('qid1', []).append(response.qid1)
        question_ratings.setdefault('qid2', []).append(response.qid2)
        question_ratings.setdefault('qid3', []).append(response.qid3)
        question_ratings.setdefault('qid4', []).append(response.qid4)
        question_ratings.setdefault('qid5', []).append(response.qid5)

    average_ratings = {}
    for question, ratings in question_ratings.items():
        average_ratings[question] = sum(ratings) / len(ratings) if ratings else 0

    return render_template('show_ratings.html', professor_id=professor_id, average_ratings=average_ratings)




# this runs the app
if __name__ == '__main__':
    app.run(debug=True)


#end of app.py