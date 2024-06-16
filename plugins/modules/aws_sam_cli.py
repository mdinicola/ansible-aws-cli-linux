#!/usr/bin/python

# Copyright: (c) 2024 Mike Di Nicola <mike@mdinicola.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: my_test

short_description: Provisions AWS SAM CLI in Linux

version_added: "1.1.0"

description: This module installs, updates, or uninstalls the AWS SAM CLI tool in Linux

options:
    state:
        description: 
            - Indicates the desired tool state.
            - Use O(updated) to update to a new version if one is available
            - The O(absent) option does not remove config files when uninstalling.  They must be manually removed
        choices: ['present','absent','updated']
        default: 'present'
        required: no
        type: str
    download_url:
        description:
            - Specify the url to download the AWS SAM CLI installer package from.
        default: 'https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip'
        type: str
    download_dir:
        description:
            - Specify where to download the AWS SAM CLI installer package.
            - Defaults to a temporary directory.
        type: str
    download_file_name:
        description:
            - Specify the the name of the AWS SAM CLI installer package when downloaded
        default: 'aws-sam-cli-linux-x86_64.zip'
        type: str
    bin_dir: 
        description: 
            - Override the default location of where I(sam) is installed
        default: '/usr/local/bin'
        required: no
        type: str
    install_dir:
        description: 
            - Override the default location of where I(sam) files are copied
        default: '/usr/local/aws-sam-cli'
        required: no
        type: str

author:
    - Mike Di Nicola (@mdinicola)
'''

EXAMPLES = r'''
- name: Install AWS SAM CLI
  mdinicola.aws_tools_linux.aws_sam_cli:
    state: present

- name: Update AWS SAM CLI
  mdinicola.aws_tools_linux.aws_sam_cli:
    state: updated

- name: Uninstall AWS SAM CLI
  mdinicola.aws_tools_linux.aws_sam_cli:
    state: absent
'''

RETURN = r'''
message:
    description: The output message from the module
    type: str
    returned: always
    sample: 'aws sam cli installed successfully'
'''

from ansible.module_utils.basic import AnsibleModule
from zipfile import ZipFile
from pathlib import Path
import os
import shutil
import tempfile
import urllib.request
import subprocess

def run_module():
    module_args = dict(
        state=dict(type='str', required=False, default = 'present'),
        download_url=dict(type='str', required=False, default='https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip'),
        download_dir=dict(type='str', required=False, default=None),
        download_file_name=dict(type='str', required=False, default='aws-sam-cli-linux-x86_64.zip'),
        bin_dir=dict(type='str', required=False, default='/usr/local/bin'),
        install_dir=dict(type='str', required=False, default='/usr/local/aws-sam-cli')
    )

    result = dict(
        changed=False
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.params['state'] == 'present':
        perform_install_or_update(module, result, False)

    elif module.params['state'] == 'absent':
        perform_uninstall(module, result)

    elif module.params['state'] == 'updated':
        perform_install_or_update(module, result, True)

    module.exit_json(**result)

def perform_install_or_update(module: AnsibleModule, result: dict, perform_update: bool = False):
    # Exit if aws sam cli is already installed
    if os.path.exists(os.path.join(module.params['bin_dir'], 'sam')) and perform_update == False:
        result['message'] = 'aws sam cli already exists'
        module.exit_json(**result)

    result['changed'] = True

    # If running in check mode, exit before making any changes
    if module.check_mode:
        module.exit_json(**result)

    download_dir, temp_dir = get_download_directory(module.params['download_dir'])

    try:
        # Download and extract installer zip
        extracted_path = download_and_extract(module.params['download_url'], download_dir, module.params['download_file_name'])

        # Install AWS SAM CLI
        installer_path = os.path.join(extracted_path, 'install')
        subprocess.run(['chmod', '+x', installer_path])
        if perform_update:
            subprocess.run([installer_path, '--update'])
        else:
            subprocess.run([installer_path])

        if not os.path.exists(os.path.join(module.params['bin_dir'], 'sam')):
            raise Exception('aws sam cli did not install successfully')

        subprocess.run(['chmod', '-R', '755', module.params['install_dir']])

        if perform_update:
            result['message'] = 'aws sam cli updated successfully'    
        else:
            result['message'] = 'aws sam cli installed successfully'

    except Exception as e:
        module.fail_json(msg='An error occurred: ' + str(e), **result)
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()

def perform_uninstall(module: AnsibleModule, result: dict):
    if not os.path.exists(os.path.join(module.params['bin_dir'], 'sam')):
        result['message'] = 'aws sam cli is not installed'
        module.exit_json(**result)

    result['changed'] = True

    # If running in check mode, exit before making any changes
    if module.check_mode:
        module.exit_json(**result)

    try:
        safe_remove_file(os.path.join(module.params['bin_dir'], 'sam'))
        safe_remove_directory(module.params['install_dir'])

        result['message'] = 'aws sam cli uninstalled successfully'
    except Exception as e:
        module.fail_json(msg='An error occurred: ' + str(e), **result)

def get_download_directory(download_dir: str = None):
    # Use download_dir variable if set, otherwise use temporary directory
    if download_dir is not None:
        return download_dir, None

    temp_dir = tempfile.TemporaryDirectory()
    return temp_dir.name, temp_dir

def download_and_extract(download_url: str, download_dir: str, file_name: str):
    # Download file
    download_path = os.path.join(download_dir, file_name)
    urllib.request.urlretrieve(download_url, download_path)

    # Extract zip file
    extracted_path = os.path.join(download_dir, Path(download_path).stem)
    with ZipFile(download_path) as zipFile:
        zipFile.extractall(extracted_path)
    
    return extracted_path

def safe_remove_file(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)

def safe_remove_directory(dir_path: str):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

def main():
    run_module()

if __name__ == '__main__':
    main()