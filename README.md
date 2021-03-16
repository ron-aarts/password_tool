### Password Tool

## Description

This tool will encrypt passwords and store them in a pickle file. <b>Please use a real password vault product instead!</b>
This tool does not provide a cryptographically secure or foolproof method to store passwords.
It obfuscates plaintext passwords usage in your scripts.

When you import the password_tool for the first time it will create 3 files: 
 - .salt
 - .password
 - vault

.salt is a generated string which is used for the salt function. You can adjust the length by adjusting the salt_len variable.<br />
.password contains a generated password and is stored in base64 encoded format. You can adjust the length of the password by adjusting the passphrase_len variable.<br />
vault is the file containing the stored entries.<br />

## Usage of functions

put_overwrite() will encrypt the passed value and overwrite the entry if it already exists.<br />
put() will check if the entry already exists. If it does not exist it will encrypt and store the passed values.<br />
get() will retrieve the entry from the vault.<br />
prompt_put() will prompt the user to input a value, using getpass, instead of passing it directly.<br />
prompt_put_overwrite() does the same as prompt_put() but overwrites the entry if it already exists.<br />
delete() will remove the entry from the vault.<br />


## Code example

```
import password_tool


password_tool.put('example_key', 'this is a password')

password_tool.get('example_key')
'this is a password'


password_tool.put('another example key')
  Please enter a value for another example key:

password_tool.get('another example key')
'qwerty'


password_tool.delete('example_key')
```
<br />