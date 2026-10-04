# net_sentinel

`net_sentinel` keeps an SSH dynamic-forwarding tunnel alive and exposes it as a local SOCKS5 proxy.

It is intended for selective proxying: applications such as FoxyProxy can send only selected traffic through a VPS, while the rest of the system uses the normal Internet connection.

```text
Application
    |
    | SOCKS5
    v
127.0.0.1:<LOCAL_PORT>
    |
    | SSH dynamic forwarding
    v
VPS
    |
    v
Internet
```

The utility monitors the SSH process and reconnects if the tunnel is lost.

The main advantage of this approach is that it builds a selective proxy on top of standard OpenSSH rather than introducing a separate VPN or proxy stack. Modern desktop operating systems already include an SSH client and ssh-keygen, while Ubuntu VPS installations normally have an SSH server available from the start. As a result, the whole system consists of a small client wrapper around a mature, well-tested SSH transport and a narrowly restricted SSH account on the VPS. There is very little additional infrastructure to install, configure or maintain.

The trade-off compared with a VPN is that this is an application-level SOCKS proxy rather than a network-level tunnel. Only applications that support SOCKS or can be explicitly configured to use it will send traffic through the VPS; arbitrary system traffic, applications unaware of the proxy, and protocols outside the supported proxy model are not transparently routed. A VPN is therefore more universal, while SSH dynamic forwarding is much simpler when selective proxying is exactly what is needed.

## Requirements

Current client implementation requires:

- Windows
- Python
- OpenSSH client (`ssh`) available in `PATH`
- an SSH key pair for this client

## Create client SSH key

Generate a dedicated ED25519 key pair:

```powershell
ssh-keygen -t ed25519
```

Use a separate key pair for each client/device.

Keep the private key on the client. Send only the public key (`.pub`) to the VPS administrator so it can be authorized for `net_sentinel`.

```text
id_ed25519      -> keep on the client
id_ed25519.pub  -> send to the VPS administrator
```

The VPS administrator should provide back:

- the VPS hostname or IP;
- the VPS SSH host public key.

## Configuration

Create the `.env` file expected by the application:

```dotenv
HOST=<VPS-HOSTNAME>
HOST_PUBLIC_KEY="ssh-ed25519 <PUBLIC-KEY>"
IDENTITY_FILE="C:/path/to/id_ed25519"
LOCAL_PORT=50000
```

- `HOST` — VPS hostname or IP address;
- `HOST_PUBLIC_KEY` — trusted SSH host public key of the VPS, used for automatic strict host verification;
- `IDENTITY_FILE` — path to the client's private SSH key;
- `LOCAL_PORT` — local SOCKS5 port.

The SOCKS proxy is bound to `127.0.0.1`, so it is available only to local applications.

## Application proxy

Configure FoxyProxy or another SOCKS-capable application to use:

```text
Type: SOCKS5
Host: 127.0.0.1
Port: 50000
```

Use the value configured in `LOCAL_PORT`.

## Test

With `net_sentinel` running:

```powershell
curl.exe --socks5-hostname 127.0.0.1:50000 https://ifconfig.me
```

The returned address should be the public IP of the VPS.

## Server setup

The VPS uses a dedicated restricted OpenSSH account that is allowed to perform local TCP forwarding but cannot open a normal shell.

See [SERVER_SETUP.md](SERVER_SETUP.md) for server installation, SSH restrictions, and adding or revoking clients.

## Security model

The trust exchange is:

```text
Client -> VPS administrator:
    client public key
    used by the VPS to authorize this client

VPS administrator -> Client:
    VPS hostname/IP
    VPS SSH host public key
    used by net_sentinel to verify the server
```

The client private key never leaves the client.

The forwarding SSH account is restricted to proxy forwarding and is separate from administrative SSH access.
