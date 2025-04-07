import os
import sys
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

sendgrid_key = os.environ.get('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = "noreply@discordtools.com"  # Or use a valid SendGrid verified sender

def send_email(to_email, subject, text_content=None, html_content=None):
    """Send an email using SendGrid"""
    if not sendgrid_key:
        print("SENDGRID_API_KEY not set")
        return False
        
    sg = SendGridAPIClient(sendgrid_key)

    message = Mail(
        from_email=Email(DEFAULT_FROM_EMAIL),
        to_emails=To(to_email),
        subject=subject
    )

    if html_content:
        message.content = Content("text/html", html_content)
    elif text_content:
        message.content = Content("text/plain", text_content)
    else:
        return False

    try:
        sg.send(message)
        return True
    except Exception as e:
        print(f"SendGrid error: {e}")
        return False

def send_verification_email(user, base_url):
    """Send email verification link"""
    verification_url = f"{base_url}/verify/{user.verification_token}"
    subject = "Verify your Discord Tools account"
    html_content = f"""
    <html>
    <body>
        <h2>Welcome to Discord Tools!</h2>
        <p>Thank you for signing up. Please verify your email address by clicking the link below:</p>
        <p><a href="{verification_url}">Verify Email Address</a></p>
        <p>If you didn't create this account, you can safely ignore this email.</p>
        <p>Best regards,<br>The Discord Tools Team</p>
    </body>
    </html>
    """
    return send_email(user.email, subject, html_content=html_content)

def send_password_reset_email(user, base_url):
    """Send password reset link"""
    reset_url = f"{base_url}/reset-password/{user.reset_token}"
    subject = "Reset your Discord Tools password"
    html_content = f"""
    <html>
    <body>
        <h2>Password Reset Request</h2>
        <p>We received a request to reset your password. Click the link below to create a new password:</p>
        <p><a href="{reset_url}">Reset Password</a></p>
        <p>This link will expire in 24 hours.</p>
        <p>If you didn't request a password reset, you can safely ignore this email.</p>
        <p>Best regards,<br>The Discord Tools Team</p>
    </body>
    </html>
    """
    return send_email(user.email, subject, html_content=html_content)