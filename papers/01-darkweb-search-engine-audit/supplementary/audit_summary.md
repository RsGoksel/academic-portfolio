# Audit Summary — OnionClaw v2.3.0 Pre-Install Verification

**Subject:** `github.com/JacobJandon/OnionClaw`, v2.3.0 line
**Audit date:** 2026-05-28
**Auditor:** the present author (independent of the upstream project)
**Status:** Cleared for read-only academic use; no malicious code identified.

## Scope

Pre-install source-code audit of the OnionClaw dispatcher prior to its use as
the measurement instrument in the accompanying manuscript. Adversarial review:
the auditor read every Python source file, every dependency declaration,
every installation hook, and every binary file present in the repository at
the audited commit.

## Method (10-point checklist applied)

1. Repository metadata: `git log` history reviewed; commit author identity
   stable across the audited tag range; no force-pushes within the audited
   window; no anomalous commits adding binaries.
2. Dependency manifests: `requirements.txt` declares four mainstream
   packages (`requests[socks]`, `beautifulsoup4`, `python-dotenv`, `stem`),
   all pinned to a lower bound and current at audit date; no typosquat
   candidates.
3. Install hooks: `setup.py` is a runtime configuration wizard, not a
   setuptools install script; no code executes during `pip install`. The
   wizard was deliberately NOT executed during the measurement reported in
   the manuscript.
4. Dangerous primitives: `subprocess`, `os.system`, `__import__` uses all
   inspected; arguments are hardcoded; no `eval`, no `exec`, no
   `pickle.loads`, no `marshal.loads` on network input.
5. Outbound network: every hostname referenced in source is either (a) the
   local Tor SOCKS proxy, (b) `check.torproject.org` for liveness, (c) the
   GitHub API for the project's own release-version check, (d) the eighteen
   .onion search engines declared in the dispatcher's configuration, or
   (e) the named LLM vendor APIs (only used when the operator supplies an
   API key at run time).
6. Encoded blobs / obfuscation: no long base64 strings, no hex-encoded
   payloads, no one-liner-encoded source files.
7. Binary files: the only non-source-code files are two PNG logo files and
   one empty Jupyter notebook placeholder. No `.exe`, no `.dll`, no `.so`,
   no `.zip` archives.
8. Secret handling: API keys are read via `os.getenv` and passed only to
   the corresponding vendor SDK. They are not written to disk and are not
   transmitted to any third-party host. The library suggests `.env` with
   chmod 600.
9. Tor configuration: the dispatcher expects an externally-installed Tor
   instance addressable at the SOCKS port configured by the operator. It
   does not bundle a Tor binary and does not modify the operator's
   existing `torrc`.
10. README vs. code reality: the feature claims in the upstream README
    match the implemented operations one-to-one; no undocumented behaviour
    was identified in source.

## Outcome

No evidence of malicious code, exfiltration, or non-disclosed network
endpoints. The dispatcher was approved for read-only academic use on the
isolated Tor instance documented in `T2_tor_setup.md`. The `setup.py`
runtime wizard was NOT executed; the library was loaded as an importable
Python module from a project-local Python virtual environment whose
contents are pinned in `T3_pip_freeze.txt`.

## Disclosure

The auditor (Kadir Göksel Gündüz, Energy Institute, Istanbul Technical
University) has no affiliation with the upstream OnionClaw project and is
not a contributor to it. The library was selected for evaluation because
it is a public open-source aggregator that exposes eighteen Tor-network
search engines behind a uniform interface, which is the exact measurement
surface of interest in the accompanying manuscript. There is no conflict
of interest.
