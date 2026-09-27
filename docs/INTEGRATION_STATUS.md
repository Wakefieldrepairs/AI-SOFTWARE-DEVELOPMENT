# Integration status

Updated: 27 September 2026

## Ownership and intent

John / Wakefield Repairs is the author of the original WCR Console & AI Development application. Chris is adapting it for his own local Linux environment and contributing that integration work back openly.

The goal is a separate, standalone desktop application. It must not share an identity, launcher, data directory, port, or service name with Oracle Control.

## Verified progress

- The exact supplied application snapshot was previously deployed in an isolated container on Chris's NAS.
- The live application service was rechecked on 27 September 2026: it was active, had no recorded restarts, and returned HTTP 200 on its loopback health check.
- Earlier end-to-end browser verification opened the real interface and completed Hardware Lab -> SMD & EIA-96 Code Decoder -> `472` -> `4.70 kOhm (4,700 ohm)`.
- The public GitHub repository has been connected to Chris's workstation, and Chris's GitHub account has push access.
- Sensitive credential, token, and browser-session material found in the supplied snapshot was excluded and removed from the retained working material without displaying its contents.
- The NAS runtime image was rebuilt without embedded application source or credentials. All three existing John-app services now run that clean image; the older image and its unused build cache were removed after the replacement passed a live smoke test.

## Not yet complete

- The GitHub repository did not contain John's current application source when this status was written.
- The application has not yet been packaged as a native Linux desktop application.
- Windows-specific launchers, absolute paths, hardware access, local AI integrations, and file-writing behaviour still need a controlled Linux compatibility pass.
- A healthy web service is not being treated as proof of the future desktop package. The packaged application must pass real user workflows.

## What is needed from John

Please provide one of the following:

1. Push the latest source-only application to this repository; or
2. Confirm that the previously supplied snapshot is the authoritative version to import.

Please do not include credentials, API keys, login sessions, browser profiles, generated outputs, backups, `node_modules`, virtual environments, or machine-specific caches.

## Acceptance boundary

The desktop conversion is complete only when the installed launcher opens the standalone app and the representative workflows work with local services after a restart. A build, service health check, or wrapper window alone is not acceptance.
