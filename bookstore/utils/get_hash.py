from hashlib import sha1

def get_hash(string):
    sh1 = sha1()
    sh1.update(string.encode('utf8'))
    return sh1.hexdigest()
