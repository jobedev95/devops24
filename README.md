# devops24
DEVOPS24 Git Repo

## Lab Environment

This repo contains a directory (`lab_environment`) with a Vagrantfile to serve as the basis
of your lab environment.

To use it, you need:

* A Linux host that runs libvirt/qemu
* Vagrant

Depending on your distribution, you might need to install these components in different ways.

See https://vagrant-libvirt.github.io/vagrant-libvirt/ for more details.

### Debian/Ubuntu/Kali Linux

On Debian/Ubuntu/Kali Linux, you can probably do

    $ sudo apt install qemu-system-common vagrant
    $ sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virtinst virt-manager

In order to properly install `vagrant`, at least on Ubuntu and Debian, you might need to add
an extra `.deb` repository as described on the HashiCorp Vagrant pages:

* https://developer.hashicorp.com/vagrant/install#linux

It should be enough to copy and paste the instructions there, and then run

    $ sudo apt install vagrant

### Fedora/Red Hat/CentOS/Rocky Linux

On Fedora/Red Hat, you can probably do

    $ sudo dnf install vagrant-libvirt
    $ sudo dnf install @vagrant

See https://developer.fedoraproject.org/tools/vagrant/vagrant-libvirt.html

Afterwards, you can check if you have the necessary services running by

    $ sudo systemctl status libvirtd | grep enabled
     Loaded: loaded (/usr/lib/systemd/system/libvirtd.service; enabled; preset: disabled)
    $ lsmod | grep kvm
    kvm_intel             421888  0
    kvm                  1241088  1 kvm_intel
    irqbypass              12288  1 kvm

Details of the output may differ between distributions, but the important thing is the modules are loaded.

### Running the lab environment

    $ cd [this directory]
    $ vagrant up

This should give you two VM:s; 'webserver' and 'dbserver' which are now ready to be used as lab environment.

## Links and Resources for learning Ansible

* [Ansible Community Documentation](https://docs.ansible.com/)
* [Learning Ansible Basics](https://www.redhat.com/en/topics/automation/learning-ansible-tutorial) (RedHat)
* [The Ansible Playbook](https://www.youtube.com/@AnsibleAutomation) (YouTube)
