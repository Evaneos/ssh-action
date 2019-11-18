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

## Usage examples

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

## Inputs

| Parameter                           | Required                                  | Description                                                          |
|-------------------------------------|-------------------------------------------|----------------------------------------------------------------------|
| [`hosts`](#hosts)                   | Yes                                       | Remote host(s) to connect to                                         |
| `commands`                          | Yes                                       | One or multiple commands to run on the remote host(s)                |
| `user`                              | [Sometimes](#ssh-config--optional-inputs) | Remote user to connect with                                          |
| `port`                              | [Sometimes](#ssh-config--optional-inputs) | Remote port to connect to (_default: `22`_)                          |
| [`private_key`](#private-key)       | [Sometimes](#password-or-private-key)     | Private SSH key to connect with                                      |
| `password`                          | [Sometimes](password-or-private-key)      | Password to connect with                                             |
| [`known_hosts`](#known-hosts)       | No                                        | Known hosts keys that SSH can rely on to connect to the remote hosts |
| [`knock_sequence`](#knock-sequence) | No                                        | Knock sequence performed onto remote host(s) before connecting to it |
| [`ssh_config`](#ssh-config)         | No                                        | SSH config to use to connect to remote host(s)                       |

## Outputs

_No output is generated._

## Configuration

### Hosts<a name="hosts"></a>

Specify the remote host(s) - [they all must share the same authentication](#one-auth-for-all-hosts) - to run the `commands` on via the `hosts` input.

### Private SSH key<a name="private-key"></a>

To authenticate yourself, you can use a private SSH key with the `private_key` input [**using a PEM format**](#not-a-valid-rsa-private-key). The script will dump the SSH private key to `~/.ssh/id_rsa`.

Note if you both `password` and `private_key`, `password` will be ignored.<a name="password-or-private-key"></a>

### Known hosts<a name="known-hosts"></a>

You can specify explicit one or multiple known hosts keys using the `known_host` input.

When not specifying `known_hosts`, the option `StrictHostKeyChecking=no` is added in the `ssh_config`: in such cases, you are exposing yourself to security risks! ⚠️

### Knock sequence<a name="knock-sequence"></a>

If your remote host needs a knocking sequence (see [`man knock`](https://linux.die.net/man/1/knock)), you can specify the sequence through the `knock_sequence` input.

For example, with a `knock_sequence` of `111 222 333`, the action will create an SSH config with a `ProxyCommand` that will knock the `host` until it is reachable or will fail after 10 attemps.

You can change this behaviour by specifying your own SSH config (see the [**SSH config**](#ssh-config) section).

### SSH config<a name="ssh-config"></a>

To have complete control over the connection behaviour, you can specify a `ssh_config` input with a compliant SSH config ([`man ssh_config`](https://linux.die.net/man/5/ssh_config)) which will be dumped as is in `~/.ssh/config`.

Beware, the `user`, `port` & `knock_sequence` inputs will be ignored, specify them explicitely in your `ssh_config`. Also note that you cannot declare the `IdentityFile` as its location is hard-coded (`~/.ssh/id_rsa`).<a name="ssh-config--optional-inputs"></a>

## Limitations

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

### One authentication for every hosts<a name="one-auth-for-all-hosts"></a>

You cannot have multiple SSH keys or passwords for all the `hosts`: they must share the same authentication method **AND** the same credential (i.e. same `password` or same `private_key`).

## Troubleshooting

### "Not a valid RSA private key file"<a name="not-a-valid-rsa-private-key"></a>

You need to use a PEM-formatted SSH private key because `paramiko`, one of the library behind this action, does not support the newest key formats [[reference](https://github.com/paramiko/paramiko/issues/340#issuecomment-492448662)]:

```shell
ssh-keygen -t rsa -b 4096 -C "email@email.com" -m PEM
```
