# ansible-aws-tools-linux
Ansible modules for installing, updating, and removing AWS tools on Linux

https://galaxy.ansible.com/ui/repo/published/mdinicola/aws_tools_linux/docs/

It provisions the following tools:
- AWS CLI

## Installation

Requires [ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) and [ansible-galaxy](https://docs.ansible.com/ansible/latest/collections_guide/collections_installing.html#installing-collections-with-ansible-galaxy) to be installed first.

To install this module, run:

        ansible-galaxy collection install mdinicola.aws_tools_linux

## Playbook examples

### AWS CLI

        name: Install AWS CLI
        mdinicola.aws_tools_linux.aws_cli:
          state: present

        name: Update AWS CLI to a newer version
        mdinicola.aws_tools_linux.aws_cli:
            state: update

        name: Uninstall AWS CLI
        mdinicola.aws_tools_linux.aws_cli:
            state: absent