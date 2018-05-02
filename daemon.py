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
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import json
import pickle
import csv

def send_error_email(error):

    msg = MIMEText(repr(error))
    msg['Subject'] = 'The contents of'
    msg['From'] = "clairem2520@yahoo.com"
    msg['To'] = "clairem9@uw.edu"
    s = smtplib.SMTP('localhost', 80)
    s.sendmail("clairem9@uw.edu", ["clairem9@uw.edu"], msg.as_string())
    s.quit()


engine = create_engine('sqlite:///app.db')
log_file = open('./daemon.log', 'a')

while True:

    try:

        with engine.connect() as conn:

            # Unprocessed Job selection
            job_query = select([Job.job_file_id, Job.lowpass_cutoff, Job.highpass_cutoff, Job.synergy_number, Job.job_hash]).where(Job.status == 'submitted')
            selected_job = conn.execute(job_query).first()

            if selected_job is not None:

                # Corresponding File selection
                file_query = select([File.raw_file_path]).where(File.file_user_hash == selected_job[0])
                selected_file = conn.execute(file_query).first()
                excel = "." + selected_file[0]

                # Update job to processing
                update_query_pro = update(Job).where(Job.job_file_id == selected_job[0]).values(status='processing')
                processing = conn.execute(update_query_pro)

                # Processing file
                xdata, ydata, aRATE, yfilt, yfiltarray, results, columnNames = readFlaskExcel(excel, selected_job[1], selected_job[2])
                list1 = [4,6,8,9,10,11,12,13]

                # Calculating Synergies
                WW, tVAF, HH = calculate_Synergies([yfiltarray[i] for i in list1],[1,2,3,4,5,6,7,8], selected_job[3])

                # Update job to processed
                update_query_done = update(Job).where(Job.job_file_id == selected_job[0]).values(status='processed')
                conn.execute(update_query_done)

                # Getting variables in proper form for templates
                muscleNames = [columnNames[i] for i in range(16)]
                muscleNamesShort = [columnNames[i] for i in range(8)]
                tVAFlabels = ["1 Synergy","2 Synergies","3 Synergies","4 Synergies","5 Synergies"]
                labels = ["5","7","9","10","11","12","13","14"]
                resultsJson = json.dumps(results)
                WWJson = json.dumps(WW)
                tVAFJson = json.dumps(tVAF)
                MNJson = json.dumps(muscleNames)
                MNSJson = json.dumps(muscleNamesShort)

                # Generating matplotlib figures of EMG
                pp = PdfPages('app/static/plots/matplots_%s.pdf' %(selected_job[4]))
                plotEMG(xdata, ydata, yfilt, selected_job[4], muscleNames, pp)
                plotWeights(WW, selected_job[4], muscleNamesShort, pp)
                plotAct(HH, selected_job[4], pp)
                pp.close()


                # with open('app/static/resultcsv/%s.csv' %(selected_job[4]), "w") as f:
                #     writer = csv.writer(f)
                #     writer.writerow(["Highpass"])
                #     writer.writerows(selected_job[2])
                #     writer.writerow(["Lowpass"])
                #     writer.writerows(selected_job[1])
                #     writer.writerow(["Number of Synergies"])
                #     writer.writerows(selected_job[3])
                #     writer.writerow(["Muscles included"])
                #     writer.writerow(list1)
                #     writer.writerow(['Unfiltered Emg'])
                #     for i in range(16):
                #         writer.writerow(ydata['EMG %s' %(i+1)])
                #     writer.writerow(['Filtered Emg'])
                #     for i in range(16):
                #         writer.writerow(yfilt['EMGFilt %s' %(i+1)])
                #     writer.writerow(["tVAF"])
                #     writer.writerow(tVAF)
                #     writer.writerow(["Weights"])
                #     for item in WW:
                #         writer.writerows(item)
                #     writer.writerow(["Activations"])
                #     for item in HH:
                #         writer.writerows(item)


                with open('pklfiles/%s.pkl' %(selected_job[4]), 'wb') as f:  # Python 3: open(..., 'wb')
                    pickle.dump([resultsJson, WWJson, labels, tVAFJson, tVAFlabels, MNJson, muscleNamesShort], f)

                log_file.write('successfully wrote file')

            else:
                time.sleep(5)

    except SQLAlchemyError as e:
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

        try:
            error_update = update(Job).where(Job.job_file_id == selected_job[0]).values(status='error')
            conn.execute(error_update)

        except:
            pass

        # send_error_email(e)
