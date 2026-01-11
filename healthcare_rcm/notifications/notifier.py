"""
Notification and Workflow Automation System
Handles email notifications, task creation, and automated workflows for prior authorization
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from healthcare_rcm.models.prior_auth_models import (
    PriorAuthRecord, AuthorizationStatus, CallOutcome
)

logger = logging.getLogger(__name__)


class PriorAuthNotifier:
    """Handles notifications and automated workflows for prior authorization"""
    
    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: int = 587,
        smtp_username: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None
    ):
        """
        Initialize notifier
        
        Args:
            smtp_server: SMTP server address (e.g., smtp.gmail.com)
            smtp_port: SMTP port (default: 587 for TLS)
            smtp_username: SMTP authentication username
            smtp_password: SMTP authentication password
            from_email: From email address
        """
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER')
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username or os.getenv('SMTP_USERNAME')
        self.smtp_password = smtp_password or os.getenv('SMTP_PASSWORD')
        self.from_email = from_email or os.getenv('FROM_EMAIL', 'noreply@priorauth.com')
        
        self.email_enabled = bool(self.smtp_server and self.smtp_username and self.smtp_password)
        
        if not self.email_enabled:
            logger.warning("Email notifications disabled - SMTP credentials not configured")
        else:
            logger.info(f"Email notifications enabled via {self.smtp_server}")
    
    def process_record(self, record: PriorAuthRecord, provider_email: Optional[str] = None):
        """
        Process a prior auth record and trigger appropriate notifications/workflows
        
        Args:
            record: PriorAuthRecord to process
            provider_email: Email address of healthcare provider
        """
        logger.info(f"Processing notifications for call {record.call_id}")
        
        # Send email notification
        if provider_email and self.email_enabled:
            self.send_email_notification(record, provider_email)
        
        # Log workflow actions
        self.log_workflow_actions(record)
        
        # Generate task list
        tasks = self.generate_task_list(record)
        if tasks:
            logger.info(f"Generated {len(tasks)} tasks")
            for i, task in enumerate(tasks, 1):
                logger.info(f"  Task {i}: {task['title']}")
    
    def send_email_notification(self, record: PriorAuthRecord, to_email: str):
        """
        Send email notification with call summary
        
        Args:
            record: PriorAuthRecord
            to_email: Recipient email address
        """
        if not self.email_enabled:
            logger.warning("Email not configured - skipping email notification")
            return
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = self._get_email_subject(record)
            
            # Create email body
            text_content = self._generate_text_email(record)
            html_content = self._generate_html_email(record)
            
            # Attach both plain text and HTML versions
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email notification sent to {to_email}")
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
    
    def _get_email_subject(self, record: PriorAuthRecord) -> str:
        """Generate email subject line"""
        status = record.authorization.status.value.upper()
        patient = record.patient.name
        
        if record.authorization.status == AuthorizationStatus.APPROVED:
            return f"✅ Prior Auth APPROVED - {patient} - {record.procedure.cpt_code}"
        elif record.authorization.status == AuthorizationStatus.DENIED:
            return f"❌ Prior Auth DENIED - {patient} - Action Required"
        elif record.authorization.status == AuthorizationStatus.PENDING:
            return f"⏳ Prior Auth PENDING - {patient} - Documentation Needed"
        else:
            return f"📋 Prior Auth Update - {patient} - {status}"
    
    def _generate_text_email(self, record: PriorAuthRecord) -> str:
        """Generate plain text email content"""
        lines = []
        lines.append("PRIOR AUTHORIZATION CALL SUMMARY")
        lines.append("=" * 60)
        lines.append("")
        
        # Status
        lines.append(f"Status: {record.authorization.status.value.upper()}")
        lines.append(f"Call Date: {record.call_date.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Patient
        lines.append("PATIENT INFORMATION")
        lines.append(f"Name: {record.patient.name}")
        if record.patient.member_id:
            lines.append(f"Member ID: {record.patient.member_id}")
        lines.append("")
        
        # Procedure
        lines.append("PROCEDURE")
        lines.append(f"CPT Code: {record.procedure.cpt_code}")
        if record.procedure.description:
            lines.append(f"Description: {record.procedure.description}")
        lines.append("")
        
        # Authorization
        if record.authorization.authorization_number:
            lines.append(f"✅ Authorization Number: {record.authorization.authorization_number}")
        if record.authorization.reference_number:
            lines.append(f"Reference Number: {record.authorization.reference_number}")
        lines.append("")
        
        # Next steps
        if record.next_steps:
            lines.append("NEXT STEPS")
            for step in record.next_steps:
                lines.append(f"• {step}")
            lines.append("")
        
        # Errors/warnings
        if record.validation_errors:
            lines.append("⚠️ ATTENTION REQUIRED")
            for error in record.validation_errors:
                lines.append(f"• {error}")
            lines.append("")
        
        lines.append("=" * 60)
        lines.append("This is an automated message from the Prior Authorization system.")
        
        return "\n".join(lines)
    
    def _generate_html_email(self, record: PriorAuthRecord) -> str:
        """Generate HTML email content"""
        status_color = {
            AuthorizationStatus.APPROVED: "#28a745",
            AuthorizationStatus.DENIED: "#dc3545",
            AuthorizationStatus.PENDING: "#ffc107",
            AuthorizationStatus.PEER_TO_PEER_REQUIRED: "#17a2b8",
        }.get(record.authorization.status, "#6c757d")
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: {status_color}; color: white; padding: 20px; border-radius: 5px; }}
        .content {{ background-color: #f8f9fa; padding: 20px; margin-top: 20px; border-radius: 5px; }}
        .section {{ margin-bottom: 20px; }}
        .section-title {{ font-weight: bold; color: #495057; margin-bottom: 10px; }}
        .info-row {{ margin: 5px 0; }}
        .next-steps {{ background-color: #e7f3ff; padding: 15px; border-left: 4px solid #0066cc; }}
        .error {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; }}
        ul {{ margin: 10px 0; padding-left: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Prior Authorization Call Summary</h2>
            <p><strong>Status: {record.authorization.status.value.upper()}</strong></p>
        </div>
        
        <div class="content">
            <div class="section">
                <div class="section-title">PATIENT INFORMATION</div>
                <div class="info-row">Name: {record.patient.name}</div>
                {f'<div class="info-row">Member ID: {record.patient.member_id}</div>' if record.patient.member_id else ''}
            </div>
            
            <div class="section">
                <div class="section-title">PROCEDURE</div>
                <div class="info-row">CPT Code: {record.procedure.cpt_code}</div>
                {f'<div class="info-row">Description: {record.procedure.description}</div>' if record.procedure.description else ''}
            </div>
            
            {f'''
            <div class="section">
                <div class="section-title">AUTHORIZATION</div>
                <div class="info-row">✅ Authorization Number: {record.authorization.authorization_number}</div>
                {f'<div class="info-row">Reference: {record.authorization.reference_number}</div>' if record.authorization.reference_number else ''}
            </div>
            ''' if record.authorization.authorization_number else ''}
            
            {f'''
            <div class="next-steps">
                <div class="section-title">NEXT STEPS</div>
                <ul>
                {''.join([f'<li>{step}</li>' for step in record.next_steps])}
                </ul>
            </div>
            ''' if record.next_steps else ''}
            
            {f'''
            <div class="error">
                <div class="section-title">⚠️ ATTENTION REQUIRED</div>
                <ul>
                {''.join([f'<li>{error}</li>' for error in record.validation_errors])}
                </ul>
            </div>
            ''' if record.validation_errors else ''}
        </div>
        
        <p style="color: #6c757d; font-size: 12px; margin-top: 20px;">
            This is an automated message from the Prior Authorization system.<br>
            Call ID: {record.call_id}<br>
            Date: {record.call_date.strftime('%Y-%m-%d %H:%M:%S')}
        </p>
    </div>
</body>
</html>
"""
        return html
    
    def log_workflow_actions(self, record: PriorAuthRecord):
        """Log appropriate workflow actions based on authorization status"""
        logger.info("📋 WORKFLOW ACTIONS:")
        
        if record.authorization.status == AuthorizationStatus.APPROVED:
            logger.info("  ✅ Authorization approved - proceed with scheduling")
            logger.info("  📝 Update EHR with authorization number")
            logger.info("  📞 Contact patient to schedule procedure")
            logger.info("  💾 Update billing system")
            
        elif record.authorization.status == AuthorizationStatus.PENDING:
            logger.info("  ⏳ Authorization pending - submit documentation")
            if record.documentation.required_documents:
                logger.info(f"  📄 Gather: {', '.join(record.documentation.required_documents)}")
            if record.documentation.fax_number:
                logger.info(f"  📠 Fax to: {record.documentation.fax_number}")
            if record.documentation.submission_deadline:
                days_until = (record.documentation.submission_deadline - datetime.now().date()).days
                logger.info(f"  ⏰ Deadline: {record.documentation.submission_deadline} ({days_until} days)")
            
        elif record.authorization.status == AuthorizationStatus.DENIED:
            logger.info("  ❌ Authorization denied - initiate appeal")
            logger.info("  📋 Review denial reason with provider")
            logger.info("  📝 Prepare appeal documentation")
            logger.info("  📞 Contact insurance for appeal process")
            
        elif record.authorization.status == AuthorizationStatus.PEER_TO_PEER_REQUIRED:
            logger.info("  👨‍⚕️ Peer-to-peer review required")
            logger.info("  📞 Schedule call with insurance medical director")
            logger.info("  📄 Prepare clinical documentation")
    
    def generate_task_list(self, record: PriorAuthRecord) -> List[Dict[str, Any]]:
        """
        Generate actionable task list based on authorization status
        
        Returns:
            List of task dictionaries with title, priority, due_date
        """
        tasks = []
        
        if record.authorization.status == AuthorizationStatus.APPROVED:
            if record.authorization.authorization_number:
                tasks.append({
                    'title': f'Update EHR with authorization {record.authorization.authorization_number}',
                    'priority': 'high',
                    'due_date': datetime.now() + timedelta(days=1)
                })
            tasks.append({
                'title': f'Contact {record.patient.name} to schedule {record.procedure.cpt_code}',
                'priority': 'high',
                'due_date': datetime.now() + timedelta(days=2)
            })
            
        elif record.authorization.status == AuthorizationStatus.PENDING:
            if record.documentation.required_documents:
                tasks.append({
                    'title': f'Gather documentation: {", ".join(record.documentation.required_documents[:2])}',
                    'priority': 'urgent',
                    'due_date': record.documentation.submission_deadline or datetime.now().date() + timedelta(days=2)
                })
            if record.documentation.fax_number:
                tasks.append({
                    'title': f'Submit documents via fax to {record.documentation.fax_number}',
                    'priority': 'urgent',
                    'due_date': record.documentation.submission_deadline or datetime.now().date() + timedelta(days=3)
                })
            if record.timeline.expected_decision_date:
                tasks.append({
                    'title': f'Follow up on authorization decision',
                    'priority': 'medium',
                    'due_date': record.timeline.expected_decision_date + timedelta(days=1)
                })
                
        elif record.authorization.status == AuthorizationStatus.DENIED:
            tasks.append({
                'title': f'Review denial reason for {record.patient.name}',
                'priority': 'urgent',
                'due_date': datetime.now() + timedelta(days=1)
            })
            tasks.append({
                'title': 'Prepare appeal documentation',
                'priority': 'urgent',
                'due_date': datetime.now() + timedelta(days=3)
            })
            tasks.append({
                'title': 'Submit formal appeal',
                'priority': 'high',
                'due_date': datetime.now() + timedelta(days=7)
            })
            
        elif record.authorization.status == AuthorizationStatus.PEER_TO_PEER_REQUIRED:
            if record.representative.phone:
                tasks.append({
                    'title': f'Schedule peer-to-peer at {record.representative.phone}',
                    'priority': 'urgent',
                    'due_date': datetime.now() + timedelta(days=1)
                })
            tasks.append({
                'title': 'Prepare clinical documentation for peer review',
                'priority': 'high',
                'due_date': datetime.now() + timedelta(days=2)
            })
        
        return tasks


# Convenience function
def notify_and_automate(
    record: PriorAuthRecord,
    provider_email: Optional[str] = None,
    smtp_config: Optional[Dict[str, Any]] = None
):
    """
    Convenience function to trigger notifications and automation
    
    Args:
        record: PriorAuthRecord to process
        provider_email: Provider email address
        smtp_config: Optional SMTP configuration dict
    """
    if smtp_config:
        notifier = PriorAuthNotifier(**smtp_config)
    else:
        notifier = PriorAuthNotifier()
    
    notifier.process_record(record, provider_email)
