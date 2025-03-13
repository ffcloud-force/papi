import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from backend.llm_apis.openai_client import OpenAiClient

@pytest.fixture
def openai_client():
    client = OpenAiClient()
    yield client
    # Make sure to close any resources if needed
    if hasattr(client, 'close'):
        client.close()

def create_mock_completion(content="This is a mock response"):
    """Helper function to create a mock completion response"""
    mock_choice = MagicMock()
    mock_choice.message.content = content
    
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    
    return mock_completion

def create_async_mock_completion(content="This is a mock async response"):
    """Helper function to create a mock async completion response"""
    mock_choice = MagicMock()
    mock_choice.message.content = content
    
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    
    return mock_completion

@pytest.mark.asyncio
async def test_get_completion_async(openai_client):
    """Test the asynchronous completion method with mocked response"""
    # Create test message
    test_messages = [{"role": "user", "content": "Hello, how are you?"}]
    
    # Mock the async client's create method
    with patch.object(
        openai_client.async_client.chat.completions,
        'create',
        new_callable=AsyncMock
    ) as mock_create:
        # Configure the mock to return a predefined response
        mock_create.return_value = create_async_mock_completion("I'm doing well, thank you!")
        
        # Call the method being tested
        result = await openai_client.get_completion_async(test_messages, model="gpt-4o-mini")
        
        # Verify the result
        assert result.choices[0].message.content == "I'm doing well, thank you!"
        
        # Verify the mock was called with correct parameters
        mock_create.assert_called_once_with(messages=test_messages, model="gpt-4o-mini")

def test_get_completion(openai_client):
    """Test the synchronous completion method with mocked response"""
    # Create test message
    test_messages = [{"role": "user", "content": "Hello, how are you?"}]
    
    # Mock the synchronous client's create method
    with patch.object(
        openai_client.client.chat.completions,
        'create',
        return_value=create_mock_completion("I'm fine, how about you?")
    ) as mock_create:
        # Call the method being tested
        result = openai_client.get_completion(test_messages, model="gpt-4o-mini")
        
        # Verify the result
        assert result.choices[0].message.content == "I'm fine, how about you?"
        
        # Verify the mock was called with correct parameters
        mock_create.assert_called_once_with(messages=test_messages, model="gpt-4o-mini")

@pytest.mark.asyncio
async def test_get_completion_async_with_different_model(openai_client):
    """Test the async completion with a different model parameter"""
    test_messages = [{"role": "user", "content": "Tell me a joke"}]
    
    with patch.object(
        openai_client.async_client.chat.completions,
        'create',
        new_callable=AsyncMock
    ) as mock_create:
        mock_create.return_value = create_async_mock_completion("Why did the chicken cross the road?")
        
        result = await openai_client.get_completion_async(test_messages, model="gpt-4")
        
        assert result.choices[0].message.content == "Why did the chicken cross the road?"
        mock_create.assert_called_once_with(messages=test_messages, model="gpt-4")

def test_get_completion_handles_error(openai_client):
    """Test that the synchronous method properly handles errors"""
    test_messages = [{"role": "user", "content": "Hello"}]
    
    with patch.object(
        openai_client.client.chat.completions,
        'create',
        side_effect=Exception("API Error")
    ) as mock_create:
        # Use pytest's raises context manager to verify exception handling
        with pytest.raises(Exception) as excinfo:
            openai_client.get_completion(test_messages)
        
        assert "API Error" in str(excinfo.value)
        mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_get_completion_async_handles_error(openai_client):
    """Test that the asynchronous method properly handles errors"""
    test_messages = [{"role": "user", "content": "Hello"}]
    
    with patch.object(
        openai_client.async_client.chat.completions,
        'create',
        new_callable=AsyncMock,
        side_effect=Exception("Async API Error")
    ) as mock_create:
        with pytest.raises(Exception) as excinfo:
            await openai_client.get_completion_async(test_messages)
        
        assert "Async API Error" in str(excinfo.value)
        mock_create.assert_called_once()

# Integration tests - these will make actual API calls
# Only run these when specifically needed, and with proper API keys configured
@pytest.mark.integration
@pytest.mark.skipif(True, reason="Skipping integration test to avoid actual API calls")
def test_integration_get_completion(openai_client):
    """Integration test for synchronous completion"""
    result = openai_client.get_completion([{"role": "user", "content": "Say 'integration test'"}])
    assert result is not None
    assert result.choices[0].message.content is not None

@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(True, reason="Skipping integration test to avoid actual API calls")
async def test_integration_get_completion_async(openai_client):
    """Integration test for asynchronous completion"""
    result = await openai_client.get_completion_async([{"role": "user", "content": "Say 'async integration test'"}])
    assert result is not None
    assert result.choices[0].message.content is not None
