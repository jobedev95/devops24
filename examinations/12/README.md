# Examination 12 - Roles

So far we have been using separate playbooks and ran them whenever we wanted to make
a specific change.

With Ansible [roles](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html) we
have the capability to organize tasks into sets, which are called roles.

These roles can then be used in a single playbook to perform the right tasks on each host.

Consider a playbook that looks like this:

    ---
    - name: Configure the web server(s) according to specs
      hosts: web
      roles:
        - webserver

    - name: Configure the database server(s) according to specs
      hosts: db
      roles:
        - dbserver

This playbook has two _plays_, each play utilizing a _role_.

This playbook is also included in this directory as [site.yml](site.yml).

Study the Ansible documentation about roles, and then start work on [QUESTION A](#question-a).

# QUESTION A

Considering the playbook above, create a role structure in your Ansible working directory
that implements the previous examinations as two separate roles; one for `webserver`
and one for `dbserver`.

Copy the `site.yml` playbook to be called `12-roles.yml`.

HINT: You can use

    $ ansible-galaxy role init [name]

to create a skeleton for a role. You won't need ALL the directories created by this,
but it gives you a starting point to fill out in case you don't want to start from scratch.

### ANSWER: 

I created a `roles` folder and ran the following commands to create the skeleton structure for each role:
```bash
ansible-galaxy role init webserver
ansible-galaxy role init dbserver
```

I also created third role manually, called ***base***, which will include tasks that should run on *all* hosts. I created the full path for `base/tasks/` and a `main.yml` file inside it. I then moved the playbook from examination 3 (which installs the base software onto all hosts) into that directory. I removed all playbook-level directives (such as hosts:, become:, vars_files: and tasks:) and only kept the task definitions.

In the `main.yml` file, I refer to the task file with:
```yaml
- name: Include installation of base software tasks
  ansible.builtin.import_tasks: 03-site.yml
```

I then moved the relevant playbooks from previous examinations into the `tasks` folder of their respective role. Depending on which host they targeted they were placed in either the dbserver or webserver role. I removed all playbook-level directives from each one and imported them using `import_tasks` in the `main.yml` file of both roles.

The dbserver `task/main.yml` file ended up looking like this:
```yaml
- name: Include installation and configuration of MariaDB tasks
  ansible.builtin.import_tasks: 09-mariadb-password.yml

- name: Include copying md files tasks
  ansible.builtin.import_tasks: 11-copy-md-files.yml
```

All related files were moved into the `files` directory of each role. The Jinja2 template file was moved to the `templates` directory of the webserver role.

The encrypted variable file `secrets.yml` was moved to the `vars` directory of the dbserver role, and the encrypted variable file `users.yml` file was moved to the `vars` directory of the webserver role. These were then included in the `tasks/main.yml` file of each role using the `include_vars` module. Below is an example of how it was included in the main file of the webserver role:
```yaml
- name: Include vaulted users
  ansible.builtin.include_vars: vars/users.yml
```

Since I added a third role, and the playbook-level instruction such as `become:true` had to be removed from the converted task files, the final `12-roles.yml` playbook had to be adjusted accordingly:
```yaml
---
- name: Configure base settings for all servers
  hosts: all
  become: true
  roles:
    - base

- name: Configure the web server(s) according to specs
  hosts: web
  become: true
  roles:
    - webserver

- name: Configure the database server(s) according to specs
  hosts: db
  become: true
  roles:
    - dbserver
```

Finally, I ran the playbook with:
```bash
ansible-playbook 12-roles.yml --vault-password-file files/vault-pass.txt
```