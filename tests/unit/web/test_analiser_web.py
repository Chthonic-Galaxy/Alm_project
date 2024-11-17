import pytest
from fastapi import HTTPException
from datetime import date
from analyzerservice.web import report_generation_api


@pytest.mark.asyncio
async def test_trigger_report_generation_error(mocker):
    """Tests error handling during report generation triggering."""
    mocker.patch("analyzerservice.src.celery_app.generate_report_task.delay", side_effect=Exception("Test Exception"))
    target_date = date(2024, 5, 16)
    with pytest.raises(HTTPException) as exc_info:
        await report_generation_api.trigger_report_generation(target_date)
    assert exc_info.value.status_code == 500
    assert "Ошибка при запуске задачи: Test Exception" in exc_info.value.detail