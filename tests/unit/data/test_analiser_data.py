import pytest
from datetime import date
from unittest.mock import AsyncMock

from analyzerservice.data import report_generator


@pytest.mark.asyncio
async def test_set_ai_analysis(mocker):
    mock_session = AsyncMock()
    mocker.patch("analyzerservice.data.report_generator.async_session", return_value=mock_session)
    test_date = date(2024, 5, 16)
    test_analysis = "Test analysis text"

    async with mock_session as session:
        await report_generator.set_ai_analysis(test_date, test_analysis)
        session.add.assert_called_once()
        session.commit.assert_awaited_once()