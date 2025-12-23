from flask import Blueprint, render_template, request, jsonify, current_app
from app import db
from app.models import Recipient, EmailTemplate, EmailLog
from app.services import parse_recipient_file, trigger_email_sending
import os
import json
from sqlalchemy import func
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

# --- Pages ---
@main.route('/')
def dashboard():
    return render_template('dashboard.html')

@main.route('/compose')
def compose():
    print("Accessing compose page")
    return render_template('compose.html')

@main.route('/recipients')
def recipients_page():
    return render_template('recipients.html')

# --- API Endpoints ---

@main.route('/api/stats')
def get_stats():
    total_sent = EmailLog.query.filter_by(status='Sent').count()
    total_failed = EmailLog.query.filter_by(status='Failed').count()
    recent_logs = [log.to_dict() for log in EmailLog.query.order_by(EmailLog.timestamp.desc()).limit(10).all()]
    
    # Chart Data: Last 7 days activity
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=6)
    
    # Group by date and status
    daily_stats = db.session.query(
        func.date(EmailLog.timestamp).label('date'),
        EmailLog.status,
        func.count(EmailLog.id)
    ).filter(EmailLog.timestamp >= start_date)\
    .group_by(func.date(EmailLog.timestamp), EmailLog.status).all()
    
    # Process data for Chart.js
    dates = []
    sent_data = []
    failed_data = []
    
    stats_map = {}
    # Initialize last 7 days
    for i in range(7):
        d = (end_date - timedelta(days=6-i)).strftime('%Y-%m-%d')
        dates.append(d)
        stats_map[d] = {'Sent': 0, 'Failed': 0}
        
    for day, status, count in daily_stats:
        if day in stats_map:
            stats_map[day][status] = count
            
    for d in dates:
        sent_data.append(stats_map[d].get('Sent', 0))
        failed_data.append(stats_map[d].get('Failed', 0))

    return jsonify({
        'sent': total_sent, 
        'failed': total_failed, 
        'logs': recent_logs,
        'chart_data': {
            'dates': dates,
            'sent': sent_data,
            'failed': failed_data
        }
    })

@main.route('/api/recipients', methods=['GET', 'POST', 'DELETE'])
def manage_recipients():
    if request.method == 'GET':
        recipients = [r.to_dict() for r in Recipient.query.all()]
        return jsonify(recipients)
    
    if request.method == 'POST':
        data = request.json
        if Recipient.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        new_recipient = Recipient(email=data['email'], name=data.get('name', ''))
        db.session.add(new_recipient)
        db.session.commit()
        return jsonify({'message': 'Recipient added'}), 201

    if request.method == 'DELETE':
        email = request.args.get('email')
        Recipient.query.filter_by(email=email).delete()
        db.session.commit()
        return jsonify({'message': 'Deleted'})

@main.route('/api/upload_recipients', methods=['POST'])
def upload_recipients():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    
    parsed_data = parse_recipient_file(filepath)
    count = 0
    for item in parsed_data:
        if not Recipient.query.filter_by(email=item['email']).first():
            db.session.add(Recipient(email=item['email'], name=item['name']))
            count += 1
    db.session.commit()
    os.remove(filepath)
    return jsonify({'message': f'{count} recipients imported successfully'})

@main.route('/api/templates', methods=['GET', 'POST'])
def manage_templates():
    if request.method == 'GET':
        templates = [t.to_dict() for t in EmailTemplate.query.all()]
        return jsonify(templates)
    
    if request.method == 'POST':
        data = request.json
        new_template = EmailTemplate(name=data['name'], subject=data['subject'], body=data['body'])
        db.session.add(new_template)
        db.session.commit()
        return jsonify({'message': 'Template saved'})

@main.route('/api/send', methods=['POST'])
def send_emails():
    # Using FormData, so we access request.form and request.files
    try:
        smtp_email = request.form.get('smtp_email')
        smtp_password = request.form.get('smtp_password')
        smtp_host = request.form.get('smtp_host')
        smtp_port = request.form.get('smtp_port')
        subject = request.form.get('subject')
        body = request.form.get('body')
        
        # Get recipients (either all from DB or specific list)
        # For this pilot, we send to all active recipients in DB
        db_recipients = Recipient.query.all()
        recipients_list = [{'email': r.email, 'name': r.name} for r in db_recipients]
        
        if not recipients_list:
            return jsonify({'error': 'No recipients found in database'}), 400

        data = {
            'smtp_email': smtp_email,
            'smtp_password': smtp_password,
            'smtp_host': smtp_host,
            'smtp_port': smtp_port,
            'subject': subject,
            'body': body,
            'recipients': recipients_list
        }
        
        files = request.files.getlist('attachments')
        
        # Trigger background sending
        # Note: In production, use Celery. Here we use threading for simplicity.
        trigger_email_sending(current_app._get_current_object(), data, files)
        
        return jsonify({'message': 'Email sending started in background'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
