import click
from pathlib import Path
from auth import generate_keys, encrypt_and_store_credentials, load_credentials
from uploader import upload_file
import certifi

CRED_FILE = Path.home() / ".mongo_upload" / "credentials.enc"

@click.group()
def cli():
    """📦 mongo_upload - CLI tool to upload JSON to MongoDB easily"""
    pass

@cli.command()
def login_cmd():
    """登入並加密儲存 MongoDB 帳密"""
    if CRED_FILE.exists():
        click.echo("You have logged in, to logout, use `mongo_upload logout`")
        return

    user = click.prompt("Mongo username: ", type=str)
    password = click.prompt("Mongo password: ", hide_input=True)
    host = click.prompt("Mongo host: (Default localhost)", default="localhost")
    port = click.prompt("Mongo port: (Default 27017)", default=27017, type=int)
    auth_db = click.prompt("Auth source: ", default="admin")

    mongo_uri = f"mongodb://{user}:{password}@{host}:{port}/?authSource={auth_db}&tls=true&tlsCAFile={certifi.where()}"
    
    generate_keys()
    encrypt_and_store_credentials({"uri": mongo_uri})
    click.echo("You have logged in, credentials are saved.")

@cli.command()
def logout():
    from auth import KEY_DIR, CRED_FILE, PUB_KEY_FILE, PRI_KEY_FILE

    if not CRED_FILE.exists():
        click.echo("No stored credentials, you are not logged in, no need to logout.")
        return

    confirm = click.confirm("⚠️ Are you sure to logout?", default=False)
    if not confirm:
        click.echo("Not logging out, cancelled.")
        return

    for file in [CRED_FILE, PUB_KEY_FILE, PRI_KEY_FILE]:
        if file.exists():
            file.unlink()
    click.echo("You have logged out.")

@cli.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("filepath", type=click.Path(exists=True))
def upload(filepath):
    credentials = load_credentials()
    if not credentials or "uri" not in credentials:
        click.echo("Please login first: `mongo_upload login`")
        return

    uri = credentials["uri"]
    db = credentials.get("db")
    collection = credentials.get("collection")

    if db and collection:
        use_defaults = click.confirm(f"Default upload to {db}.{collection}, continue?", default=True)
        if not use_defaults:
            db = click.prompt("Enter database name: ")
            collection = click.prompt("Enter collection name: ")
    else:
        db = click.prompt("Enter database name: ")
        collection = click.prompt("Enter collection name: ")

    confirm = click.confirm(f"Are you going to upload {filepath} to {db}.{collection}?", default=True)
    if not confirm:
        click.echo("Upload is cancelled.")
        return

    credentials["db"] = db
    credentials["collection"] = collection
    encrypt_and_store_credentials(credentials)

    upload_file(uri, filepath, db, collection)
