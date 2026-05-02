# Changelog

All notable changes to this project are documented here.

## v5.5 - 2026-05-03

- Added a recent-bills display toggle for switching between the latest 20 records and all records.
- Kept bulk selection and deletion working in both recent and all-record views.
- Stored each visible recent-bill row's original source index to make deletion reliable even when duplicate records have the same amount, description, and date.

## v5.4 - 2026-04-30

- Added a first-run "read existing data directory" flow that can connect to data already on the computer.
- Detects existing data from an old project folder, an accounts_data folder, or a folder containing path_config.json.
- Preserves existing encrypted data by requiring the original master password hash before treating a directory as readable.
- Migrates legacy root-level master_password.hash into the selected accounts_data directory for compatibility with the current loader.

## v5.3 - 2026-04-28

- Rebuilt the main window as a professional accounting workspace with sidebar navigation, a persistent account context bar, and structured content pages.
- Redesigned dashboard, bill entry, ledger search, transfer settlement, export, and account settings layouts while preserving the existing business logic.
- Improved table column policies so amount, date, description, and action columns remain readable across normal and minimum window sizes.
- Reworked the first-run path configuration dialog with a wider grid layout and stable path fields to prevent overlapping controls.
- Updated UI screenshots for the new workspace design.
- Added macOS DMG packaging assets and a GitHub Actions workflow for macOS and Windows installer builds.

## v5.2 - 2026-04-28

- Reworked the desktop UI with a fresh light theme and clearer visual hierarchy.
- Fixed first-run path configuration and login dialog layout overlap.
- Improved table refresh performance by batching redraws.
- Delayed matplotlib loading until PNG export is needed.
- Fixed account-management double-click switching.
- Fixed custom category refresh and deletion validation.
- Reduced repeated encrypted writes during batch deletion.
- Updated PNG export styling to match the new visual identity.

## Earlier Versions

See the version history in [README.md](README.md#-版本更新).
