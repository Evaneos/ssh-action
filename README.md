[![Docker badge](https://img.shields.io/badge/docker-ssh--action-blue.svg?style=flat-square&logo=docker)](https://hub.docker.com/repository/docker/evaneos/ssh-action)

# SSH

This Github action allows to run commands over SSH.

You can:
- run multiple **commands over SSH**
- run those commands on **multiple hosts**
- **easily configure** the SSH configuration
- or provide **your own SSH config** both simply or in details

## Disclaimer

This Github action is rather young and it might not be as stable and battle-tested as you need: use it at your own risk.

## Usage

### Basic usage

```yaml
steps:
- name: Run a command remotely
  uses: docker://evaneos/ssh-action:0.1.0
  with:
    hosts: example.com
    user: john-doe
    private_key: ${{ secrets.PRIVATE_SSH_KEY }}
    knock_sequence: ${{ secrets.KNOCK_SEQUENCE }}
    commands: echo "Hello world!"
```

### Alternative usage

```yaml
steps:
- name: Multiple commands over multiple hosts with custom SSH config
  uses: docker://evaneos/ssh-action:0.1.0
  with:
    hosts: |
        host1.example.com
        host2.example.com
    private_key: ${{ secrets.PRIVATE_SSH_KEY }}
    known_hosts: ${{ secrets.KNOWN_HOSTS }}
    ssh_config: |
      Host host1.example.com
        User your-user1
        ProxyCommand ssh jump-host1.example.com -W %h:%p
      Host host2.example.com
        User your-user2
        ProxyCommand ssh jump-host2.example.com -W %h:%p
    commands: |
      echo "I can run..."
      echo "...multiple commands"
```

### SSH config<a name="ssh-config"></a>

You can specify a `ssh_config` input with a compliant SSH config ([`man ssh_config`](https://linux.die.net/man/5/ssh_config)) which will be dumped as is in `~/.ssh/config`.

Among other things, this will allow you to use a bastion or jump hosts or change the behaviour of the knock sequence.

In such case, beware:
- the `user` input is ignored, specify the `User` in `ssh_config`
- the `port` input is ignored, specify the `Port` in `ssh_config` if it's not standard
- the `knock_sequence` input is ignored, specify a `ProxyCommand` in `ssh_config` if you need it
  + Example: `ProxyCommand /bin/sh -c 'until nc -zv %h %p -w 1 2>&1 ; do knock %h 111 222 333 ; done; exec nc %h %p'`
- do not declare the `IdentityFile` as its location is hard-coded (`~/.ssh/id_rsa`)

### Port

If your port is not standard (`22`), you can specify it through the `port` input.

Note it is ignored if you declare an `ssh_config` input.

### Authentication

#### Private SSH key<a name="private-key"></a>

To authenticate yourself, you can use a private SSH key with the `private_key` input.

The script dumps the SSH private key to `~/.ssh/id_rsa`.

Note if you both `password` and `private_key`, `password` will be ignored.

Beware you need to use a PEM-formatted SSH key because `paramiko`, one of the library behind this action, does not support the newest key formats [[reference](https://github.com/paramiko/paramiko/issues/340#issuecomment-492448662)].

#### Password

To authenticate yourself, you can use a `password`.

The script passes the password to the SSH CLI through `sshpass`

#### Known hosts

You can specify explicit one or multiple (for jump host for example) known hosts keys using the `known_host` input.

If you do not specify the `known_hosts` input, the option `StrictHostKeyChecking=no` will be put in the SSH config file.

⚠️ Be aware that by not specifying `known_hosts`, you would be exposing yourself to security risks.

#### Knock sequence

If your remote host needs a knocking sequence (see [`man knock`](https://linux.die.net/man/1/knock)), you can specify the sequence through the `knock_sequence` input.

For example, with a `knock_sequence` of `111 222 333`, the action will create an SSH config with a `ProxyCommand` that will knock the `host` until it is reachable or will fail after 10 attemps.

You can change this behaviour by specifying your own SSH config (see the [**SSH config**](#ssh-config) section).

### Use environment variables

⚠️ You cannot use the [`env`](https://help.github.com/en/actions/automating-your-workflow-with-github-actions/workflow-syntax-for-github-actions#env) syntax to use environment variables within the `command`.

This is due to the fact that, for stability and security reasons, environment variables are not passed to the remote host.

You can overcome this issue by declaring them explicitely in the `commands` input, like so:

```yaml
steps:
- name: Run commands remotely
  uses: ./.github/workflows/actions/ssh
  with:
    # [...]
    commands: |
      export COMMIT_SHA_1=${{ github.event.pull_request.head.sha }}
      export YOUR_SECRET=${{ secrets.YOUR_SECRET }}

      # [...]
```

## Configuration

See [`action.yaml`](./action.yaml).

## Troubleshooting

### "Not a valid RSA private key file"

See the [**Private SSH key**](#private-key) section, you need to use a PEM-formatted SSH key:

```shell
ssh-keygen -t rsa -b 4096 -C "email@email.com" -m PEM
```

## Todo

- Add pipenv integration in Dockerfile
- Add Contributing guidelines
- Add better disclaimer and manage expectation
- Add more dependencies/implementation details
- Add changelog
- Add release(s)
- Document Docker repo 
- Publish to marketplace
- Tests
- CI
