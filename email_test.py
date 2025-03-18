import smtplib
from email.mime.text import MIMEText
from email.header import Header

smtp = smtplib.SMTP('smtp.qq.com', 587)
smtp.starttls()
smtp.login('1183038359@qq.com', 'fshaycklvizdiaej')

msg = MIMEText('测试邮件内容', 'plain', 'utf-8')
msg['Subject'] = Header('测试邮件', 'utf-8')
msg['From'] = '1183038359@qq.com'
msg['To'] = '1183038359@qq.com'

smtp.sendmail('1183038359@qq.com', '1183038359@qq.com', msg.as_string())
smtp.quit()