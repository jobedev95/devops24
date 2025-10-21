# Examination 15 - Metrics (VG)

[Prometheus](https://prometheus.io/) is a powerful application used for event monitoring and alerting.

[Node Exporter](https://prometheus.io/docs/guides/node-exporter/) collects metrics for Prometheus from
the hardware and the kernel on a machine (virtual or not).

Start by running the Prometheus server and a Node Exporter in containers on your Ansible controller
(the you're running Ansible playbooks from). This can be accomplished with the [prometheus.yml](prometheus.yml)
playbook.

You may need to install [podman](https://podman.io/docs/installation) first.

If everything worked correctly, you should see the data exported from Node Exporter on http://localhost:9090/,
and you can browse this page in a web browser.

# QUESTION A

Make an Ansible playbook, `15-node_exporter.yml` that installs [Node Exporter](https://prometheus.io/download/#node_exporter)
on each of the VMs to export/expose metrics to Prometheus.

Node exporter should be running as a `systemd` service on each of the virtual machines, and
start automatically at boot.

You can find `systemd` unit files that you can use [here](https://github.com/prometheus/node_exporter/tree/master/examples/systemd), along with the requirements regarding users and permissions.

Consider the requirements carefully, and use Ansible modules to create the user, directories, copy files,
etc.

Also, consider the firewall configuration we implemented earlier, and make sure we can talk to the node
exporter port.

HINT: To get the `firewalld` service names available in `firewalld`, you can use

    $ firewall-cmd --get-services

on the `firewalld`-enabled hosts.

Note also that while running the `podman` containers on your host, you may sometimes need to stop and
start them.

    $ podman pod stop prometheus

and

    $ podman pod start prometheus

will get you on the right track, for instance if you've changed any of the Prometheus configuration.

# Resources and Information

* https://github.com/prometheus/node_exporter/tree/master/examples/systemd
* https://prometheus.io/docs/guides/node-exporter/



### ANSWER:

I first installed podman:
```bash
sudo apt install podman
```

I then configured the prometheus scrape targets:
```yaml
- targets:
    - 'node-exporter:9100'
    - '192.168.121.206:9100' # Webserver
    - '192.168.121.217:9100' # Dbserver
```

I then ran the `prometheus.yml` file, which sets up the Prometheus configuration YAML file and the pod with the two containers ***prometheus*** and ***node-exporter***.
```yaml
ansible-playbook prometheus.yml
```

Visiting http://localhost:9090/ in the host computer confirms that Prometheus is running correctly. It also shows that the ***controller*** scrape target status is "Up" (which is the node-exporter container). This indicates that Prometheus successfully connected and scraped metrics from that endpoint. However, the status for the two servers are down, as Node Exporter needs to be installed and configured on them before Prometheus can scrape any metrics from those targets.

In the playbook I created several tasks. The first one was to create the system user ***node_exporter***. I used the `shell: /sbin/nologin ` parameter which prevents anyone from logging in interactively as the user. I also define it as a system user with parameter `system: true`.
```yaml
- name: Ensure node_exporter user exists
    ansible.builtin.user:
      name: "node_exporter"
      shell: /sbin/nologin
      system: true
      create_home: false
```

At the playbook level I have defined a variable which sets the version of Node Exporter to be downloaded. Current version is 1.9.1:
```yaml
vars:
    node_exporter_version: "1.9.1"
```
I have two tasks that uses the `ansible.builtin.get_url` and `ansible.builtin.unarchive` modules respectively to download and extract Node Exporter to `/tmp`. A third task then copies the Node Exporter binary into the directory `/usr/sbin/node_exporter`:
```yaml
- name: Download Node Exporter archive to temporary folder
      ansible.builtin.get_url:
        url: "https://github.com/prometheus/node_exporter/releases/download/v{{ node_exporter_version }}/node_exporter-{{ node_exporter_version }}.linux-amd64.tar.gz"
        dest: /tmp/node_exporter.tar.gz
        mode: "0644"

    - name: Extract Node Exporter binary
      ansible.builtin.unarchive:
        src: /tmp/node_exporter.tar.gz
        dest: /tmp/
        remote_src: true # Informs Ansible that the archive file is on the remote host

    - name: Copy Node Exporter binary to /usr/sbin/node_exporter
      ansible.builtin.copy:
        src: "/tmp/node_exporter-{{ node_exporter_version }}.linux-amd64/node_exporter"
        dest: /usr/sbin/node_exporter
        owner: node_exporter
        group: node_exporter
        mode: "0755"
        remote_src: true # Informs Ansible that the binary file is on the remote host
```

I downloaded the service unit files `node_exporter.service` and `node_exporter.socket`, as well as the configuration file `sysconfig.node_exporter` from the provided GitHub link. I created three tasks in accordance with the instructions in the README file.

- The first creates the directory `/var/lib/node_exporter/textfile_collector`, which is used by Node Exporter to read custom metric files

- The second copies the `node_exporter.service` and `node_exporter.socket` files into `/etc/systemd/system/`. It also notifies a handler called ***Reload systemd***, which reloads systemd to re-scan and load the new unit files. The service file defines how the service runs while the socket file defines the socket activation behavior.

- The third copies the `sysconfig.node_exporter` configuration file into `/etc/sysconfig/node_exporter`. This configures the startup options and flags used by systemd.

```yaml
- name: Create textfile collector directory
  ansible.builtin.file:
    path: /var/lib/node_exporter/textfile_collector
    state: directory
    owner: node_exporter
    group: node_exporter
    mode: '0755'

- name: Copy Node Exporter systemd service and socket files
  ansible.builtin.copy:
    src: "files/{{ item }}"
    dest: /etc/systemd/system/
    mode: "0644"
  loop:
    - node_exporter.service
    - node_exporter.socket
  notify: Reload systemd

- name: Copy sysconfig file
  ansible.builtin.copy:
    src: files/sysconfig.node_exporter
    dest: /etc/sysconfig/node_exporter
    mode: "0644"
```

Below is the handler I created which reloads systemd when notified by the above task:
```yaml
handlers:
  - name: Reload systemd
    ansible.builtin.systemd:
      daemon_reload: true
```

Next task simply starts and enables the Node Exporter socket. It does not enable or start the actual Node Exporter service, since it´s a socket-activated service which gets triggered whenever a connection is made to TCP port 9100:
```yaml
- name: Start and enable the Node Exporter socket
  ansible.builtin.systemd:
    name: node_exporter.socket
    enabled: true
    state: started
```

Before creating the firewall task I ran the command `firewall-cmd --get-services` to see all available predefined firewalld services that can be enabled. I found one called `prometheus-node-exporter`, which is a predefined firewalld service for Node Exporter that opens TCP port 9100. I created a task to enable the service in firewalld:
```yaml
- name: Enable Node Exporter service in firewalld
  ansible.posix.firewalld:
    service: prometheus-node-exporter # Opens TCP port 9100 in the firewall
    permanent: true
    state: enabled
    immediate: true
```

Refreshing the Prometheus UI on http://localhost:9090/ now shows all three scrape targets with the status "Up". 

Running the command ```sudo systemctl status node_exporter.socket``` on both servers also shows that the node exporter socket is both active and enabled.