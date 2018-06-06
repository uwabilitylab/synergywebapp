from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from decorators import check_confirmed, admin_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from app import app, db
from werkzeug.datastructures import FileStorage
from app.forms import LoginForm, RegistrationForm
from app.models import User, File, Job
import pandas as pd
from math import floor
import datetime
import os
import json
import pickle
import string
import random
import re
import urllib
import csv


#define muscles here
otherarray = ["", "Other"];
othertext =["Don't Include", "Other"];
lowarray = ["Add_Mag", "Gas_Med", "Glu_Max", "Glu_Med", "Lat_Ham", "Med_Ham", "Pre_Bre", "Rec_Fem", "Soleus", "Ten_Fas_Lat", "Tib_Ant", "Vas_Med", "Vas_Lat"];
lowtext = ["Adductor Magnus",  "Gastrocnemius Medialis", "Gluteus Maximus", "Gluteus Medius", "Lateral Hamstring", "Medial Hamstring", "Peroneus Brevis", "Rectus Femoris", "Soleus", "Tensor Fasciae Latae", "Tibialis Anterior", "Vastus Medialis", "Vastus Lateralis"];
trunkarray = ["Ere_Spi", "Ext_Obl", "Lat_Dor", "Rec_Abd", "Spleni", "Trap_Inf", "Tra_Sup"];
trunktext = ["Erector Spinae", "External Obliques", "Latissimus Dorsi", "Rectus Abdmoninus", "Splenius", "Trapizius Inferior", "Trapizius Superior"];
higharray =["Ant_Del", "Bic_Bra", "Pos_Del", "Tri_Bra"];
hightext= ["Anterior Deltoid", "Biceps Brachii", "Posterior Deltoid", "Triceps Brachii"];

all_muscles = lowarray + trunkarray + higharray

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


        muscle_id_re = r"muscle\[(\d+)\]";
        parameterSelection = {'status':0}
        parameterSelection['message'] = ''

        try:
            excel = request.files['file']

            #input validation
            muscles = request.form.to_dict();
            includedMuscles = []
            matchedName = []
            for muscle_name,value in muscles.items():
                if value != "":
                    # extract the column index from the muscle field name
                    muscle_matches = re.match(muscle_id_re, muscle_name);
                    if muscle_matches is not None:
                        matchedName.append(value)
                        includedMuscles.append(int(muscle_matches[1]))

            # include = request.values.get
            print("muscles: " + str(includedMuscles))
            #includedMuscles validity is checked in daemon.py

            #check the file extension is allowed
            escaped_filename = secure_filename(excel.filename)
            if not (escaped_filename.endswith(".csv") or escaped_filename.endswith(".tsv")):
                raise ValueError("Please upload only csv and tsv files")

            #check that the file is actually csv or tsv
            print(excel.read(1024))
            dialect = csv.Sniffer().sniff(str(excel.read(65536),'utf-8')) #need to read in enough bytes to include a couple of lines
            print(str(dialect))
            # double-check the sniffed delimiter is allowed
            allowed_delimiters = [',', '\t']

            if dialect.delimiter not in allowed_delimiters:
                print(str(dialect.deliminiter))
                raise TypeError("Invalid file: must be comma or tab-delimited text!")


            excel.save(os.path.join(app.config['UPLOAD_FOLDER'], escaped_filename))
            size = os.stat(os.path.join(app.config['UPLOAD_FOLDER'], escaped_filename)).st_size
            f = File(file_user_id=current_user.id, file_size=str(size/1000) + "KB")
            yes = f.set_file_hash(os.path.join(app.config['UPLOAD_FOLDER'], escaped_filename))
            no = f.set_file_user_hash(os.path.join(app.config['UPLOAD_FOLDER'], escaped_filename))
            f.set_file_path("/app/csvfiles/%s" % (escaped_filename))
            parameterSelection['name'] = f.file_user_hash
            parameterSelection['muscles'] = includedMuscles
            parameterSelection['mnames'] = matchedName
            # pS = json.dumps(parameterSelection)
            print("FILE SIZE: " + str(size))


            db.session.add(f)
            db.session.commit()
            parameterSelection['status'] = 1;
        except ValueError as e:
            parameterSelection['status'] = 2;
            parameterSelection['message'] = str(e)
        except (UnicodeDecodeError, TypeError) as e:
            parameterSelection['status'] = 2;
            parameterSelection['message'] = "Invalid file: must be comma or tab-delimited text!"
        except Exception as e:
            print(str(e))
            parameterSelection['message'] = "An unknown error occurred, please contact support"
            parameterSelection['status'] = 3;
            ###### Must fix this laterrrrr


        # return redirect(url_for('parameterSelection',name=f.file_user_hash,muscles=includedMuscles,mnames=matchedName))
        return jsonify(parameterSelection)

    return render_template('fileUpload.html', array=otherarray, text=othertext,lowarray=lowarray, lowtext=lowtext,trunkarray=trunkarray,trunktext=trunktext,higharray=higharray,hightext=hightext)


@app.route("/parameterSelection/<string:name>/<string:muscles>/<string:mnames>", methods=['GET', 'POST'])
@login_required
@check_confirmed
def parameterSelection(name, muscles, mnames):
    user = current_user.username

    if request.method == 'POST':
        low = int(request.form['low'])
        high = int(request.form['high'])
        numSyn = int(request.form['syn'])
        address = request.remote_addr

        matchedNames = json.loads(urllib.parse.unquote(mnames))
        musclesIncluded = json.loads(urllib.parse.unquote(muscles))
        print(matchedNames)
        print(musclesIncluded)

        all_muscles_set = set(all_muscles)
        matchedNames_set = set(matchedNames)

        if (not matchedNames_set.issubset(all_muscles_set)):
            return(render_template('busted.html'))

        timeDigest= datetime.datetime.now(tz=None)
        timeFormat = timeDigest.strftime("%Y-%m-%d %H:%M:%S.%f")
        j = Job(job_file_id=name, included_muscles=json.dumps(musclesIncluded), matched_names=json.dumps(matchedNames), lowpass_cutoff=low, highpass_cutoff=high, synergy_number=numSyn, status='submitted', processed_file_path=app.config['UPLOAD_FOLDER'], ip_address=address, time_submitted=timeDigest)
        jh = j.set_job_hash(''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(50)))
        # musnames = open(os.path.join(app.config['BASE_FOLDER'] + '/app/static/', '%s.txt' %(jh)), 'w+')
        # musnames.write('%s' %(muscles))
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

    if request.method == 'POST':

        return redirect(url_for('results', name=name))

    # if request.method == 'POST' and fileStatus == 'processed':
    #
    #     return redirect(url_for('results', name=name))
    #
    # elif request.method == 'POST':
    #
    #     return render_template('status.html',fileStatus=fileStatus)

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

    # tVAF = [round(elem, 2) for elem in tVAF]
    tVAF = [floor(elem*100)/100 for elem in tVAF]

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

    # to select number of synergies
    q = Job.query.filter_by(job_hash = name).first()
    syn_num = q.synergy_number

    awnwn = []
    for k in range(syn_num):
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
