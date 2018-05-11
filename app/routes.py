from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from decorators import check_confirmed, admin_required
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
import string
import random

@app.route("/", methods=['GET'])
def frontPage():

    return render_template('frontPage.html')

@app.route("/about", methods=['GET'])
def about():

    return render_template('about.html')

@app.route("/aboutClaire", methods=['GET'])
def aboutClaire():

    return render_template('aboutClaire.html')


@app.route("/admin", methods=['GET', 'POST'])
@login_required
@admin_required
def admin():

    users = User.query.all()

    if request.method == 'POST':
        return redirect(url_for('admin_con', status = request.form["user_conf"]))

    return render_template('admin.html', users = users)

@app.route("/admin/confirmation/<string:status>", methods=['GET','POST'])
@login_required
@admin_required
def admin_con(status):

    if request.method == 'POST':
        return redirect(url_for('admin'))

    change_status = User.query.filter_by(username=status).first()
    print(change_status.confirmed)
    if change_status.confirmed == False:
        # update(User).where(User.username == status).values(confirmed=True)
        change_status.confirmed = True
        timeDigest= datetime.datetime.now(tz=None)
        timeFormat = timeDigest.strftime("%Y-%m-%d %H:%M:%S.%f")
        change_status.confirmed_on = timeDigest
        db.session.commit()
    else:
        # update(User).where(User.username == status).values(confirmed=False)
        change_status.confirmed = False
        db.session.commit()

    return render_template('adminConfirmation.html', status=status)

@app.route("/userHomepage", methods=['GET', 'POST'])
@login_required
@check_confirmed
def userHomepage():

    user = current_user.username
    q1 = User.query.filter_by(username = user).first()
    if q1 is not None:

        q2 = File.query.filter_by(file_user_id = q1.id).all()

        if q2 is not None:

            q3 = []
            i = 0;
            for qq22 in q2:

                qq33 = []
                qq33.append(qq22)
                qq33.append(Job.query.filter_by(job_file_id = qq22.file_user_hash).all())
                q3.append(qq33)

    if request.method == 'POST':
        try:
            name = request.form['job_hash']
            return redirect(url_for('results', name=request.form['job_hash']))
        except KeyError:
            return redirect(url_for('doimport'))

    return render_template('userHomepage.html', q2=q2, q3=q3, user=user)

@app.route("/doimport", methods=['GET', 'POST'])
@login_required
@check_confirmed
def doimport():

    user = current_user.username

    if request.method == 'POST':


        excel = request.files['file']
        excel.save(os.path.join(app.config['UPLOAD_FOLDER'], excel.filename))
        size = os.stat(os.path.join(app.config['UPLOAD_FOLDER'], excel.filename)).st_size
        f = File(file_user_id=current_user.id, file_size=str(size/1000) + "KB")
        yes = f.set_file_hash(os.path.join(app.config['UPLOAD_FOLDER'], excel.filename))
        no = f.set_file_user_hash(os.path.join(app.config['UPLOAD_FOLDER'], excel.filename))
        f.set_file_path("/app/csvfiles/%s" % (excel.filename))

        try:
            db.session.add(f)
            db.session.commit()

        except:
            pass

        return redirect(url_for('parameterSelection',name=f.file_user_hash))

    return render_template('fileUpload.html')


@app.route("/parameterSelection/<string:name>", methods=['GET', 'POST'])
@login_required
@check_confirmed
def parameterSelection(name):
    user = current_user.username

    if request.method == 'POST':
        low = request.form['low']
        high = request.form['high']
        numSyn = request.form['syn']
        address = request.remote_addr
        timeDigest= datetime.datetime.now(tz=None)
        timeFormat = timeDigest.strftime("%Y-%m-%d %H:%M:%S.%f")
        j = Job(job_file_id=name, lowpass_cutoff=low, highpass_cutoff=high, synergy_number=numSyn, status='submitted', processed_file_path=app.config['UPLOAD_FOLDER'], ip_address=address, time_submitted=timeDigest)
        jh = j.set_job_hash(''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(50))
)
        db.session.add(j)
        db.session.commit()

        return redirect(url_for('status', name=j.job_hash))

    return render_template('parameterSelection.html')

@app.route("/status/<string:name>",methods=['GET', 'POST'])
@login_required
@check_confirmed
def status(name):

    user = current_user.username
    q = Job.query.filter_by(job_hash = name).first()
    fileStatus = q.status

    if request.method == 'POST' and fileStatus == 'processed':

        return redirect(url_for('results', name=name))

    elif request.method == 'POST':

        return render_template('status.html',fileStatus=fileStatus)

    return render_template('status.html',fileStatus=fileStatus)

@app.route("/results/<string:name>", methods=['GET'], endpoint='results')
@login_required
@check_confirmed
def result(name):

    user = current_user.username
    #
    # with open('pklfiles/%s.pkl' %(name), 'rb') as f:  # Python 3: open(..., 'rb')
    #     resultsJson, WWJson, labels, tVAFJson, tVAFlabels, MNJson, muscleNamesShort = pickle.load(f)


    with open('pklfiles/%s.pkl' %(name), 'rb') as f:  # Python 3: open(..., 'rb')
        [tVAF, vaf] = pickle.load(f)

    tVAF = [round(elem, 2) for elem in tVAF]

    # vaf = [round(elem, 2) for elem in vaf]

    print(tVAF)
    print(vaf)

    fn = open(os.path.join(app.config['PLOT_FOLDER'] + '/EMG_Plots_%s' %(name), 'filenames.txt'),'r')
    an = open(os.path.join(app.config['PLOT_FOLDER'] + '/Act_Plots_%s' %(name), 'filenames.txt'),'r')
    wn = open(os.path.join(app.config['PLOT_FOLDER'] + '/Wei_Plots_%s' %(name), 'filenames.txt'),'r')
    tn = open(os.path.join(app.config['PLOT_FOLDER'] + '/tVAF_Plots_%s' %(name), 'filenames.txt'),'r')

    ann = []
    for line in an:
        ann.append(line)

    wnn = []
    for line in wn:
        wnn.append(line)

    # ann = an.read()
    # wnn = wn.read()
    awn = []
    j = 1
    for i in range(len(ann)):
        awn_one = [ann[i], wnn[i]]
        awn.append(awn_one)

    j = 1
    l = 0
    awnwn = []
    for k in range(5):
        awnone = []
        for i in range(j):
            awnone.append(awn[l])
            l = l + 1
        awnwn.append(awnone)
        j = j + 1

    tnn = []
    for line in tn:
        tnn.append(line)


    return render_template('basic9.html', name = name, fn = fn, awnwn = awnwn, tnn=tnn, tVAF = tVAF, vaf = vaf)

# @app.route("/uploading", methods=['GET', 'POST'])
# def douploading():
#     # ajax request

@app.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('userHomepage'))
    flash('Waiting for confirmation by system administrators', 'warning')
    return render_template('unconfirmed.html', new_user = current_user.username)

#ajax logins??
#most likely return json instead of a template
#Create a fake user that is loaded up every time for now to be able to simulate
#using a session. Assign every file and job to the one fake user and nothing else.
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.confirmed:

        user = current_user.name
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

        return redirect(url_for('userHomepage'))

    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated and current_user.confirmed:

        return redirect(url_for('doimport'))

    form = RegistrationForm()
    if form.validate_on_submit():

        user = User(username=form.username.data, email=form.email.data, institution=form.institution.data, confirmed=False)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('unconfirmed'))

    return render_template('register.html', title='Register', form=form)
