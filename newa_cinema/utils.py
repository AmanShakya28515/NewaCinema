import random
from django.core.mail import send_mail
from django.conf import settings

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    subject = "Your Login OTP"
    message = f"Your OTP code is: {otp}"
    from_email = f"CineDabali <{settings.EMAIL_HOST_USER}>" 
    recipient_list = [email]
    
    send_mail(subject, message, from_email, recipient_list)

