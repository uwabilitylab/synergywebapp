from flask_mail import Message
from app import mail

def send_email(subject, sender, recipients, text_body):
  msg = Message(subject, sender=sender, recipients=recipients)
  msg.body = text_body
  mail.send(msg)

def send_confirmation_email(sender, recipients):
    msg = Message('Thanks for Registering!',sender=sender,recipients=recipients)
    msg.body = 'Thanks for registering to use the muscle synergy calculator! Your account has been approved and you will now be able to upload files. If you have any questions contact Claire Mitchell at clairemit9@gmail.com.'
    mail.send(msg)
