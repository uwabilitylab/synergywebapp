import sys
import time
# import sqlite
from email.mime.text import MIMEText
from subprocess import Popen, PIPE
# from synergyPage import User, File, Job
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_bootstrap import Bootstrap
from app.models import User, File, Job
from sqlalchemy import create_engine
from sqlalchemy.sql import select, update
from app.flaskLoadFile import readFlaskExcel
from app.flaskSynergies import calculate_Synergies, calculate_tVAF
import json
import pickle

def send_error_email(error):
    msg = MIMEText(error)
    msg["From"] = "clairem9@uw.edu"
    msg["To"] = "clairem9@uw.edu"
    msg["Subject"] = "Error Synergy App"
    p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
    p.communicate(msg.as_string())


engine = create_engine('sqlite:///app.db')
conn = engine.connect()

log_file = open('./daemon.log', 'a')



while True:

    try:

        job_s = select([Job.job_hash]).where(Job.status == 'submitted')
        job_new = select([Job.job_file_id]).where(Job.job_hash == job_s)
        result = conn.execute(job_new).first()

        if result is not None:

            for row in result:
                the_row = row

                file_s=select([File.raw_file_path]).where(File.file_hash == row)
                result2 = conn.execute(file_s) # this should be the file path for processing that we send
                resultTwo = []
                for row in result2:
                    resultTwo.append(row)
                excel = resultTwo[0]
                job_s2 = select([Job.lowpass_cutoff, Job.highpass_cutoff]).where(Job.status == 'submitted')
                trans = conn.begin()
                results2 = conn.execute(job_s2).first()
                trans.commit()
                resultsTwo = []
                for row in results2:
                    resultsTwo.append(row)

                excel = excel[0][1:]
                update_s = update(Job).where(Job.status == 'submitted').values(status='processing')

                conn.execute(update_s)
                xdata, ydata, aRATE, yfilt, yfiltarray, results, columnNames = readFlaskExcel(excel, resultsTwo[0], resultsTwo[1])

                list1 = [4,6,8,9,10,11,12,13]
                numSym = 5
                WW, tVAF, HH = calculate_Synergies([yfiltarray[i] for i in list1],[1,2,3,4,5,6,7,8],5)


                trans2 = conn.begin()
                update2_s = update(Job).where(Job.status == 'processing').values(status='processed')
                conn.execute(update2_s)
                trans2.commit()

                conn.close()

                muscleNames = [columnNames[i] for i in range(16)]
                muscleNamesShort = [columnNames[i] for i in range(8)]
                tVAFlabels = ["1 Synergy","2 Synergies","3 Synergies","4 Synergies","5 Synergies"]
                labels = ["5","7","9","10","11","12","13","14"]

                resultsJson = json.dumps(results)
                WWJson = json.dumps(WW)
                tVAFJson = json.dumps(tVAF)
                MNJson = json.dumps(muscleNames)
                MNSJson = json.dumps(muscleNamesShort)

                with open('%s.pkl' %(the_row), 'wb') as f:  # Python 3: open(..., 'wb')
                    pickle.dump([resultsJson, WWJson, labels, tVAFJson, tVAFlabels, MNJson, muscleNamesShort], f)

                # currentJob.status = 'processing'
                # db.session.commit()
                #
                # currentJob.lowpass_cutoff
                # currentJob.highpass_cutoff
                # currentJob.synergy_number
                # currentFile = File.query.filter(currentJob.job_file_id).first()
                # excel = currentFile.raw_file_path
                # xdata, ydata, aRATE, yfilt, yfiltarray, results, columnNames = readFlaskExcel(excel, low, high)
                #
                # list1 = [4,6,8,9,10,11,12,13]
                # WW, tVAF, HH = calculate_Synergies([yfiltarray[i] for i in list1],[1,2,3,4,5,6,7,8],int(numSyn))
                #
                # currentJob.status = 'processed'
                # db.session.commit()

                log_file.write('successfully wrote file')

        else:
            time.sleep(5)


            # if result.rows == 1:
                # db.query('UPDATE jobs SET status=\'processing\' WHERE job_id=%s', result.job_id)
                # low = result.lowpass_cutoff
                # high = result.highpass_cutoff
                # synNum = result.synergy_number
                # xdata, ydata, aRATE, yfilt, yfiltarray, results, columnNames = readFlaskExcel(excel, low, high)
                # list1 = [4,6,8,9,10,11,12,13]
                # WW, tVAF, HH = calculate_Synergies([yfiltarray[i] for i in list1],[1,2,3,4,5,6,7,8],int(numSyn))
                #
                # db.query('UPDATE jobs SET status=\'processed\', processed_emg_path=%s WHERE job_id=%s', processed_results.path, result.job_id)
                # log_file.write('successfully wrote file')
            # else:
            #     time.sleep(5)
            #     print('connection failed')

                # except SQLiteError as e:
                #     log_file.write('error in database')
                #     should_exit = True
                #
                #     try:
                #         if e.code == #######
                #             db.connect()
                #             should_exit = False
                #         db.query('UPDATE jobs SET status=\'error\', notes=\'%s\' WHERE job_id=%s', str(e), result.job_id)
                #
                #     except:
                #         should_exit = True
                #
                #     send_error_email(str(e))
                #
                #     if should_exit:
                #         break
                #
                # except KeyboardInterrupt as e: #User hits Ctrl-C
                #     log_file.write('recieved shutdown request')
                #     break
                #
                # except Exception as e:
                #     log_file.write('unidentified error')
                #
                #     try:
                #         # sqlite.query('UPDATE jobs SET status=\'error\', notes=\'%s\' WHERE job_id=%s', str(e), result.job_id)
                #         send_error_email(str(e))
            # db.close()
