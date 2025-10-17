# Examination 10 - Templating

With the installation of the web server earlier in Examination 6, we set up
the `nginx` web server with a static configuration file that listened to all
interfaces on the (virtual) machine.

What we really want is for the webserver to _only_ listen to the external
interface, i.e. the interface with the IP address that we connect to the machine to.

Of course, we can statically enter the IP address into the file and upload it,
but if the IP address of the machine changes, we have to do it again, and if the
playbook is meant to be run against many different web servers, we have to be able
to do this manually.

Make a directory called `templates/` and put the `nginx` configuration file from Examination 6
into that directory, and call it `example.internal.conf.j2`.

If you look at the `nginx` documentation, note that you don't have to enable any IPv6 interfaces
on the web server. Stick to IPv4 for now.

# QUESTION A

Copy the finished playbook from Examination 6 (`06-web.yml`) and call it `10-web-template.yml`.

Make the static configuration file we used earlier into a Jinja template file,
and set the values for the `listen` parameters to include the external IP
address of the virtual machine itself.

Use the `ansible.builtin.template` module to accomplish this task.

# Resources and Documentation

* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/template_module.html
* https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html
* https://nginx.org/en/docs/http/ngx_http_core_module.html#listen



### ANSWER:

I turned the old Nginx configuration file into a Jinja template and replaced the static listen values with Jinja2 variables:
```diff
-    listen 80;
-    listen 443 ssl;
+    listen {{ ansible_default_ipv4.address }}:80;
+    listen {{ ansible_default_ipv4.address }}:443 ssl;
```

I removed the previous task that used the `ansible.builtin.copy` module, which copied the Nginx configuration file to the web server as-is. The new task instead uses the `ansible.builtin.template` module, which dynamically inserts the hosts default IPv4 address using the Jinja2 template:
```yml
    - name: Deploy example.internal.conf 
      ansible.builtin.template:
        src: templates/example.internal.conf.j2
        dest: /etc/nginx/conf.d/example.internal.conf
      register: result
```

I could then verify the change by running the following command on the host:
```bash
grep listen /etc/nginx/conf.d/example.internal.conf
```
It gave me this output which confirms the change:
```
listen 192.168.121.206:80;
listen 192.168.121.206:443 ssl;
```

---
**Below is the full playbook:**
```yaml
- name: Copy HTTPS Nginx configuration
  hosts: web
  become: true
  tasks:
    - name: Copy https.conf to Nginx configuration directory
      ansible.builtin.copy:
        src: https.conf
        dest: /etc/nginx/conf.d/https.conf
        owner: root
        group: root
        mode: '0644'
    - name: Create web root directory
      ansible.builtin.file:
        path: /var/www/example.internal/html/
        state: directory
        mode: '0755'
    - name: Copy index.html to html directory
      ansible.builtin.copy:
        src: files/index.html
        dest: /var/www/example.internal/html/
    - name: Deploy Nginx configuration file
      ansible.builtin.template:
        src: templates/example.internal.conf.j2
        dest: /etc/nginx/conf.d/example.internal.conf
      register: result
    - name: Print result
      ansible.builtin.debug:
        var: result
    - name: Restart nginx service
      ansible.builtin.service:
         name: nginx
         state: restarted
      when: result is changed
````