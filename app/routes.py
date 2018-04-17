from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from werkzeug.datastructures import FileStorage
from app.forms import LoginForm, RegistrationForm
from app.models import User, File, Job
import pandas as pd
import datetime
import os
import json
import pickle

@app.route("/", methods=['GET'])
def frontPage():

    return render_template('frontPage.html')

@app.route("/about", methods=['GET'])
def about():

    return render_template('about.html')

@app.route("/aboutClaire", methods=['GET'])
def aboutClaire():

    return render_template('aboutClaire.html')


@app.route("/userHomepage", methods=['GET', 'POST'])
@login_required
def userHomepage():

    user = current_user.username

    print(user)
    q1 = User.query.filter_by(username = user).first()
    print(q1)
    if q1 is not None:
        q2 = File.query.filter_by(file_user_id = q1.id).all()
        print(q2)
        if q2 is not None:
            q3 = []
            i = 0;
            for qq22 in q2:
                qq33 = []
                qq33.append(qq22)
                qq33.append(Job.query.filter_by(job_file_id = qq22.file_user_hash).all())

                # qq33 = [q2,Job.query.filter_by(job_file_id = qq22.file_user_hash).all()]
                # # qq33.append(q2)
                # # qq33.append(Job.query.filter_by(job_file_id = qq22.file_user_hash).all())
                # # a = [q2, Job.query.filter_by(job_file_id = qq22.file_user_hash).all()]
                #
                # a = {'s%i' %(i):[q2, Job.query.filter_by(job_file_id = qq22.file_user_hash).all()]}
                # i = i + 1
                q3.append(qq33)

            # table = q3
            # print(table)
# print(q2)
# qq = []
# for row in q:
#     qq.append(Job.query.filter_by(job_file_id = row.file_hash))

# table = q2
# table = "<table style='border:1px solid red'>"
# for row in q2:
#     table = table + "<tr>"
#
# table = table + "</tr>"

# print(table)


    if request.method == 'POST':
        try:
            name = request.form['job_file_id']
            return redirect(url_for('results', name=request.form['job_file_id']))
        except KeyError:
            return redirect(url_for('doimport'))

        # searchword = request.args.get('job_file_id', '')
        # print("a" + searchword + "a")
        # if searchword == "":
        #     return redirect(url_for('doimport'))
        # else:
        #     return redirect(url_for('results', name=request.form['job_file_id']))

    return render_template('userHomepage.html', q2=q2, q3=q3, user=user)




# @app.route('/')
@app.route("/doimport", methods=['GET', 'POST'])
@login_required
def doimport():

    user = current_user.username

    if request.method == 'POST':


        excel = request.files['file']
        excel.save(os.path.join(app.config['UPLOAD_FOLDER'], excel.filename))

        # randString = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        # line = randString + timeFormat
        # m = sha1(line.encode('utf-8')).hexdigest()
        # filepath = "/Users/claire_mit/Documents/Steele_Lab/SynergyWebApp/" + m
        print("fails before entry")
        f = File(file_user_id=current_user.id, file_size="1")
        print(f.file_hash)
        print("fails before setting hash")
        # print(excel)
        #file.read() is the same as file.stream.read()
        # img_key = hashlib.md5(file.read()).hexdigest()
        # loadedfile = pd.read_excel(excel)
        # fff = open(excel)
        # print(loadedfile)
        yes = f.set_file_hash(os.path.join(app.config['UPLOAD_FOLDER'], excel.filename))
        no = f.set_file_user_hash(os.path.join(app.config['UPLOAD_FOLDER'], excel.filename))
        print(yes)
        print("fails after setting hash")
        # Need to implement here the already been uploaded
        # Also where different users upload the same file


        f.set_file_path("/app/csvfiles/%s" % (excel.filename))
        print("fails after setting file path")
        # saved_file = open("/Users/claire_mit/Documents/Steele_Lab/SynergyWebApp/app/%s" % (yes), 'w' )
        # saved_file.write(loadedfile)
        # saved_file.close()
        try:
            db.session.add(f)
            db.session.commit()

        except:
            pass

        print("fails after commiting")
        return redirect(url_for('parameterSelection',name=f.file_user_hash))
        # return render_template('parameterSelection.html')

    return render_template('fileUpload.html')

@app.route("/parameterSelection/<string:name>", methods=['GET', 'POST'])
@login_required
def parameterSelection(name):
    #query the current file
    #extract from the query string(?) or url parameter
    user = current_user.username

    #### check if the id of the user matches the job  so that people cannot enter: http://localhost:5000/status/bdf0d5437d68f23ff11dd0e5623c0827 if that is not their job

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

    user = current_user.username
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

    user = current_user.username

    with open('pklfiles/%s.pkl' %(name), 'rb') as f:  # Python 3: open(..., 'rb')
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
        user = current_user.name
        print(user)
        return redirect(url_for('userHomepage'))
    form = LoginForm()
    if form.validate_on_submit():
        username=form.username.data
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':

            next_page = url_for('userHomepage')
            print(username)
        return redirect(url_for('userHomepage'))
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
