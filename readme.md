


### 事前準備
- docker compose関連ファイルの作成
  - docker-compose.yaml
  - Dockerfile

```bash
docker compose build
```

### fastapiのインストール
- pyproject.tomlを生成
```bash
sh init_pyprj_toml.sh
```

- fastapiのインストール
```bash
docker compose run --entrypoint "poetry install --no-root" demo-app
```

### hello worldを表示するためのファイルの作成

- main.py
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
```

### docker composeの実行
```bash
docker compose up
```


## TODOアプリ
> REST API
> - GET /tasks
> - POST /tasks
> - PUT /tasks/{task_id}
> - DELETE /tasks/{task_id}
> - PUT /tasks/{task_id}/done
> - DELETE /tasks/{task_id}/done
- 必要機能
> ToDoリストを表示する
> ToDoにタスクを追加する
> ToDoのタスクの説明文を変更する
> ToDoのタスクを削除する
> ToDoのタスクを完了にする
> ToDoのタスクを未完了にする

## FastAPIの実装

- ルーター（routers）
- スキーマ（schemas）

### dbの作成

`docker compose up`されている状態で、別のターミナルを開き、以下のコマンドを実行
- db コンテナの中で"mysql demo"コマンドを発行
```bash
docker compose exec db mysql demo
```

MySQLクライアントのインストール
```bash
# demo-app コンテナの中で"poetry add sqlalchemy pymysql"を実行
docker compose exec demo-app poetry add sqlalchemy pymysql
```

### DBの初期化

- migrate_db.py
```bash
docker compose exec demo-app poetry run python -m api.migrate_db
```


### aiomysqlのインストール
非同期化のため
```bash
docker compose exec demo-app poetry add aiomysql
```

### テスト関連

```bash
docker compose exec demo-app poetry add -G dev pytest-asyncio aiosqlite httpx
```
- テストを実行
```bash
docker compose run --entrypoint "poetry run pytest" demo-app
```

```bash
docker compose run --entrypoint "poetry run pytest -k test_due_date" demo-app
```

### entrypointの設定

- entrypoint.sh 
```bash
# !/bin/bash

# DB migrationを実行する
poetry run python -m api.migrate_cloud_db

# uvicornのサーバーを立ち上げる
poetry run uvicorn api.main:app --host 0.0.0.0
```