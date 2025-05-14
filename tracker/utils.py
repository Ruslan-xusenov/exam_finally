import re

def is_email(identifier):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, identifier) is not None


def is_phone(identifier):
    phone_regex = r'^\+?[\d\s\-]+$'
    return re.match(phone_regex, identifier) is not None