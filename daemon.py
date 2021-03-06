import sys
import time
from email.mime.text import MIMEText
from subprocess import Popen, PIPE
import smtplib
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_bootstrap import Bootstrap
from app.models import User, File, Job
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import select, update
from app.flaskLoadFile import readFlaskExcel
from app.flaskSynergies import calculate_Synergies, calculate_tVAF
from app.plotEmg import plotEMG
from app.plotActivations import plotAct
from app.plotWeights import plotWeights
from app.plotTVAF import plotTVAF
from app import app
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import json
import pickle
import csv
import gc
import os
import ast
import traceback

plt.style.use('./deploy/synergywebapp.mplstyle')


def send_error_email(error):

    s = 'Error Message'
    se = app.config['ADMINS'][0]
    r = ['clairemit9@gmail.com']
    tb = MIMEText(repr(error))
    send_email(subject=s, sender=se, recipients=r, text_body=tb)

# Make this for the outputs in code cleanup
#def produce_job_outputs():


engine = create_engine('sqlite:///run/app.db')
log_file = open('./run/daemon.log', 'a')

while True:

    try:

        with engine.connect() as conn:

            # Unprocessed Job selection
            job_query = select([Job.job_file_id, Job.lowpass_cutoff, Job.highpass_cutoff, Job.synergy_number, Job.job_hash, Job.included_muscles, Job.matched_names]).where(Job.status == 'submitted')
            selected_job = conn.execute(job_query).first()

            if selected_job is not None:

                # Corresponding File selection
                file_query = select([File.new_file_path]).where(File.new_file_path == selected_job[0])
                selected_file = conn.execute(file_query).first()
                excel = app.config['UPLOAD_FOLDER'] + "/" + selected_file[0]

                # Update job to processing
                update_query_pro = update(Job).where(Job.job_hash == selected_job[4]).values(status='processing')
                processing = conn.execute(update_query_pro)

                musclesIncluded = json.loads(selected_job[5])
                namesIncluded = json.loads(selected_job[6])

                # Processing file
                xdata, ydata, aRATE, yfilt, yfiltarray, results, columnNames = readFlaskExcel(excel, musclesIncluded, selected_job[1], selected_job[2])

                # Force a garbage collection
                gc.collect()

                # Calculating Synergies
                WW, tVAF, HH, vaf = calculate_Synergies(yfiltarray, selected_job[3])
                muscleNames = columnNames

                # Generating matplotlib figures of EMG
                pp = PdfPages('app/static/plots/matplots_%s.pdf' %(selected_job[4]))
                plotEMG(xdata, ydata, yfilt, selected_job[4], namesIncluded, pp)
                plotTVAF(tVAF, selected_job[4], pp)
                plotWeights(WW, selected_job[4], namesIncluded, pp)
                plotAct(xdata, HH, selected_job[4], pp)
                pp.close()

                with open('app/static/resultcsv/%s.csv' %(selected_job[4]), "w") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Highpass"])
                    writer.writerow([int(selected_job[2])])
                    writer.writerow(["Lowpass"])
                    writer.writerow([int(selected_job[1])])
                    writer.writerow(["Max Number of Synergies"])
                    writer.writerow([int(selected_job[3])])
                    writer.writerow(["Muscles included"])
                    writer.writerow(musclesIncluded)
                    writer.writerow(['Unfiltered Emg'])
                    for i in range(len(ydata)):
                        writer.writerow(['EMG %s' %(i+1)])
                        writer.writerow(ydata['EMG %s' %(i+1)])
                    writer.writerow(['Filtered Emg'])
                    for i in range(len(yfilt)):
                        writer.writerow(['EMGFilt %s' %(i+1)])
                        writer.writerow(yfilt['EMGFilt %s' %(i+1)])
                    writer.writerow(["tVAF"])
                    writer.writerow(tVAF)
                    writer.writerow(["Weights"])
                    i = 1
                    for item in WW:
                        writer.writerow(["Synergy Solution %s" %(i)])
                        writer.writerows(item)
                        i = i + 1
                    writer.writerow(["Activations"])
                    i = 1
                    for item in HH:
                        writer.writerow(["Synergy Solution %s" %(i)])
                        writer.writerows(item)
                        i = i + 1

                with open('pklfiles/%s.pkl' %(selected_job[4]), 'wb') as f:  # Python 3: open(..., 'wb')
                    pickle.dump([tVAF, vaf], f)


                log_file.write('successfully wrote file')

                # Update job to processed
                update_query_done = update(Job).where(Job.job_hash == selected_job[4]).values(status='processed')
                conn.execute(update_query_done)

            else:
                time.sleep(5)

    except SQLAlchemyError as e:
        print(traceback.format_exc())
        log_file.write('boo database error')
        should_exit = True

        try:
            if e == TimeoutError:
                conn = engine.connect()
                should_exit = False

        except:
            should_exit = True

        # send_error_email(e)

        if should_exit:
            conn.close()
            break

    except KeyboardInterrupt as e:
        # send_error_email(e)
        conn.close()
        log_file.write('recieved shutdown request')
        break

    except Exception as e:
        log_file.write('boo other error')
        print(e)
        print(traceback.format_exc())

        try:
            error_update = update(Job).where(Job.job_file_id == selected_job[0]).values(status='error')
            conn.execute(error_update)

        except:
            pass

        # send_error_email(e)
