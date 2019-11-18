#!/usr/bin/env sh

# Very basic script to test
# /!\ Not stable nor reproducible for now! /!\

export INPUT_HOSTS='
host1.example.com
host2.example.com
'

export INPUT_KNOCK_SEQUENCE='1111 2222 3333 4444 5555'

read -r -d '' INPUT_COMMANDS <<'EOF'
echo "It seems..."
echo "...that..."
echo "...Github action rocks!"
EOF
export INPUT_COMMANDS

read -r -d '' INPUT_KNOWN_HOSTS <<'EOF'
host1.example.com ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ==
host2.example.com ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCsj2bNKTBSpIYDEGk9KxsGh3mySTRgMtXL583qmBpzeQ+jqCMRgBqB98u3z++J1sKlXHWfM9dyhSevkMwSbhoR8XIq/U0tCNyokEi/ueaBMCvbcTHhO7FcwzY92WK4Yt0aGROY5qX2UKSeOvuP4D6TPqKF1onrSzH9bx9XUf2lEdWT/ia1NEKjunUqu1xOB/StKDHMoX4/OKyIzuS0q/T1zOATthvasJFoPrAjkohTyaDUz2LN5JoH839hViyEG82yB+MjcFV5MU3N1l1QL3cVUCh93xSaua1N85qivl+siMkPGbO5xR/En4iEY6K2XPASUEMaieWVNTRCtJ4S8H+9
EOF
export INPUT_KNOWN_HOSTS

read -r -d '' INPUT_SSH_CONFIG <<'EOF'
Host host1.example.com
    User your-user1
    ProxyCommand ssh jump-host1.example.com -W %h:%p
Host host2.example.com
    User your-user2
    ProxyCommand ssh jump-host2.example.com -W %h:%p
EOF
export INPUT_SSH_CONFIG

read -r -d '' INPUT_PRIVATE_KEY  <<'EOF'
-----BEGIN RSA PRIVATE KEY-----

-----END RSA PRIVATE KEY-----
EOF

export INPUT_PRIVATE_KEY

docker run -ti --rm \
    --env INPUT_HOSTS="$INPUT_HOSTS" \
    --env INPUT_USER="evaneos" \
    --env INPUT_KNOCK_SEQUENCE="$INPUT_KNOCK_SEQUENCE" \
    --env INPUT_COMMANDS="$INPUT_COMMANDS" \
    --env INPUT_KNOWN_HOSTS="$INPUT_KNOWN_HOSTS" \
    --env INPUT_PRIVATE_KEY="$INPUT_PRIVATE_KEY" \
    `#--env INPUT_SSH_CONFIG="$INPUT_SSH_CONFIG"` \
    --entrypoint /bin/sh \
    evaneos/ssh-action:0.1.0
