# Standalone Linux desktop application plan

## Objective

Package John's existing WCR Console & AI Development application as its own Linux desktop app while preserving its appearance, behaviour, features, and content as closely as practical.

## Proposed shape

- A small Tauri desktop shell provides the native window, application identity, launcher, and lifecycle controls.
- The existing Python/Streamlit application remains the functional core initially, started locally on loopback as a managed sidecar or user service.
- Local data lives in an app-specific user-data directory.
- Local AI calls use explicitly configured loopback services; no API key is embedded in source or packaging.
- The app receives its own icon, desktop entry, launcher, service names, logs, and rollback package.
- Oracle Control remains separate and unchanged.

This keeps the first conversion narrow and reversible. A deeper interface rewrite can be considered later, but it is not required merely to deliver a dependable desktop application.

## Work stages

### 1. Establish the source baseline

- Receive John's latest source-only tree.
- Compare it with the supplied snapshot without overwriting either one.
- Record the selected source commit and preserve John's authorship and history.
- Remove secrets and local/generated material before any import.

### 2. Make the application portable

- Replace Windows-only launch commands and absolute paths with platform-aware equivalents.
- Define Python and system dependencies from clean manifests.
- Separate source, user data, generated output, and configuration.
- Keep hardware access opt-in and fail clearly when a device is unavailable.

### 3. Build the desktop package

- Add the Tauri shell and a deterministic local backend start/stop path.
- Use an app-specific loopback port selected to avoid existing services.
- Package required Python resources rather than relying on developer-machine paths.
- Add a Linux desktop entry and launcher without altering Oracle Control.

### 4. Connect Chris's local services

- Detect the approved local Ollama endpoint and supported models.
- Keep external providers disabled until a user deliberately supplies credentials outside the repository.
- Validate file, browser, audio, GPU, and hardware features individually where they are genuinely supported.

### 5. Verify the real result

- Launch from the desktop application menu.
- Complete the SMD decoder workflow used by the existing deployment proof.
- Exercise one representative file/project workflow.
- Exercise one local-AI workflow without cloud credentials.
- Restart the workstation-side service and confirm recovery.
- Verify uninstall and rollback leave John's data intact.

## Deliverables

- Installable Linux desktop package.
- Desktop launcher and isolated runtime service.
- Dependency and configuration documentation.
- Test evidence for real workflows.
- Rollback instructions.
- A clear list of features that remain Windows-only, hardware-dependent, or awaiting source clarification.
