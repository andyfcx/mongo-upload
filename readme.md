# 🧩 mongo_upload

A secure, elegant CLI tool to upload JSON files to MongoDB with encrypted credentials and a beautiful progress bar.

Built with:
- [Click](https://click.palletsprojects.com/) for CLI interactions
- [PyMongo](https://pymongo.readthedocs.io/) for MongoDB communication
- [cryptography](https://cryptography.io/) for asymmetric credential encryption
- [Rich](https://rich.readthedocs.io/) for modern terminal UI
- [Poetry](https://python-poetry.org/) for dependency and packaging management

---

## ✨ Features

- 🔐 Encrypted MongoDB credential storage using RSA asymmetric encryption
- 📂 Upload JSON files to specified MongoDB collections
- 🧠 Remembers your default database and collection
- 📊 Beautiful progress bar with [Rich](https://rich.readthedocs.io/)
- 🧹 Logout and wipe stored credentials

---

## 📦 Installation

### Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation)

### Option 1: Local development
```bash
poetry install
poetry run mongo_upload login
```

### Option 2: Install as a global command
```
./install.sh
```
