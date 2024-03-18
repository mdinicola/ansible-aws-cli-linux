#!/usr/bin/python

# Copyright: (c) 2024 Mike Di Nicola <mike@mdinicola.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: my_test

short_description: Provisions AWS CLI in Linux

version_added: "1.0.0"

description: This module installs, updates, or uninstalls the AWS CLI tool in Linux

options:
    state:
        description: 
            - Indicates the desired tool state.
            - Use O(update) to update to a new version if one is available
        choices: ['present','absent','update']
        default: 'present'
        required: no
        type: str
    download_url:
        description:
            - Specify the url to download the AWS CLI installer package from.
        default: 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip'
        type: str
    download_dir:
        description:
            - Specify where to download the AWS CLI installer package.
            - Defaults to a temporary directory.
        type: str
    download_file_name:
        description:
            - Specify the the name of the AWS CLI installer package when downloaded
        default: 'awscli-exe-linux-x86_64.zip'
        type: str
    bin_dir: 
        description: 
            - Override the default location of where I(aws) is installed
        default: '/usr/local/bin'
        required: no
        type: str
    install_dir:
        description: 
            - Override the default location of where I(aws) files are copied
        default: '/usr/local/aws-cli'
        required: no
        type: str

author:
    - Mike Di Nicola (@mdinicola)
'''

EXAMPLES = r'''
# Install the AWS CLI
- name: Install AWS CLI
  mdinicola.aws_tools_linux.aws_cli:
    state: present

# Update the AWS CLI to a newer version
- name: Update AWS CLI
  mdinicola.aws_tools_linux.aws_cli:
    state: update

# fail the module
- name: Update AWS CLI
  mdinicola.aws_tools_linux.aws_cli:
    state: absent
'''

RETURN = r'''
## These are examples of possible return values, and in general should use other names for return values.
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'aws cli installed successfully'
'''

from ansible.module_utils.basic import AnsibleModule
import os
import tempfile

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        state=dict(type='str', required=False, default = 'present'),
        download_url=dict(type='str', required=False, default='https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip'),
        download_dir=dict(type='str', required=False, default=None),
        download_file_name=dict(type='str', required=False, default='awscli-exe-linux-x86_64.zip'),
        bin_dir=dict(type='str', required=False, default='/usr/local/bin'),
        install_dir=dict(type='str', required=False, default='/usr/local/aws-cli')
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    
    if module.params['state'] == 'present':
        # Exit if aws cli is already installed
        if os.path.exists(os.path.join(module.params['bin_dir'], 'aws')):
            result['message'] = 'aws cli already exists'
            module.exit_json(**result)

        result['changed'] = True

        # If running in check mode, exit before making any changes
        if module.check_mode:
            module.exit_json(**result)

        # Use download_dir variable if set, otherwise use temporary directory
        download_dir = module.params['download_dir']
        temp_dir = None
        if download_dir is None:
            temp_dir = tempfile.TemporaryDirectory()
            download_dir = temp_dir.name
    elif module.params['state'] == 'absent':
        if not os.path.exists(os.path.join(module.params['bin_dir'], 'aws')):
            result['message'] = 'aws cli is not installed'
            module.exit_json(**result)

        

    elif module.params['state'] == 'update':
            pass
    
    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    #if module.params['new']:
    #    result['changed'] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    #if module.params['name'] == 'fail me':
    #    module.fail_json(msg='You requested this to fail', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()