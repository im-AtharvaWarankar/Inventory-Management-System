
# Reset Password Link
def reset_password_message(token):
    return f"""Your reset password token is {token}"""


# Update Password Template
def update_password_message():
    return """Password has been updated successfully"""


# Register Message
def register_message():
    return """Successfully registered."""


# Admin reset password
def admin_reset_password_message(token):
    return f"""Your reset password token is {token}"""


# Admin Update Password Template
def admin_update_password_message():
    return """Password has been updated successfully"""


# Admin Register Message
def admin_register_message():
    return """Successfully registered."""


def send_otp(token):
    return f"""You have requested an OTP(One-time Password) to log in. Please enter the following code when prompted: {token}"""
