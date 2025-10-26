#!/usr/bin/env python3

from ansible.module_utils.basic import AnsibleModule

def main():

    # Creates Ansible Module object that defines what arguments it expects
    module = AnsibleModule(
        argument_spec=dict(
            message=dict(type='str', required=True)
        ),
        supports_check_mode=True
    )

    # Get the users message string input
    message = module.params['message']

    # Reverse the string
    reversed_message = message[::-1]

    # Determine changed state
    if message != reversed_message:
        changed = True
    else:
        changed = False

    # Handle explicit failure
    if message == "fail me":
        module.fail_json(
            msg="You requested this to fail",
            changed=True,
            original_message=message,
            reversed_message=reversed_message,
        )

    # Handle normal success case
    module.exit_json(
        changed=changed,
        original_message=message,
        reversed_message=reversed_message
    )

if __name__ == "__main__":
    main()