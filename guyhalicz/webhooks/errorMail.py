import smtplib
from email.message import EmailMessage
from webhooks.conf import EMAIL_ID, EMAIL_PASSWORD

def sendMail(errorMessage):
    msg = EmailMessage()
    msg.set_content(errorMessage)

    msg['Subject'] = 'Error/Exception'
    msg['From'] = EMAIL_ID
    msg['To'] = EMAIL_ID

    # Send the message via our own SMTP server.
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(EMAIL_ID, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()
