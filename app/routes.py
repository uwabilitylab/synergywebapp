from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User, File, Job
import pandas as pd
import datetime
import os
import json
import pickle

@app.route('/')
@app.route("/doimport", methods=['GET', 'POST'])
@login_required
def doimport():

    if request.method == 'POST':
        excel = request.files['file']
        excel.save(os.path.join(app.config['UPLOAD_FOLDER'], excel.filename))

        # randString = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        # line = randString + timeFormat
        # m = sha1(line.encode('utf-8')).hexdigest()
        # filepath = "/Users/claire_mit/Documents/Steele_Lab/SynergyWebApp/" + m

        f = File(file_user_id=current_user.id, file_size="1")
        # print(excel)
        #file.read() is the same as file.stream.read()
        # img_key = hashlib.md5(file.read()).hexdigest()
        # loadedfile = pd.read_excel(excel)
        # fff = open(excel)
        # print(loadedfile)
        yes = f.set_file_hash(excel)

        # Need to implement here the already been uploaded
        # Also where different users upload the same file


        f.set_file_path("/app/csvfiles/%s" % (excel.filename))
        # saved_file = open("/Users/claire_mit/Documents/Steele_Lab/SynergyWebApp/app/%s" % (yes), 'w' )
        # saved_file.write(loadedfile)
        # saved_file.close()
        db.session.add(f)
        db.session.commit()
        return redirect(url_for('parameterSelection',name=f.file_hash))
        # return render_template('parameterSelection.html')

    return render_template('fileUpload.html')

@app.route("/parameterSelection/<string:name>", methods=['GET', 'POST'])
@login_required
def parameterSelection(name):
    #query the current file
    #extract from the query string(?) or url parameter
    if request.method == 'POST':
        low = request.form['low']
        high = request.form['high']
        numSyn = request.form['syn']
        address = request.remote_addr
        timeDigest= datetime.datetime.now(tz=None)
        timeFormat = timeDigest.strftime("%Y-%m-%d %H:%M:%S.%f")
        j = Job(job_file_id=name, lowpass_cutoff=low, highpass_cutoff=high, synergy_number=numSyn, status='submitted', processed_file_path="/Users/claire_mit/Documents/Steele_Lab/SynergyWebApp/", ip_address=address, time_submitted=timeDigest)
        print(str(j.id)+name)
        jh = j.set_job_hash(str(j.id)+name)
        db.session.add(j)
        db.session.commit()

        return redirect(url_for('status', name=name))

    return render_template('parameterSelection.html')

@app.route("/status/<string:name>",methods=['GET', 'POST'])
@login_required
def status(name):

    #Get the info from the jobs page about the status of the page
    # q = db.session.query(User, Address)
    q = Job.query.filter_by(job_file_id = name).first()
    fileStatus = q.status

    if request.method == 'POST' and fileStatus == 'processed':

        return redirect(url_for('results', name=name))

    elif request.method == 'POST':

        return render_template('status.html',fileStatus=fileStatus)

    # q.status

    return render_template('status.html',fileStatus=fileStatus)

@app.route("/results/<string:name>", methods=['GET'], endpoint='results')
@login_required
def result(name):

    # q = Job.query.filter_by(job_file_id = name).first()
    # jid = q.

    with open('%s.pkl' %(name), 'rb') as f:  # Python 3: open(..., 'rb')
        resultsJson, WWJson, labels, tVAFJson, tVAFlabels, MNJson, muscleNamesShort = pickle.load(f)

    # return render_template('fileupload.html')
    return render_template('basic9.html', resultsJson = resultsJson,
            WWJson = WWJson, labels = labels, tVAFJson = tVAFJson,
            tVAFlabels = tVAFlabels, MNJson = MNJson, muscleNamesShort = muscleNamesShort)

# @app.route("/uploading", methods=['GET', 'POST'])
# def douploading():
#     # ajax request


#ajax logins??
#most likely return json instead of a template
#Create a fake user that is loaded up every time for now to be able to simulate
#using a session. Assign every file and job to the one fake user and nothing else.
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('doimport'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('login')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('doimport'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        # c.execute('INSERT INTO users (username, email, password_hash) VALUES (form.username.data, form.email.data, generate_password_hash(form.password.data))')
        # con.commit
        # con.close()
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
