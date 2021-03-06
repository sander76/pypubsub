import asyncio
import logging
from unittest.mock import Mock
import pytest

from aiosubpub import Channel

_LOGGER = logging.getLogger(__name__)


@pytest.fixture
def dummy_message():
    return "a dummy message"


class MockedCallback:
    def __init__(self):
        self.mock = Mock()

    def __call__(self, *args, **kwargs):
        self.mock(*args, **kwargs)


@pytest.fixture
def mock_callback():
    return MockedCallback()


@pytest.mark.asyncio
async def test_pubsub_callback_success(dummy_message, mock_callback: MockedCallback):
    dummy_channel = Channel("dummy channel")

    subscription = dummy_channel.subscribe(mock_callback)

    dummy_channel.publish(dummy_message)
    await asyncio.sleep(0.1)
    mock_callback.mock.assert_called_once_with(dummy_message)
    subscription.cancel()


@pytest.mark.asyncio
async def test_channel_list(mock_callback: MockedCallback):
    """Assert the subscription list is empty when starting a channel"""
    dummy_channel = Channel("dummy channel")
    assert len(dummy_channel.subscriptions) == 0


@pytest.mark.asyncio
async def test_channel_subscriptions(mock_callback):
    dummy_channel = Channel("dummy channel")

    sub1 = dummy_channel.subscribe(mock_callback)
    sub2 = dummy_channel.subscribe(mock_callback)

    assert len(dummy_channel.subscriptions) == 2

    sub1.cancel()
    sub2.cancel()


@pytest.mark.asyncio
async def test_channel_unsubscribe_no_watch(mock_callback):
    """Test subscription after unsubscribe.

    This test cancels the subscription before the watching starts.
    """
    dummy_channel = Channel("dummy channel")
    subscription_task = dummy_channel.subscribe(mock_callback)
    assert len(dummy_channel.subscriptions) == 1

    subscription_task.cancel()
    await asyncio.sleep(0.1)
    assert len(dummy_channel.subscriptions) == 0


@pytest.mark.asyncio
async def test_channel_unsubscribe_watch(mock_callback):
    """Test subscription after unsubscribe."""

    dummy_channel = Channel("dummy channel")
    subscription_task = dummy_channel.subscribe(mock_callback)
    assert len(dummy_channel.subscriptions) == 1

    await asyncio.sleep(0.1)
    subscription_task.cancel()
    await asyncio.sleep(0.1)
    assert len(dummy_channel.subscriptions) == 0


@pytest.mark.asyncio
async def test_custom_subscription(dummy_message):
    """Test a custom subscription"""

    channel = Channel("dummy channel")

    subscription = channel.get_subscription()

    async def _custom_subscriber():
        with subscription as sub:
            result = await sub.get()
            return result

    channel.publish(dummy_message)

    result = await _custom_subscriber()
    assert result == dummy_message
