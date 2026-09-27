# Safe update workflow

This is the update route for Chris's standalone copy after John publishes a newer version.

## Current baseline

The deployment currently running on Chris's NAS came from the supplied 15 September 2026 snapshot. The GitHub repository did not yet contain John's application source when this workflow was written.

The Ubuntu launcher opens that secured NAS deployment. It does not silently replace the running version when GitHub changes.

## When John pushes an update

Chris can say: **“John has pushed the update — update my standalone app from his GitHub.”**

The integration pass will then:

1. Fetch John's new Git commit without overwriting the running application.
2. Scan the incoming tree for API keys, credentials, login sessions, browser profiles, and private machine data. Any such material is removed from the integration copy without displaying its value and is not committed onward.
3. Compare the new source with the currently deployed 15 September baseline and record which version is being selected.
4. Preserve Chris's local application data separately from source and build files.
5. Build and test the update in a staged service or package.
6. Complete representative interface, file/project, and local-AI workflows—not just a health check.
7. Switch the launcher/service only after the staged version passes, retaining a rollback route to the last working build.

## Source and data rules

- Source updates come from this repository.
- Runtime data, credentials, and login material stay outside Git.
- Oracle Control remains separate and unchanged.
- John's authorship and commit history are preserved.
- A failed or incomplete update does not replace the working application.
