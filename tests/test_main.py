import pytest
import pytest_asyncio
import starlette.status
from httpx import AsyncClient, ASGITransport
# from fastapi.testclient import TestClient  # Import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from api.db import get_db, Base
from api.main import app

ASYNC_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    # 非同期対応したDB接続用のengineとsessionを作成
    async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
    async_session = sessionmaker(
        autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
    )

    # テスト用にオンメモリのSQLiteテーブルを初期化（関数ごとにリセット）
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # DIを使ってFastAPIのDBの向き先をテスト用DBに変更
    async def get_test_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = get_test_db

    transport = ASGITransport(app=app)

    # テスト用に非同期HTTPクライアントを返却
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_create_and_read(async_client):
    response = await async_client.post("/tasks", json={"title": "テストタスク"})
    assert response.status_code == starlette.status.HTTP_200_OK
    response_obj = response.json()
    assert response_obj["title"] == "テストタスク"

    response = await async_client.get("/tasks")
    assert response.status_code == starlette.status.HTTP_200_OK
    response_obj = response.json()
    assert len(response_obj) == 1
    assert response_obj[0]["title"] == "テストタスク"
    assert response_obj[0]["done"] is False


@pytest.mark.asyncio
async def test_done_flag(async_client):
    response = await async_client.post("/tasks", json={"title": "テストタスク2"})
    assert response.status_code == starlette.status.HTTP_200_OK
    response_obj = response.json()
    assert response_obj["title"] == "テストタスク2"

    # 完了フラグを立てる
    response = await async_client.put(f"/tasks/1/done")
    assert response.status_code == starlette.status.HTTP_200_OK

    # 既に完了フラグが立ってるので400を返却
    response = await async_client.put(f"/tasks/1/done")
    assert response.status_code == starlette.status.HTTP_400_BAD_REQUEST

    # 完了フラグを外す
    response = await async_client.delete(f"/tasks/1/done")
    assert response.status_code == starlette.status.HTTP_200_OK

    # 完了フラグが外れてるので404を返却
    response = await async_client.delete(f"/tasks/1/done")
    assert response.status_code == starlette.status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input_param, expectation",
    [
        ("2024-12-01", starlette.status.HTTP_200_OK),
        ("2024-12-32", starlette.status.HTTP_422_UNPROCESSABLE_ENTITY),
        ("2024/12/01", starlette.status.HTTP_422_UNPROCESSABLE_ENTITY),
        ("2024-1201", starlette.status.HTTP_422_UNPROCESSABLE_ENTITY)
    ]
)
async def test_due_date(input_param, expectation, async_client):
    response = await async_client.post("/tasks", json={"title": "テストタスク", "due_date": input_param})
    assert response.status_code == expectation
