# Security Policy

清账 is a local-first desktop app. Bill data is stored on the user's machine and protected with a master password derived encryption key.

## Sensitive Files

Never publish files generated at runtime:

- `master_password.hash`
- `password_backup_*.txt`
- `accounts_data/`
- `password_backups/`
- `*.encrypted`
- `path_config.json`

## Reporting Issues

If you find a security issue, avoid sharing sample data publicly. Open a private report if available, or contact the maintainer directly with minimal reproduction details.

