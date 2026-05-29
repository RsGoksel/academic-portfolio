# T2 — Isolated Tor Environment Setup

**Date:** 2026-05-28
**Status:** DONE — Tor bootstrapped to 100%, `check.torproject.org` confirms `IsTor: true`.

## Tor binary

Source: **Tor Expert Bundle** (downloaded by the implementer subagent before it crashed).
- Bundle: `C:\tmp\darkweb-audit\tor\tor-expert-bundle.tar.gz` (22 MB)
- Bundle signatures: `C:\tmp\darkweb-audit\tor\sha256sums-signed-build.txt`
- Extracted `tor.exe`: **`C:\tmp\darkweb-audit\tor\tor\tor.exe`**

The user's existing Tor Browser (if any) is NOT touched. This is a separate process with separate config + data dir.

## torrc (final, in use)

```
SocksPort 127.0.0.1:9050
ControlPort 127.0.0.1:9051
CookieAuthentication 1
DataDirectory C:\tmp\darkweb-audit\tor\data
Log notice file C:\tmp\darkweb-audit\tor\tor.log
AvoidDiskWrites 0
ClientOnly 1
GeoIPFile C:\tmp\darkweb-audit\tor\geoip\geoip
GeoIPv6File C:\tmp\darkweb-audit\tor\geoip\geoip6
```

Bindings are loopback-only — nothing exposed to LAN.

## Process

- Running PID: **66276**
- Launched via background Bash task `b2vxv2i9d`
- Bootstrap log: `C:\tmp\darkweb-audit\tor\tor.log`

## Bootstrap log (tail)

```
May 28 11:22:55 Bootstrapped 56% (loading_descriptors): Loading relay descriptors
May 28 11:22:55 Bootstrapped 63% (loading_descriptors): Loading relay descriptors
May 28 11:22:56 Bootstrapped 70% (loading_descriptors): Loading relay descriptors
May 28 11:22:56 Bootstrapped 75% (enough_dirinfo): Loaded enough directory info to build circuits
May 28 11:22:56 Bootstrapped 90% (ap_handshake_done): Handshake finished with a relay to build circuits
May 28 11:22:56 Bootstrapped 95% (circuit_create): Establishing a Tor circuit
May 28 11:22:57 Bootstrapped 100% (done): Done
```

Bootstrap time ≈ 45 seconds.

## Verification: check.torproject.org

```json
{"IsTor":true,"IP":"45.84.107.182"}
```

HTML page also confirms: `Congratulations. This browser is configured to use Tor.`

Exit-node IP `45.84.107.182` ≠ Goksu's home IP. Routing through Tor is real.

## How to restart in future sessions

```powershell
# 1. Start tor.exe (background)
& "C:\tmp\darkweb-audit\tor\tor\tor.exe" -f "C:\tmp\darkweb-audit\tor\torrc"

# 2. Wait for bootstrap (in another shell)
Get-Content C:\tmp\darkweb-audit\tor\tor.log -Wait | Select-String "Bootstrapped 100"

# 3. Verify
curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip
```

## How to stop

```powershell
Get-Process tor -ErrorAction SilentlyContinue | Stop-Process
# or specifically: Stop-Process -Id 66276
```

If a stale `lock` file remains under `C:\tmp\darkweb-audit\tor\data\`, delete it before restarting.

## Security notes

- ControlPort 9051 requires cookie auth (`CookieAuthentication 1`) — set so the OnionClaw MCP (T3) can request circuit rotation via stem, but no remote process can.
- `ClientOnly 1` ensures we never accidentally become a relay/exit.
- Tor data dir is under `C:\tmp\darkweb-audit\tor\data\` — disposable; remove with the rest of the audit workspace when done.

**Ready for T3.**
