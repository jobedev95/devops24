# Examination 13 - Handlers

In [Examination 5](../05/) we asked the question what the disadvantage is of restarting
a service every time a task is run, whether or not it's actually needed.

In order to minimize the amount of restarts and to enable a complex configuration to run
through all its steps before reloading or restarting anything, we can trigger a _handler_
to be run once when there is a notification of change.

Read up on [Ansible handlers](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_handlers.html)

In the previous examination ([Examination 12](../12/)), we changed the structure of the project to two separate
roles, `webserver` and `dbserver`.

# QUESTION A

Make the necessary changes to the `webserver` role, so that `nginx` only reloads when it's configuration
has changed in a task, such as when we have changed a `server` stanza.

Also note the difference between `restarted` and `reloaded` in the [ansible.builtin.service](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/service_module.html) module.

In order for `nginx` to pick up any configuration changes, it's enough to do a `reload` instead of
a full `restart`.



### ANSWER:

I removed the task that restarts nginx when the `result` variable is changed. Instead, I add a `notify:` directive to the task that should trigger a handler called ***Reload nginx***:
```yaml
- name: Deploy nginx configuration file
  ansible.builtin.template:
    src: templates/example.internal.conf.j2
    dest: /etc/nginx/conf.d/example.internal.conf
  register: result
  notify: Reload nginx
```
In the `handlers` directory of the webserver role I create a handler task file with the following handler to reload nginx:
```yaml
- name: Reload nginx
  ansible.builtin.service:
    name: nginx
    state: reloaded
```

In the `handlers/main.yml` file I import the handler task:
```yaml
- name: Include nginx reload handlers
  import_tasks: reload_nginx.yml
```

After that I can run the playbook as usual. The output clearly shows when then handler has been executed:
```bash
RUNNING HANDLER [webserver : Reload nginx] ***********************************************************************
changed: [192.168.121.206]
```