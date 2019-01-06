import smtplib
import os
import datetime

import conf

"""
config file; place it as conf.py

host = "mail.domain.com"
port =  587
tls =  True
username = ""
password = ""
sender = "XYZ <xyz@domain.com>"
to = "ABC <abc@domain.com>"
"""

def send_email( subject, content ):
    """ Send a simple, stupid, text, UTF-8 mail in Python """

    for ill in [ "\n", "\r" ]:
        subject = subject.replace(ill, ' ')

    headers = {
        'Content-Type': 'text/html; charset=utf-8',
        'Content-Disposition': 'inline',
        'Content-Transfer-Encoding': '8bit',
        'From': conf.sender,
        'To': conf.to,
        'Date': datetime.datetime.now().strftime('%a, %d %b %Y  %H:%M:%S %Z'),
        'X-Mailer': 'python',
        'Subject': subject
    }

    # create the message
    msg = ''
    for key, value in headers.items():
        msg += "%s: %s\n" % (key, value)

    # add contents
    msg += "\n%s\n"  % (content)

    s = smtplib.SMTP(conf.host, conf.port)

    if conf.tls:
        s.ehlo()
        s.starttls()
        s.ehlo()

    if conf.username and conf.password:
        s.login(conf.username, conf.password)

    print ("sending %s to %s" % (subject, headers['To']))
    s.sendmail(headers['From'], headers['To'], msg.encode("utf8"))
    s.quit()
send_email('عنوان ایمیل','متن نامه\nسلام. این یک ایمیل آزمایشی است.')