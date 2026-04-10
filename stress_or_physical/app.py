
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Assessment
from bayesian import run_bayesian
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stress_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    return render_template('index.html', username=current_user.email)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        return render_template('login.html', error='Invalid email or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            return render_template('login.html', error='Email already registered')
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/assessment')
@login_required
def assessment():
    return render_template('assessment.html')

@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.form
    result = run_bayesian(data)
    new_assessment = Assessment(
        user_id=current_user.id,
        date=datetime.now(),
        result_json=json.dumps(result),
        annotations='{}'
    )
    db.session.add(new_assessment)
    db.session.commit()
    return render_template('results.html', result=result, assessment_id=new_assessment.id)

@app.route('/history')
@login_required
def history():
    assessments = Assessment.query.filter_by(
        user_id=current_user.id
    ).order_by(Assessment.date.desc()).all()
    return render_template('history.html', assessments=assessments)

@app.route('/history/<int:assessment_id>')
@login_required
def view_assessment(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    if assessment.user_id != current_user.id:
        return redirect(url_for('history'))
    result = json.loads(assessment.result_json)
    annotations = assessment.annotations_dict
    return render_template('results.html', result=result, readonly=True,
                           assessment_id=assessment_id, annotations=annotations)

@app.route('/annotate/<int:assessment_id>', methods=['POST'])
@login_required
def annotate(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    if assessment.user_id != current_user.id:
        return jsonify({'error': 'unauthorized'}), 403
    data = request.get_json()
    assessment.annotations = json.dumps(data)
    db.session.commit()
    return jsonify({'status': 'ok'})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)
