from ultralytics import YOLO
from email.message import EmailMessage
import ssl
from dotenv import load_dotenv
import smtplib
import os 


load_dotenv()


def send_email(cont_dic, img_path=None):

    mail_sender = os.environ.get('sender_email')
    mail_password = os.environ.get('app_password')
    mail_receiver = os.environ.get('receiver_email')

    
    subject = 'Complaint Register'
    body = f"Potholes are identifed at location: {cont_dic['location']}. It's a {cont_dic['highway_type']} that contains {cont_dic['size']}. Take necessary actions"

    em = EmailMessage()
    em['From'] = mail_sender
    em['To'] = mail_receiver
    em['subject'] = subject

    em.set_content(body)

    if img_path:
        with open(img_path, 'rb') as img_file:
            img_data = img_file.read()
            em.add_attachment(img_data, maintype='image', subtype='png', filename=os.path.basename(img_path))
            
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(mail_sender, mail_password)
        smtp.sendmail(mail_sender, mail_receiver, em.as_string())


def detect_potholes(model, source_path=None):
    results = model(source_path, save=True)
    for res in results:
        save_dir = res.save_dir

    return save_dir






