# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
import ssl

class EmailSender:
    def __init__(self):
        self.smtp_server = "smtp.163.com"
        self.smtp_port = 465  # 使用SSL端口
        self.sender_email = "cheunghonghui1998@163.com"
        self.password = "PPj56V79k59Ws76Q"

    def send_email(self, to_emails: List[str], subject: str, content: str):
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = subject

        msg.attach(MIMEText(content, 'html'))

        try:
            # 创建SSL上下文
            context = ssl.create_default_context()
            
            # 使用SSL连接
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                print("连接到SMTP服务器...")
                server.login(self.sender_email, self.password)
                print("登录成功")
                
                # 发送邮件
                server.send_message(msg)
                print(f"邮件已发送到: {to_emails}")
                return True
                
        except Exception as e:
            print(f"发送邮件失败: {str(e)}")
            return False





