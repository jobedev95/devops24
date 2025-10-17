# Examination 7 - MariaDB installation

To make a dynamic web site, many use an SQL server to store the data for the web site.

[MariaDB](https://mariadb.org/) is an open-source relational SQL database that is good
to use for our purposes.

We can use a similar strategy as with the _nginx_ web server to install this
software onto the correct host(s). Create the playbook `07-mariadb.yml` with this content:

    ---
    - hosts: db
      become: true
      tasks:
        - name: Ensure MariaDB-server is installed.
          ansible.builtin.package:
            name: mariadb-server
            state: present

# QUESTION A

Make similar changes to this playbook that we did for the _nginx_ server, so that
the `mariadb` service starts automatically at boot, and is started when the playbook
is run.

### ANSWER:

I added this simple task using the `ansible.builtin.service` module to ensure the service starts when the playbook is run with `state: started`, and is started automatically at boot with `enabled: yes`:
```yaml
    - name: Ensure MariaDB service is enabled and started
      ansible.builtin.service:
        name: mariadb
        state: started
        enabled: yes
```

# QUESTION B

When you have run the playbook above successfully, how can you verify that the `mariadb`
service is started and is running?

### ANSWER:

I can run the command `systemctl status mariadb` inside the db-server to see if mariadb is active and running. Alternatively I can run: `ansible db -m ansible.builtin.shell -a "systemctl status mariadb`, which will return the same information.

# BONUS QUESTION

How many different ways can use come up with to verify that the `mariadb` service is running?

### ANSWER: 

There are multiple ways to verify if the mariadb service is running. Below are three of the available methods:

I can use `ansible db -m service_facts` to get a list of all current services in the server and their status.

I can run `ansible db -m ansible.builtin.command -a "systemctl is-active mariadb` to get a short output stating if the service is running or not.

The command `ps aux | grep mariadb` will show if the mariadb process is running. Can also be run via the ansible.builtin.shell command.

