import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
import os
import threading

def parse_recipient_file(filepath):
    """Parses CSV or Excel files to extract Name and Email."""
    try:
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)
        
        # Normalize headers
        df.columns = [c.lower() for c in df.columns]
        recipients = []
        
        for _, row in df.iterrows():
            email = row.get('email')
            name = row.get('name', '')
            if email:
                recipients.append({'email': str(email).strip(), 'name': str(name).strip()})
        return recipients
    except Exception as e:
        print(f"Error parsing file: {e}")
        return []

def send_bulk_email_thread(app, sender_email, sender_password, smtp_server, smtp_port, subject, body_template, recipients, attachment_paths):
    """Background thread function to send emails."""
    from app import db
    from app.models import EmailLog

    with app.app_context():
        try:
            # Setup SMTP connection
            server = smtplib.SMTP(smtp_server, int(smtp_port))
            server.starttls()
            server.login(sender_email, sender_password)

            for recipient in recipients:
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = recipient['email']
                
                # Personalize Subject and Body
                personalized_subject = subject.replace('{Name}', recipient['name'])
                personalized_body = body_template.replace('{Name}', recipient['name'])
                
                msg['Subject'] = personalized_subject
                msg.attach(MIMEText(personalized_body, 'html'))

                # Attach files
                for path in attachment_paths:
                    if os.path.exists(path):
                        with open(path, "rb") as attachment:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename= {os.path.basename(path)}",
                        )
                        msg.attach(part)

                try:
                    server.send_message(msg)
                    log = EmailLog(recipient_email=recipient['email'], status='Sent')
                except Exception as e:
                    log = EmailLog(recipient_email=recipient['email'], status='Failed', error_message=str(e))
                
                db.session.add(log)
                db.session.commit()

            server.quit()
            
            # Cleanup attachments
            for path in attachment_paths:
                if os.path.exists(path):
                    os.remove(path)

        except Exception as e:
            print(f"SMTP Error: {e}")

def trigger_email_sending(app, data, files):
    """Prepares data and starts the background thread."""
    # Save attachments temporarily
    attachment_paths = []
    if files:
        for f in files:
            path = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
            f.save(path)
            attachment_paths.append(path)

    # Start thread
    thread = threading.Thread(
        target=send_bulk_email_thread,
        args=(
            app,
            data['smtp_email'],
            data['smtp_password'],
            data['smtp_host'],
            data['smtp_port'],
            data['subject'],
            data['body'],
            data['recipients'],
            attachment_paths
        )
    )
    thread.start()
