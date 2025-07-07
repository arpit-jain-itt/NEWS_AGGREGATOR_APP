import pytest
from unittest.mock import patch
from datetime import datetime
from server.models.report_model import Report

ADMIN_HEADERS = {"X-User-ID": "1"}


@pytest.fixture
def fake_reports_state():
    now = datetime.now().isoformat()
    return [
        Report(
            id=1,
            user_id=1,
            article_id=10,
            reason="spam",
            created_at=now,
            status="pending",
        ),
        Report(
            id=2,
            user_id=2,
            article_id=10,
            reason="offensive",
            created_at=now,
            status="reviewed",
        ),
    ]


def test_article_reports(client, fake_reports_state):
    with patch(
        "server.services.admin_service.AdminService.get_reports_for_article",
        return_value=fake_reports_state,
    ):
        res = client.get("/api/admin/reports/10", headers=ADMIN_HEADERS)
        print("\ntest_article_reports:", res.get_json())
        data = res.get_json()["data"]
        print(
            "Reports after fetch:",
            [(r.article_id, r.reason) for r in fake_reports_state],
        )
        assert res.status_code == 200
        assert isinstance(data, list)
        assert data[0]["article_id"] == 10
        assert data[0]["reason"] == "spam"
