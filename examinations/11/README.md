# Examination 11 - Loops

Imagine that on the web server(s), the IT department wants a number of users accounts set up:

    alovelace
    aturing
    edijkstra
    ghopper

These requirements are also requests:

* `alovelace` and `ghopper` should be added to the `wheel` group.
* `aturing` should be added to the `tape` group
* `edijkstra` should be added to the `tcpdump` group.
* `alovelace` should be added to the `audio` and `video` groups.
* `ghopper` should be in the `audio` group, but not in the `video` group.

Also, the IT department, for some unknown reason, wants to copy a number of '\*.md' files
to the 'deploy' user's home directory on the `db` machine(s).

I recommend you use two different playbooks for these two tasks. Prefix them both with `11-` to
make it easy to see which examination it belongs to.

# QUESTION A

Write a playbook that uses loops to add these users, and adds them to their respective groups.

When your playbook is run, one should be able to do this on the webserver:

    [deploy@webserver ~]$ groups alovelace
    alovelace : alovelace wheel video audio
    [deploy@webserver ~]$ groups aturing
    aturing : aturing tape
    [deploy@webserver ~]$ groups edijkstra
    edijkstra : edijkstra tcpdump
    [deploy@webserver ~]$ groups ghopper
    ghopper : ghopper wheel audio

There are multiple ways to accomplish this, but keep in mind _idempotency_ and _maintainability_.

### ANSWER:

I created a separate `users.yml` file inside the `/vars` directory containing the list of all users and the groups they belong to. I did this to declutter the playbook itself and because it is best practice for maintainability.

```yaml
---
users:
  - username: alovelace
    groups: ["wheel", "video", "audio"]

  - username: aturing
    groups: ["tape"]

  - username: edijkstra
    groups: ["tcpdump"]

  - username: ghopper
    groups: ["wheel", "audio"]
```

Inside the playbook I import the `vars/users.yml` file. The task then uses the `ansible.builtin.user` module to create the users. The task uses a loop that goes through each user and its items in the `users.yml` file.

Each item can then be referenced to in every loop. `{{ item.username }}` fetches the username of the user for example.

```yaml
---
- name: Create user accounts on web server
  hosts: web
  become: true

  vars_files:
    - vars/users.yml

  tasks:
    - name: Ensure users are present with correct groups
      ansible.builtin.user:
        name: "{{ item.username }}"
        groups: "{{ item.groups | join(',') }}"
        append: yes
        state: present
      loop: "{{ users }}"
```

# QUESTION B

Write a playbook that uses

    with_fileglob: 'files/*.md5'

to copy all `\*.md` files in the `files/` directory to the `deploy` user's directory on the `db` server(s).

For now you can create empty files in the `files/` directory called anything as long as the suffix is `.md`:

    $ touch files/foo.md files/bar.md files/baz.md

### ANSWER: 

I used the `ansible.builtin.copy` module to copy the markdown files to the home directory of the user ***deploy*** in the db server. I then added the task directive `with_fileglob:` to instruct the task to run the task for each file with the `.md` extension. The `src` parameter is then set to `{{ item }}`, which represents the current file in the loop.
```yaml
---
- name: Copy Markdown files to deploys home directory on db server
  hosts: db
  become: true

  tasks:
    - name: Copy all Markdown files to deploys home directory
      ansible.builtin.copy:
        src: "{{ item }}"
        dest: "/home/deploy/"
        owner: deploy
        group: deploy
        mode: '0644'
      with_fileglob:
        - "files/*.md"
```


# BONUS QUESTION

Add a password to each user added to the playbook that creates the users. Do not write passwords in plain
text in the playbook, but use the password hash, or encrypt the passwords using `ansible-vault`.

There are various utilities that can output hashed passwords, check the FAQ for some pointers.

### ANSWER: 

I added a password field for each user in the `vars/users.yml` file. Every password is piped to the `password_hash('sha512')` filter, which generates a SHA-512 hash of the password. I then encrypted the command `users.yml` file with `ansible-vault encrypt users.yml`.
```yaml
---
users:
  - username: alovelace
    groups: ["wheel", "video", "audio"]
    password: "{{ 'testpassword' | password_hash('sha512') }}"

  - username: aturing
    groups: ["tape"]
    password: "{{ 'testpassword' | password_hash('sha512') }}"
[...]
```

In the playbook I added the password parameter `password: "{{ item.password }}"`. Another adjustment I made in the playbook was to add the parameter `no_log: true` to prevent hashed passwords from being displayed in the task output log when the playbook runs.

>One thing to note here is that new password hashes are created on each run, which breaks the idempotency. Static pre-hashed passwords or a fixed salt would solve the issue, but would also be less secure.
```yaml
---
- name: Create user accounts on web server
  hosts: web
  become: true

  vars_files:
    - vars/users.yml

  tasks:
    - name: Ensure users are present with correct groups and passwords
      ansible.builtin.user:
        name: "{{ item.username }}"
        groups: "{{ item.groups | join(',') }}"
        append: yes
        state: present
        password: "{{ item.password }}"
      loop: "{{ users }}"
      no_log: true # Hide hashed passwords from output
```

# BONUS BONUS QUESTION

Add the real names of the users we added earlier to the GECOS field of each account. Google is your friend.

### ANSWER: 

I first added a gecos field for each user in the `users.yaml` file.
```yaml
---
users:
  - username: alovelace
    groups: ["wheel", "video", "audio"]
    gecos: "Ada Lovelace"
    password: "{{ 'testpassword' | password_hash('sha512') }}"
[...]
```

I then added the parameter `comment: "{{ item.gecos }}"` inside the task in the playbook.
```yaml
---
- name: Create user accounts on web server
  hosts: web
  become: true

  vars_files:
    - vars/users.yml

  tasks:
    - name: Ensure users are present with correct groups, passwords and info
      ansible.builtin.user:
        name: "{{ item.username }}"
        groups: "{{ item.groups | join(',') }}"
        append: yes
        state: present
        password: "{{ item.password }}"
        comment: "{{ item.gecos }}"
      loop: "{{ users }}"
      no_log: true # Hide hashed passwords from output
```

# Resources and Documentation

* [loops](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_loops.html)
* [ansible.builtin.user](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/user_module.html)
* [ansible.builtin.fileglob](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/fileglob_lookup.html)
* https://docs.ansible.com/ansible/latest/reference_appendices/faq.html#how-do-i-generate-encrypted-passwords-for-the-user-module

