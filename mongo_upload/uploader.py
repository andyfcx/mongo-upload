import json
from pymongo import MongoClient
from rich.progress import Progress
from pathlib import Path

def upload_file(uri, filepath, db_name, collection_name):
    client = MongoClient(uri)
    db = client[db_name]
    col = db[collection_name]

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        data = [data]

    total = len(data)
    print(f"📦 開始上傳 {total} 筆資料到 {db_name}.{collection_name}\n")

    with Progress() as progress:
        task = progress.add_task("上傳中...", total=total)
        for doc in data:
            col.insert_one(doc)
            progress.update(task, advance=1)

    print("\n✅ 上傳完成")
