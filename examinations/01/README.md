# Examination 1 - Understanding SSH and public key authentication

Connect to one of the virtual lab machines through SSH, i.e.

    $ ssh -i deploy_key -l deploy webserver

Study the `.ssh` folder in the home directory of the `deploy` user:

    $ ls -ld ~/.ssh

Look at the contents of the `~/.ssh` directory:

    $ ls -la ~/.ssh/

## QUESTION A

What are the permissions of the `~/.ssh` directory?

### ANSWER:  
**Output:**
```bash
drwx------. 2 deploy deploy 29 Oct 13 10:42 /home/deploy/.ssh
```
The hidden directory `~/.ssh` has the permissions read, write and execute for the owner, which is the user ***deploy***.


Why are the permissions set in such a way?

### ANSWER:  
This directory contains sensitive information so security is of utmost concern. Both private ssh keys and `authorized_keys` are stored in this directory. To prevent unauthorized access these permissions ensures that only the owner can view or modify the contents and SSH-configuration. 

## QUESTION B

What does the file `~/.ssh/authorized_keys` contain?

### ANSWER:  
The file `authorized_keys` contains a list of public SSH keys that are allowed to access the system via SSH. When a SSH connection attempt is detected, the system first checks if the public key presented by the client matches any of the entries in this file. If there's a match access will be granted, with no password required.

## QUESTION C

When logged into one of the VMs, how can you connect to the other VM without a password?

### ANSWER
Initially the ***deploy*** user in the dbserver does not have a password. This will be required to copy the public key over from the webserver with the `ssh-copy-id` command. I connected to the dbserver from the host computer and added a password to the user to fix this problem:
```bash
sudo passwd deploy
```

Then I went back to the webserver and created new SSH-keys, which gets automatically stored in `~/.ssh/`:
```bash
ssh-keygen -t ed25519
```

Last step is to copy over the public key to dbserver. The command adds the public key to the `authorized_keys` file in dbserver:
```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub deploy@dbserver
```

After this I can SSH into dbserver without using a password:
```bash
ssh deploy@dbserver
```

### Hints:

* man ssh-keygen(1)
* ssh-copy-id(1) or use a text editor

## BONUS QUESTION

Can you run a command on a remote host via SSH? How?

### ANSWER:  
Yes, you simply use the standard ssh command but end it with the command you want to execute on the second server wrapped in quotation marks. This will not start an interactive SSH-session.
```bash
ssh deploy@dbserver 'ls -l /home/deploy'
```