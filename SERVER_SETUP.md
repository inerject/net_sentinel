# SSH server setup

This document describes the OpenSSH server configuration used by `net_sentinel`.

A single restricted Unix account is used:

```text
dyn_forwarding_only
```

The account name **must be exactly `dyn_forwarding_only`** because the current `net_sentinel` client uses this SSH username internally.

Each client/person has a separate SSH key pair, but all clients use the same restricted account.

## 1. Create the account

```bash
adduser --disabled-password --shell /usr/sbin/nologin dyn_forwarding_only

chown root:root /home/dyn_forwarding_only
chmod 700 /home/dyn_forwarding_only
```

The account is not intended for normal shell access.

## 2. Create the authorized-keys file

```bash
mkdir -p /etc/ssh/authorized_keys_dyn
chown root:root /etc/ssh/authorized_keys_dyn
chmod 755 /etc/ssh/authorized_keys_dyn

touch /etc/ssh/authorized_keys_dyn/dyn_forwarding_only
chown root:root /etc/ssh/authorized_keys_dyn/dyn_forwarding_only
chmod 644 /etc/ssh/authorized_keys_dyn/dyn_forwarding_only
```

Keeping the file under `root` control prevents the restricted account from authorizing additional keys itself.

## 3. Restrict the account in sshd

Add to `/etc/ssh/sshd_config`:

```sshconfig
Match User dyn_forwarding_only
        AuthorizedKeysFile /etc/ssh/authorized_keys_dyn/%u
        AllowTcpForwarding local
        PermitOpen any
        AllowAgentForwarding no
        X11Forwarding no
        PermitTunnel no
        PermitTTY no
        MaxSessions 0
        PasswordAuthentication no
        KbdInteractiveAuthentication no
```

This allows local TCP forwarding, including SOCKS dynamic forwarding, while disabling normal SSH sessions and unrelated forwarding features.

Validate and reload:

```bash
sshd -t
systemctl reload ssh
```

Optional verification:

```bash
sshd -T -C user=dyn_forwarding_only,host=localhost,addr=127.0.0.1 \
  | grep -E 'authorizedkeysfile|allowtcpforwarding|permitopen|maxsessions|permittty|x11forwarding|allowagentforwarding|permittunnel|passwordauthentication|kbdinteractiveauthentication'
```

## 4. Get the VPS host public key

For ED25519:

```bash
cat /etc/ssh/ssh_host_ed25519_key.pub
```

Copy that public value to the client's `HOST_PUBLIC_KEY`.

Do not distribute the corresponding private key:

```text
/etc/ssh/ssh_host_ed25519_key
```

## 5. Add a client

Obtain the client's SSH public key from the client/user and append it to:

```text
/etc/ssh/authorized_keys_dyn/dyn_forwarding_only
```

Example entry:

```text
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA... laptop-user
```

Use a meaningful comment at the end of the key to identify the client later.

No new Unix account is required for each client.

## 6. Revoke a client

Delete that client's public-key line from:

```text
/etc/ssh/authorized_keys_dyn/dyn_forwarding_only
```

No sshd reload is normally required. Existing SSH connections may remain active until they disconnect.
