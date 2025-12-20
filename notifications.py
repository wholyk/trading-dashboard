"""
Monitoring and notification module for the trading bot.
Provides real-time alerts and status updates via email and logging.
"""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, List
from datetime import datetime


logger = logging.getLogger(__name__)


class NotificationService:
    """Handles notifications via email and other channels."""
    
    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        sender_email: Optional[str] = None,
        sender_password: Optional[str] = None,
        recipient_email: Optional[str] = None
    ):
        """
        Initialize notification service.
        
        Args:
            smtp_server: SMTP server address (or from environment)
            smtp_port: SMTP port (or from environment)
            sender_email: Sender email address (or from environment)
            sender_password: Sender email password (or from environment)
            recipient_email: Recipient email address (or from environment)
        """
        self.smtp_server = smtp_server or os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.environ.get('SMTP_PORT', '587'))
        self.sender_email = sender_email or os.environ.get('SENDER_EMAIL')
        self.sender_password = sender_password or os.environ.get('SENDER_PASSWORD')
        self.recipient_email = recipient_email or os.environ.get('RECIPIENT_EMAIL')
        
        self.enabled = all([
            self.sender_email,
            self.sender_password,
            self.recipient_email
        ])
        
        if self.enabled:
            logger.info(f"NotificationService initialized (recipient: {self.recipient_email})")
        else:
            logger.warning("NotificationService disabled - missing email configuration")
    
    def send_email(
        self,
        subject: str,
        body: str,
        is_html: bool = False
    ) -> bool:
        """
        Send email notification.
        
        Args:
            subject: Email subject
            body: Email body
            is_html: Whether body is HTML (default False)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.warning("Email notifications not configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            
            # Attach body
            mime_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(body, mime_type))
            
            # Connect and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Email sent: {subject}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_trading_summary(self, summary: Dict) -> bool:
        """
        Send trading execution summary via email.
        
        Args:
            summary: Execution summary dictionary
        
        Returns:
            True if successful, False otherwise
        """
        timestamp = summary.get('timestamp', datetime.now().isoformat())
        orders_placed = summary.get('orders_placed', 0)
        symbols_analyzed = summary.get('symbols_analyzed', 0)
        errors = summary.get('errors', [])
        
        # Create email body
        subject = f"Trading Bot Summary - {timestamp}"
        
        body = f"""
Trading Bot Execution Summary
==============================

Timestamp: {timestamp}
Symbols Analyzed: {symbols_analyzed}
Orders Placed: {orders_placed}

"""
        
        if errors:
            body += "Errors:\n"
            for error in errors:
                body += f"  - {error}\n"
        else:
            body += "Status: No errors reported\n"
        
        body += "\n"
        body += "This is an automated message from your trading bot.\n"
        
        return self.send_email(subject, body)
    
    def send_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "info"
    ) -> bool:
        """
        Send alert notification.
        
        Args:
            alert_type: Type of alert (e.g., "MAX_DRAWDOWN", "ORDER_FAILED")
            message: Alert message
            severity: Alert severity ("info", "warning", "error", "critical")
        
        Returns:
            True if successful, False otherwise
        """
        subject = f"[{severity.upper()}] Trading Bot Alert: {alert_type}"
        
        body = f"""
Trading Bot Alert
=================

Type: {alert_type}
Severity: {severity.upper()}
Time: {datetime.now().isoformat()}

Message:
{message}

This is an automated alert from your trading bot.
"""
        
        return self.send_email(subject, body)


class TradingMonitor:
    """Monitors trading bot performance and generates alerts."""
    
    def __init__(self, notification_service: Optional[NotificationService] = None):
        """
        Initialize trading monitor.
        
        Args:
            notification_service: NotificationService instance (optional)
        """
        self.notification_service = notification_service or NotificationService()
        self.metrics = {
            'total_executions': 0,
            'total_orders': 0,
            'total_errors': 0,
            'last_execution': None
        }
        logger.info("TradingMonitor initialized")
    
    def record_execution(self, summary: Dict):
        """
        Record a trading execution and send notifications.
        
        Args:
            summary: Execution summary dictionary
        """
        self.metrics['total_executions'] += 1
        self.metrics['total_orders'] += summary.get('orders_placed', 0)
        self.metrics['total_errors'] += len(summary.get('errors', []))
        self.metrics['last_execution'] = summary.get('timestamp')
        
        # Send summary notification
        self.notification_service.send_trading_summary(summary)
        
        # Send alerts for errors
        errors = summary.get('errors', [])
        if errors:
            for error in errors:
                self.notification_service.send_alert(
                    alert_type="EXECUTION_ERROR",
                    message=error,
                    severity="error"
                )
    
    def check_drawdown_alert(self, current_value: float, peak_value: float, threshold: float = 0.05):
        """
        Check for drawdown and send alert if threshold exceeded.
        
        Args:
            current_value: Current portfolio value
            peak_value: Peak portfolio value
            threshold: Drawdown threshold for alert (default 5%)
        """
        if peak_value == 0:
            return
        
        drawdown = (peak_value - current_value) / peak_value
        
        if drawdown >= threshold:
            self.notification_service.send_alert(
                alert_type="DRAWDOWN_WARNING",
                message=f"Portfolio drawdown: {drawdown:.2%} (threshold: {threshold:.2%})",
                severity="warning" if drawdown < 0.10 else "critical"
            )
    
    def get_metrics(self) -> Dict:
        """Get monitoring metrics."""
        return self.metrics.copy()


def send_test_notification():
    """Send a test notification to verify configuration."""
    service = NotificationService()
    
    if not service.enabled:
        print("Email notifications not configured.")
        print("Set the following environment variables:")
        print("  - SENDER_EMAIL")
        print("  - SENDER_PASSWORD")
        print("  - RECIPIENT_EMAIL")
        print("  - SMTP_SERVER (optional, defaults to smtp.gmail.com)")
        print("  - SMTP_PORT (optional, defaults to 587)")
        return False
    
    success = service.send_email(
        subject="Trading Bot - Test Notification",
        body="This is a test notification from your trading bot. Configuration successful!"
    )
    
    if success:
        print("Test notification sent successfully!")
    else:
        print("Failed to send test notification. Check logs for details.")
    
    return success


if __name__ == "__main__":
    send_test_notification()
