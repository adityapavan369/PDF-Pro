Title: Secure config, CSRF protection, host install script and CI workflow

Summary:
- Added environment-driven admin credentials and session hardening in `config.py`.
- Implemented a lightweight CSRF protection (no external Flask-WTF dependency) and added CSRF token to the admin login and rerun forms.
- Added `scripts/install_host_deps.sh` to install LibreOffice and visual-diff Python libs on Ubuntu hosts.
- Added GitHub Actions workflow `.github/workflows/acceptance.yml` to run acceptance tests on an Ubuntu runner and upload `outputs/` as artifacts.
- Documented host setup and CI steps in `README.md`.

Notes:
- The container environment used for development here cannot install system packages (LibreOffice) due to permissions; use the install script on a host or rely on CI.
- We intentionally avoided Flask-WTF due to compatibility issues with Flask 3.x in this environment and implemented a small CSRF helper instead.
