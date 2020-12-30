#!/usr/bin/env python

"""
    This tool will encrypt passwords and store them in a pickle file. Please use a real password vault product instead!
    This tool does not provide a cryptographically secure or foolproof method to store passwords.
    It obfuscates plaintext passwords usage in your scripts.

    When you import the password_tool for the first time it will create 3 files: .salt, .password, and vault.
    .salt is a generated string which is used for the salt function. You can adjust the length by adjusting the
    salt_len variable.

    .password contains a generated password and is stored in base64 encoded format. You can adjust the length of the
    password by adjusting the passphrase_len variable.

    vault is the file containing the stored entries.


    Examples:

    password_tool.put('example_key', 'thisisapassword')

    password_tool.get('example_key')
    'thisisapassword'

    password_tool.prompt_put('example_key2')

    Please enter a value for example_key2:

    password_tool.get('example_key2')
    'qwerty'

    password_tool.delete('example_key2')

"""

import base64
import os
import pickle
import secrets
import string
import stat
from getpass import getpass
from Crypto.Cipher import AES
from pbkdf2 import PBKDF2


saltseed_file = '.salt'
passphrase_file = '.password'
vault_file = 'vault'
passphrase_len = 64  # 512-bit passphrase
key_len = 32  # 256-bit key
block_size = 16   # 16-bit blocks
iv_len = 16  # 128-bits IV
salt_len = 8  # 64-bits salt


""" 
    Below are functions used to retrieve the salt and encrypt or decrypt vault entries.
"""


def get_salt(key):
    return PBKDF2(key, saltseed).read(salt_len)


def encrypt(plaintext, salt):
    initvector = os.urandom(iv_len)
    key = PBKDF2(passphrase, salt).read(key_len)
    cipher = AES.new(key, AES.MODE_CBC, initvector)

    return initvector + cipher.encrypt(plaintext +
                                       str(' '*(block_size - (len(plaintext) % block_size))).encode('utf-8'))


def decrypt(ciphertext, salt):
    key = PBKDF2(passphrase, salt).read(key_len)
    initvector = ciphertext[:iv_len]
    ciphertext = ciphertext[iv_len:]
    cipher = AES.new(key, AES.MODE_CBC, initvector)

    return cipher.decrypt(ciphertext).decode('utf-8').rstrip(' ')


""" 
    Below are functions available for use.
    - put_overwrite() will encrypt the passed value and overwrite the entry if it already exists.
    - put() will check if the entry already exists. If it does not exist it will encrypt and store the passed values.
    - get() will retrieve the entry from the vault.
    - prompt_put() will prompt the user to input a value, using getpass, instead of passing it directly.
    - prompt_put_overwrite() does the same as prompt_put() but overwrites the entry if it already exists.
    - delete() will remove the entry from the vault.
"""


def put_overwrite(key, value):
    db[key] = encrypt(value.encode('utf-8'), get_salt(key))

    with open(vault_file, 'wb') as outfile:
        pickle.dump(db, outfile)


def put(key, value):
    if key not in db:
        db[key] = encrypt(value.encode('utf-8'), get_salt(key))

        with open(vault_file, 'wb') as outfile:
            pickle.dump(db, outfile)

    else:
        print('\nError: Key already exists! Please use put_overwrite to overwrite.')


def get(key):
    if key in db:
        return decrypt(db[key], get_salt(key))

    else:
        print('\nKey not found!')


def prompt_put(key):
    if key not in db:
        value = getpass(f'\nPlease enter a value for {key}: ')
        put(key, value)

    else:
        print('\nError: Key already exists! Please use prompt_put_overwrite to overwrite.')


def prompt_put_overwrite(key):
    value = getpass(f'\nPlease enter a value for {key}: ')
    put_overwrite(key, value)


def delete(key):
    if key in db:
        del db[key]
        with open(vault_file, 'wb') as outfile:
            pickle.dump(db, outfile)

    else:
        print('\nKey not found!')


""" 
    The lines below will try to open the salt_file and passphrase_file, if they don't exist new ones will be created.
    In case a new passphrase is generated and a vault file already exists, the script will attempt to delete it.
    The old vault file is no longer usable if a new passphrase has been generated. 
"""

# Open or create salt file:
try:
    with open(saltseed_file, 'r') as infile:
        saltseed = infile.read()

    if len(saltseed) == 0:
        raise IOError

except (IOError, FileNotFoundError):
    with open(saltseed_file, 'w') as outfile:
        outfile.write(''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(salt_len)))

    os.chmod(saltseed_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP)  # Set file permissions.

    with open(saltseed_file, 'r') as infile:
        saltseed = infile.read()

# Open or create password file:
try:
    with open(passphrase_file, 'rb') as infile:
        passphrase = infile.read()

    if len(passphrase) == 0:
        raise IOError

    else:
        passphrase = base64.b64decode(passphrase)

except (IOError, FileNotFoundError):
    with open(passphrase_file, 'wb') as outfile:
        passphrase = os.urandom(passphrase_len)
        outfile.write(base64.b64encode(passphrase))

        try:
            os.remove(vault_file)  # Old vault is unusable if password has to be regenerated.

        except Exception:
            pass

        os.chmod(passphrase_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP)  # Set file permissions.

# Open or create vault:
try:
    with open(vault_file, 'rb') as infile:
        db = pickle.load(infile)

    if db == {}:
        raise IOError

except (IOError, EOFError):
    db = {}

    with open(vault_file, 'wb') as outfile:
        pickle.dump(db, outfile)
