import random

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(email, otp):
    # DEV MODE (email fail safe)
    print(f"DEV OTP for {email}: {otp}")
    return True
