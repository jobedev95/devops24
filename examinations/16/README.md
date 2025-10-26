# Examination 16 - Security Compliance Check

The ever-present IT security team were not content with just having us put firewall rules
on our servers. They also want our servers to pass CIS certifications.

# QUESTION A

Implement _at least_ 10 of the checks in the [CIS Security Benchmark](https://www.cisecurity.org/benchmark/almalinuxos_linux) for AlmaLinux 10 and run them on the virtual machines.

These checks should be run by a playbook called `16-compliance-check.yml`.

*Important*: The playbook should only _check_ or _assert_ the compliance status, not perform any changes.

Use Ansible facts, modules, and "safe" commands. Here is an example:

    ---
    - name: Security Compliance Checks
      hosts: all
      tasks:
        - name: check for telnet-server
          ansible.builtin.command:
            cmd: rpm -q telnet-server
            warn: false
          register: result
          changed_when: result.stdout != "package telnet-server is not installed"
          failed_when: result.changed

Again, the playbook should make *no changes* to the servers, only report.

Often, there are more elegant and practical ways to assert compliance. The example above is
taken more or less verbatim from the CIS Security Benchmark suite, but it is often considered
bad practice to run arbitrary commands through [ansible.builtin.command] or [ansible.builtin.shell]
if you can avoid it.

In this case, you _can_ avoid it, by using the [ansible.builtin.package_facts](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/package_facts_module.html).

In conjunction with the [ansible.builtin.assert](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/assert_module.html) module you have a toolset to accomplish the same thing, only more efficiently and in an Ansible-best-practice way.

For instance:

    ---
    - name: Security Compliance Checks
      hosts: all
      tasks:
        - name: Gather the package facts
          ansible.builtin.package_facts:

        - name: check for telnet-server
          ansible.builtin.assert:
            fail_msg: telnet-server package is installed
            success_msg: telnet-server package is not installed
            that: "'telnet-server' not in ansible_facts.packages"

It is up to you to implement the solution you feel works best.


### ANSWER:
I picked out 10 of the CIS Benchmarks in the CIS AlmaLinux OS 10 PDF document and created compliant checks for them:
1. **Section 2.1.15** - Ensure telnet server services are not in use
2. **Section 4.1.1** - Ensure firewalld is installed
3. **Section 4.1.3** - Ensure firewalld.service is configured
4. **Section 1.3.1.5** - Ensure the SELinux mode is enforcing
5. **Section 2.2.1** - Ensure ftp client is not installed
6. **Section 2.1.12** - Ensure rsync services are not in use
7. **Section 2.3.2** - Ensure rsyslog service is enabled and active
8. **Section 5.1.20** - Ensure sshd PermitRootLogin is disabled
9. **Section 5.1.19** - Ensure sshd PermitEmptyPasswords is disabled
10. **Section 6.2.1.1** - Ensure journald service is active

I start the playbook with gathering facts about all installed packages and services of the target hosts. I also gather the contents of the SSHD configuration file with the `ansible.builtin.slurp` module and store it as a variable called `sshd_config`, since I will make some compliant checks on it as well:
```yaml
- name: Gather package facts
  ansible.builtin.package_facts:

- name: Gather service facts
  ansible.builtin.service_facts:

- name: Gather SSHD configuration
  ansible.builtin.slurp:
    src: /etc/ssh/sshd_config
  register: sshd_config
```

With the `ansible.builtin.assert` module I can now check if a certain package is installed. Below I evaluate if `firewalld` is installed to see if the target hosts are compliant with Section 4.1.1 of CIS AlmaLinux OS 10. If compliant the `success_msg` will be displayed, if non-compliant the `fail_msg` will be displayed. 

The parameter `ignore_errors: true` on each task ensures that the playbook will continue on with further compliant checks even when one fails. An alternative to this would be to have `failed_when: false`, which marks a task as “ok” even if the condition for failure has been met, this in turn will result in the fail message appearing in green color.
```yaml
- name: Check firewalld is installed
  ansible.builtin.assert:
    that: "'firewalld' in ansible_facts.packages"
    success_msg: "firewalld is installed"
    fail_msg: "firewalld is not installed"
  ignore_errors: true
```

With the same module I can also check the status of a service. In this example I check to see if the rsyslog service is running and enabled on the target host to be compliant with Section 2.3.2 of CIS AlmaLinux OS 10:
```yaml
- name: Check rsyslog service state
  ansible.builtin.assert:
    that:
      - ansible_facts.services['rsyslog.service'].state == 'running'
      - ansible_facts.services['rsyslog.service'].status == 'enabled'
    success_msg: "rsyslog is running and enabled"
    fail_msg: "rsyslog is not running or disabled"
  ignore_errors: true
```

With the assert module I can also check the contents of a gathered file. To be compliant with Section 5.1.20 of CIS AlmaLinux 10 I check if the `/etc/ssh/sshd_config` file has been configured with `PermitRootLogin no`. It uses b64decode to decode the contents of the variable since the slurp module gathers the content in base64 format.
```yaml
- name: Check SSH PermitRootLogin setting
  ansible.builtin.assert:
    that: "'PermitRootLogin no' in (sshd_config.content | b64decode)"
    success_msg: "SSH root login disabled"
    fail_msg: "SSH root login enabled"
  ignore_errors: true
```

When running the playbook, some of the compliant checks succeeds. For example, this one confirms that the rsyslog service is running and therefore compliant:
```bash
TASK [Check rsyslog service state] ****************************************************************************************************************************************
ok: [192.168.121.217] => {
    "changed": false,
    "msg": "rsyslog is running and enabled"
}
ok: [192.168.121.206] => {
    "changed": false,
    "msg": "rsyslog is running and enabled"
}
```

But some compliant checks fails. The following failure tells me that root login is currently allowed via SSH on both target hosts:
```bash
TASK [Check SSH PermitRootLogin setting] **********************************************************************************************************************************
fatal: [192.168.121.217]: FAILED! => {
    "assertion": "'PermitRootLogin no' in (sshd_config.content | b64decode)",
    "changed": false,
    "evaluated_to": false,
    "msg": "SSH root login enabled"
}
...ignoring
fatal: [192.168.121.206]: FAILED! => {
    "assertion": "'PermitRootLogin no' in (sshd_config.content | b64decode)",
    "changed": false,
    "evaluated_to": false,
    "msg": "SSH root login enabled"
}
...ignoring
```

# BONUS QUESTION

If you implement these tasks within one or more roles, you will gain enlightenment and additional karma.

### ANSWER: 
I created a role called `cis_compliance`, with a `tasks` directory and a `main.yml` file inside it together with a copy of the `16-compliance-check.yml` (but converted into tasks only). The `main.yml` file then imports the tasks with `ansible.builtin.import_tasks: 16-compliance-check.yml`.

I then created a playbook called `16-bonus.yml` that runs the `cis_compliance` role on all hosts:
```yaml
---
- name: Run CIS compliance checks on all hosts
  hosts: all
  become: true
  roles:
    - cis_compliance
```

# Resources

For inspiration and as an example of an advanced project using Ansible for this, see for instance
https://github.com/ansible-lockdown/RHEL10-CIS. Do *NOT*, however, try to run this compliance check
on your virtual (or physical) machines. It will likely have unintended consequences, and may render
your operating system and/or virtual machine unreachable.