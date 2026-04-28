# Contributing

Thank you for improving 清账.

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 run.py
```

## Checks

Before opening a pull request, run:

```bash
python3 -m py_compile main.py run.py core/*.py ui/*.py
```

If you change exports, manually test both Excel and PNG output.

## Data Safety

Do not commit local runtime data:

- `path_config.json`
- `accounts_data/`
- `password_backups/`
- `master_password.hash`
- `*.encrypted`

