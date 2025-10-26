# Examination 8 - MariaDB configuration

MariaDB and MySQL have the same origin (MariaDB is a fork of MySQL, because of... Oracle...
it's a long story.) They both work the same way, which makes it possible to use Ansible
collections that handle `mysql` to work with `mariadb`.

To be able to manage MariaDB/MySQL through the `community.mysql` collection, you also
need to make sure the requirements for the collections are installed on the database VM.

See https://docs.ansible.com/ansible/latest/collections/community/mysql/mysql_db_module.html#ansible-collections-community-mysql-mysql-db-module-requirements

HINT: In AlmaLinux, the correct package to install on the VM host is called ``.

# QUESTION A

Copy the playbook from examination 7 to `08-mariadb-config.yml`.

Use the `community.mysql` module in this playbook so that it also creates a database instance
called `webappdb` and a database user called `webappuser`.

Make the `webappuser` have the password "secretpassword" to access the database.

HINT: The `community.mysql` collection modules has many different ways to authenticate
users to the MariaDB/MySQL instance. Since we've just installed `mariadb` without setting
any root password, or securing the server in other ways, we can use the UNIX socket
to authenticate as root:

* The socket is located in `/var/lib/mysql/mysql.sock`
* Since we're authenticating through a socket, we should ignore the requirement for a `~/.my.cnf` file.
* For simplicity's sake, let's grant `ALL` privileges on `webapp.*` to `webappuser`

# Documentation and Examples
https://docs.ansible.com/ansible/latest/collections/community/mysql/index.html


### ANSWER:

I copied the playbook from examination 07, and added the following tasks:

```yaml
    - name: Install PyMySQL
      ansible.builtin.package:
        name: python3-PyMySQL
        state: present

    - name: Create a database called webappdb
      community.mysql.mysql_db:
        name: webappdb
        state: present
        login_unix_socket: /var/lib/mysql/mysql.sock

    - name: Create a database user called webappuser
      community.mysql.mysql_user:
        name: webappuser
        password: secretpassword
        priv: 'webappdb.*:ALL'
        state: present
        login_unix_socket: /var/lib/mysql/mysql.sock
```

The first task is to install the ***python3-PyMySQL*** package which is a required for the community.mysql module to work with the server. The following two tasks uses the community module to create a database called ***webappdb*** and a database user called ***webappuser***, which is granted all privileges. The socket connection lets Ansible log in to MariaDB locally as root without a password, which is required since no root password has been set yet.

After running the playbook I confirmed that every task was successful. The command `ansible db -m ansible.builtin.shell -a "mysql -u webappuser -psecretpassword -e 'SELECT DATABASE();' webappdb"` attempts to log in as webappuser and verify access to the webappdb database. It gave me the following output which confirms the database exists and can be accessed by the user:
```
DATABASE()
webappdb
```

Running the command `SHOW GRANTS FOR 'webappuser'@'localhost';` also confirms that webappuser has all privileges.