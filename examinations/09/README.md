# Examination 9 - Use Ansible Vault for sensitive information

In the previous examination we set a password for the `webappuser`. To keep this password
in plain text in a playbook, or otherwise, is a huge security hole, especially
if we publish it to a public place like GitHub.

There is a way to keep sensitive information encrypted and unlocked at runtime with the
`ansible-vault` tool that comes with Ansible.

https://docs.ansible.com/ansible/latest/vault_guide/index.html

*IMPORTANT*: Keep a copy of the password for _unlocking_ the vault in plain text, so that
I can run the playbook without having to ask you for the password.

# QUESTION A

Make a copy of the playbook from the previous examination, call it `09-mariadb-password.yml`
and modify it so that the task that sets the password is injected via an Ansible variable,
instead of as a plain text string in the playbook.

### ANSWER: 

I first created a YAML file called ***secrets.yml*** containing a variable with the db-server password:
```yaml
---
db_password: "secretpassword"
```

After I created the file I added the path to the it at the playbook level using the `vars_files` parameter:
```yaml
  vars_files:
    - vars/secrets.yml
```
Lastly I refer to the variable containing the password (in the task that's creating the database):
```yaml
password: "{{ db_password }}"
```

With this setup, the playbook will automatically fetch the variable containing the password from the secrets.yml file, meaning it does not have to store the password in plain text. However the YAML file containing the variable still contains the password in plain text.


# QUESTION B

When the [QUESTION A](#question-a) is solved, use `ansible-vault` to store the password in encrypted
form, and make it possible to run the playbook as before, but with the password as an
Ansible Vault secret instead.

### ANSWER:

I encrypted the file with the following command and gave it the password "secrettest":
```bash
ansible-vault encrypt vars/secrets.yml
```

To run the playbook I can either run this command and then enter my password interactively:
```bash
ansible-playbook 09-mariadb-password.yml --ask-vault-pass
```

Or I can run the playbook while referring to a separate file which contains the vault password in plain text:
```bash
ansible-playbook 09-mariadb-password.yml --vault-password-file files/vault-pass.txt
```

To make it even better I can add the path to the file containing the vault password in the ansible config file:
```conf
[defaults]
vault_password_file = files/vault-pass.txt
```

Now I can run the playbook as normal without any flags.