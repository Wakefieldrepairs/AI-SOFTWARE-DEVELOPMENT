# Security and credentials

Do not commit API keys, passwords, login sessions, OAuth tokens, private keys, browser profiles, cookies, or machine credentials to this repository.

Store local secrets outside the repository and load them at runtime through protected environment or credential files. Example files must contain placeholders only.

The repository ignores common secret-bearing files, but ignore rules are not a security boundary. Before each push, check the staged diff and run a secret scanner.

## If a secret is shared accidentally

1. Do not quote, paste, or display its value.
2. Revoke or rotate it immediately with the provider.
3. Remove it from the working tree.
4. If committed, purge it from Git history and coordinate the required force-push with the repository owner.
5. Re-scan the repository before continuing.

Deleting a file from the latest commit does not remove it from earlier Git history. GitHub secret scanning and push protection should be enabled by the repository owner where available.
