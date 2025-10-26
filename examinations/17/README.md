# Examination 17 - sudo rules

In real life, passwordless sudo rules is a security concern. Most of the time, we want
to protect the switching of user identity through a password.

# QUESTION A

Create an Ansible role or playbook to remove the passwordless `sudo` rule for the `deploy`
user on your machines, but create a `sudo` rule to still be able to use `sudo` for everything,
but be required to enter a password.

On each virtual machine, the `deploy` user got its passwordless `sudo` rule from the Vagrant
bootstrap script, which placed it in `/etc/sudoers.d/deploy`.

Your solution should be able to have `deploy` connect to the host, make the change, and afterwards
be able to `sudo`, only this time with a password.

To be clear; we want to make sure that at no point should the `deploy` user be completely without
the ability to use `sudo`, since then we're pretty much locked out of our machines (save for using
Vagrant to connect to he machine and fix the problem).

*Tip*: Check out _validate_ in [ansible.builtin.lineinfile](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/lineinfile_module.html) to ensure a file can be parsed correctly (such as running `visudo --check`)
before being changed.

No password is set for the `deploy` user, so begin by setting the password to `hunter12`.

HINT: To construct a password hash (such as one for use in [ansible.builtin.user](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/user_module.html), you can use the following command:

    $ openssl passwd -6 hunter12

This will give you a SHA512 password hash that you can use in the `password:` field.

You can verify this by trying to login to any of the nodes without the SSH key, but using the password
provided instead.

To be able to use the password when running the playbooks later, you must use the `--ask-become-pass`
option to `ansible` and `ansible-playbook` to provide the password. You can also place the password
in a file, like with `ansible-vault`, or have it encrypted via `ansible-vault`.




### ANSWER:

I created a vaulted password and named it `deploy_pass`. This is to be used as a vaulted inline variable inside the playbook:
```bash
ansible-vault encrypt_string --vault-password-file ../vault-pass.txt 'hunter12' --name 'deploy_pass'
Encryption successful
deploy_pass: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          38656234373265646463326232373263336363373039626466336230373661613736616165636337
          3236663663316665363534383861633531643936333731610a636165663064636433343937653332
          66383636373039313666626239663839346561326531363833656461363430303365626364393336
          6135346563663565390a383465376162393439336337376432336662353061306161666165613266
          3866
```

In the playbook I have three tasks. The first is to gather all entries from the shadow file, which should contain all the hashed passwords of all users in the target host. This is done so that the next task can check if a specific user has a password set or not. The entries gets stored inside the `ansible_facts` dictionary as a nested dictionary called `getent_shadow`.
```yaml
- name: Gather shadow entries
  ansible.builtin.getent:
    database: shadow
```

The second task sets a new password for the user ***deploy*** if it doesn't have a password set yet. The aim is to make the playbook idempotent instead of setting a new password for the user every time it is run. The decrypted `deploy_pass` variable gets hashed with `password_hash('sha512')` before being set.

To determine if a password has already been set, the task goes through the previously gathered shadow entries, stored under `ansible_facts.getent_shadow`. By inspecting the first field of the user `deploy[0]`, which is the hashed password field, it can detect whether it´s empty `''` or locked/disabled `'!', '*'`.
```yaml
- name: Ensure deploy user has password if not set
  ansible.builtin.user:
    name: deploy
    password: "{{ deploy_pass | string | password_hash('sha512') }}"
  when: ansible_facts.getent_shadow.deploy[0] in ['', '!', '*']
```

Before creating the third task I inspected the sudoers file for the ***deploy*** user in `/etc/sudoers.d/deploy`. The configuration contained the *NOPASSWD* option, which meant passwordless sudo was allowed for the user:
```bash
%deploy ALL=(ALL) NOPASSWD: ALL
```

So I created a third task that changes the configuration by using the `ansible.builtin.lineinfile` module. It uses regex to find a line that matches the pattern `"^%?deploy.*NOPASSWD: ALL"`, which is a line that starts with `%deploy` or `deploy` and contains `NOPASSWD: ALL`. If a match is found it replaces the line with `deploy ALL=(ALL) ALL`, which disables passwordless sudo. The last parameter of the task validates the syntax before applying any of the changes with `visudo`, which is done to make sure the sudoers file does not become corrupted:
```yaml
- name: Remove passwordless sudo (NOPASSWD) and enforce password requirement
  ansible.builtin.lineinfile:
    path: /etc/sudoers.d/deploy
    regexp: "^%?deploy.*NOPASSWD: ALL"
    line: "deploy ALL=(ALL) ALL"
    validate: "visudo -cf %s" # Validates the file
```

After running the playbook the configuration ended up with the correct options set:
```bash
deploy ALL=(ALL) ALL
```