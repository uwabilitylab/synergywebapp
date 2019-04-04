from flask import render_template
from app import app, db
from app.models import Job

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Job=Job)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(413)
def internal_server_error(e):
    return render_template('413.html'), 413
