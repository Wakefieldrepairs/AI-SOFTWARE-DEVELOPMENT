# WCR Console & AI Development

This repository is the shared collaboration space for John's **WCR Console & AI Development** application and Chris's local integration work.

John / Wakefield Repairs created the original application, its features, interface, and content. The desktop and local-runtime work described here is an integration layer; it does not replace or claim authorship of John's work.

## Current position

- A supplied snapshot of John's application has been preserved locally and deployed as a separate, isolated application.
- The deployed application is currently healthy, and a real Hardware Lab workflow has previously been completed successfully through its interface.
- Chris now has an interim Ubuntu Apps launcher named **John's App**. It opens the secured NAS deployment in its own app-style window while the native package is being built.
- The GitHub repository did not yet contain John's current source on 27 September 2026, so no native desktop build has been made from GitHub yet.
- A Linux desktop conversion and verification plan is now documented.
- Credentials and login material are explicitly excluded from this repository.

## Documents

- [Integration status](docs/INTEGRATION_STATUS.md)
- [Desktop application plan](docs/DESKTOP_APP_PLAN.md)
- [Safe update workflow](docs/UPDATE_WORKFLOW.md)
- [Collaboration record](COLLABORATION.md)
- [Security policy](SECURITY.md)

## Next handoff

John: please push the latest source-only version of the application, or confirm that the supplied snapshot is the version to use. Please exclude API keys, login sessions, browser profiles, generated media, dependency folders, backups, and local machine data.

Once the authoritative source is present, Chris's integration work can continue from a clean branch without changing the original product identity.
