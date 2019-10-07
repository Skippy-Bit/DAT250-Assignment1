from bs4 import BeautifulSoup
import hashlib

# File containing all utils functions for the application 

# Hash the password using SHA256 and a salt
def hash_password(user_password):
    SALT = '6385c57a230996dcbf7ba2bcb68b0b00'
    return hashlib.sha256(user_password.encode()+SALT.encode()).hexdigest()

# Sanitize string, removes html
def sanitizeStr(value, strip = True):
    soup = BeautifulSoup(value,features="html.parser")
    text = soup.get_text(' ',strip=strip)
    return text