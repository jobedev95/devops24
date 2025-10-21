# Examination 14 - Firewalls (VG)

The IT security team has noticed that we do not have any firewalls enabled on the servers,
and thus ITSEC surmises that the servers are vulnerable to intruders and malware.

As a first step to appeasing them, we will install and enable `firewalld` and
enable the services needed for connecting to the web server(s) and the database server(s).

# QUESTION A

Create a playbook `14-firewall.yml` that utilizes the [ansible.posix.firewalld](https://docs.ansible.com/ansible/latest/collections/ansible/posix/firewalld_module.html) module to enable the following services in firewalld:

* On the webserver(s), `http` and `https`
* On the database servers(s), the `mysql`

You will need to install `firewalld` and `python3-firewall`, and you will need to enable
the `firewalld` service and have it running on all servers.

When the playbook is run, you should be able to do the following on each of the
servers:

## dbserver

    [deploy@dbserver ~]$ sudo cat /etc/firewalld/zones/public.xml
    <?xml version="1.0" encoding="utf-8"?>
    <zone>
      <short>Public</short>
      <description>For use in public areas. You do not trust the other computers on networks to not harm your computer. Only selected incoming connections are accepted.</description>
      <service name="ssh"/>
      <service name="dhcpv6-client"/>
      <service name="cockpit"/>
      <service name="mysql"/>
    <forward/>
    </zone>

## webserver

    [deploy@webserver ~]$ sudo cat /etc/firewalld/zones/public.xml
    <?xml version="1.0" encoding="utf-8"?>
    <zone>
      <short>Public</short>
      <description>For use in public areas. You do not trust the other computers on networks to not harm your computer. Only selected incoming connections are accepted.</description>
      <service name="ssh"/>
      <service name="dhcpv6-client"/>
      <service name="cockpit"/>
      <service name="https"/>
      <service name="http"/>
      <forward/>
    </zone>

# Resources and Documentation

https://firewalld.org/

### ANSWER:

I first created a task that installs `firewalld` and `python3-firewall`. I then have a task that enables and starts the `firewalld` service. Both tasks apply on both servers.
```yaml
---
- name: Configure firewalld on all servers
  hosts: all
  become: true
  tasks:
    - name: Ensure firewalld and python3-firewall are installed
      ansible.builtin.package:
        name:
          - firewalld
          - python3-firewall
        state: present

    - name: Enable and start firewalld service
      ansible.builtin.service:
        name: firewalld
        state: started
        enabled: true
```

I then created a task that configures the firewall on the webserver. It enables the HTTP and HTTPS services in firewalld:
```yaml
- name: Configure firewall on webserver
  hosts: web
  become: true
  tasks:
    - name: Enable HTTP and HTTPS services in firewalld
      ansible.posix.firewalld:
        service: "{{ item }}"
        permanent: true # Ensures the configuration stays after reboots
        state: enabled
        immediate: true # Applies without restarting firewalld
      loop:
        - http
        - https
```

Lastly I created a task that configures the firewall on the dbserver. It enables the MySQL in firewalld:
```yaml
- name: Configure firewall on dbserver
  hosts: db
  become: true
  tasks:
    - name: Enable MySQL service in firewalld
      ansible.posix.firewalld:
        service: mysql
        permanent: true # Ensures the configuration stays after reboots
        state: enabled
        immediate: true # Applies without restarting firewalld
```

To confirm that all firewall configurations were successful I ran the command `sudo cat /etc/firewalld/zones/public.xml` on both servers which gave me identical outputs as the examples given in the examination.