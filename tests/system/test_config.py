#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for the system config module.
"""

import os
import json
import pytest
import tempfile
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Import the module to test
from src.system.config import (
    load_env,
    get_config,
    get_api_key,
    get_environment,
    is_development,
    is_testing,
    is_production,
    create_example_env_file,
    ConfigManager,
    SystemConfig,
    Environment,
    Constants
)

# Test data
TEST_ENV_CONTENT = """
# Environment
ENVIRONMENT=development

# API Keys
ALPHA_VANTAGE_API_KEY=test_alpha_vantage_key
NEWSAPI_API_KEY=test_newsapi_key

# Database
DB_HOST=localhost
DB_PORT=5432
"""

TEST_CONFIG_DATA = {
    "environment": "development",
    "debug": True,
    "log_level": "INFO",
    "data_dir": "data",
    "api_keys": {
        "alpha_vantage": "test_alpha_vantage_key",
        "newsapi": "test_newsapi_key"
    },
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "trading_system",
        "user": "user",
        "password": "password"
    },
    "trading": {
        "mode": "paper",
        "max_position_value": 100000,
        "default_order_size": 100
    },
    "reporting": {
        "format": "html",
        "enable_email_alerts": False
    }
}

@pytest.fixture
def temp_env_file():
    """Create a temporary .env file for testing."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        f.write(TEST_ENV_CONTENT)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)

@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create base.json
        with open(os.path.join(temp_dir, 'base.json'), 'w') as f:
            json.dump(TEST_CONFIG_DATA, f)
        
        # Create development.json with some overrides
        dev_config = {
            "debug": True,
            "log_level": "DEBUG"
        }
        with open(os.path.join(temp_dir, 'development.json'), 'w') as f:
            json.dump(dev_config, f)
        
        # Create production.json with some overrides
        prod_config = {
            "environment": "production",
            "debug": False,
            "log_level": "WARNING"
        }
        with open(os.path.join(temp_dir, 'production.json'), 'w') as f:
            json.dump(prod_config, f)
        
        yield temp_dir

def test_load_env(temp_env_file):
    """Test the load_env function."""
    # Mock the ConfigManager.load_env method
    with patch('src.system.config.ConfigManager.load_env') as mock_load:
        # Configure the mock to return success
        mock_load.return_value = True
        
        # Call the function
        result = load_env(env_file=temp_env_file)
        
        # Verify the result
        assert result is True
        
        # Verify the mock was called with expected arguments
        mock_load.assert_called_once()

def test_config_manager_load_env(temp_env_file):
    """Test the ConfigManager.load_env method."""
    # Create a config manager with the temporary .env file
    manager = ConfigManager(env_file=temp_env_file)
    
    # Call the method
    result = manager.load_env()
    
    # Verify the result
    assert result is True
    
    # Verify that environment variables were loaded
    assert os.environ.get('ENVIRONMENT') == 'development'
    assert os.environ.get('ALPHA_VANTAGE_API_KEY') == 'test_alpha_vantage_key'
    assert os.environ.get('NEWSAPI_API_KEY') == 'test_newsapi_key'

def test_get_environment():
    """Test the get_environment function."""
    # Mock the ConfigManager.environment property
    with patch('src.system.config.ConfigManager.environment', 
              Environment.DEVELOPMENT):
        # Call the function
        env = get_environment()
        
        # Verify the result
        assert env == Environment.DEVELOPMENT

def test_is_development():
    """Test the is_development function."""
    # Mock the get_environment function
    with patch('src.system.config.get_environment') as mock_get:
        # Configure the mock to return development
        mock_get.return_value = Environment.DEVELOPMENT
        
        # Call the function
        result = is_development()
        
        # Verify the result
        assert result is True
        
        # Verify the mock was called
        mock_get.assert_called_once()

def test_is_testing():
    """Test the is_testing function."""
    # Mock the get_environment function
    with patch('src.system.config.get_environment') as mock_get:
        # Configure the mock to return testing
        mock_get.return_value = Environment.TESTING
        
        # Call the function
        result = is_testing()
        
        # Verify the result
        assert result is True
        
        # Verify the mock was called
        mock_get.assert_called_once()

def test_is_production():
    """Test the is_production function."""
    # Mock the get_environment function
    with patch('src.system.config.get_environment') as mock_get:
        # Configure the mock to return production
        mock_get.return_value = Environment.PRODUCTION
        
        # Call the function
        result = is_production()
        
        # Verify the result
        assert result is True
        
        # Verify the mock was called
        mock_get.assert_called_once()

def test_get_config():
    """Test the get_config function."""
    # Create a sample config
    sample_config = SystemConfig(
        environment=Environment.DEVELOPMENT,
        debug=True,
        log_level="INFO",
        data_dir="data",
        api_keys={"alpha_vantage": "test_key"},
        database={"host": "localhost"},
        trading={"mode": "paper"},
        reporting={"format": "html"}
    )
    
    # Mock the ConfigManager.get_config method
    with patch('src.system.config.ConfigManager.get_config') as mock_get:
        # Configure the mock to return the sample config
        mock_get.return_value = sample_config
        
        # Call the function
        config = get_config()
        
        # Verify the result
        assert config == sample_config
        
        # Verify the mock was called
        mock_get.assert_called_once()

def test_get_api_key():
    """Test the get_api_key function."""
    # Mock the ConfigManager.get_api_key method
    with patch('src.system.config.ConfigManager.get_api_key') as mock_get:
        # Configure the mock to return a key
        mock_get.return_value = "test_api_key"
        
        # Call the function
        key = get_api_key("alpha_vantage")
        
        # Verify the result
        assert key == "test_api_key"
        
        # Verify the mock was called with expected arguments
        mock_get.assert_called_once_with("alpha_vantage")

def test_config_manager_get_api_key(temp_env_file):
    """Test the ConfigManager.get_api_key method."""
    # Create a config manager with the temporary .env file
    manager = ConfigManager(env_file=temp_env_file)
    
    # Load environment variables
    manager.load_env()
    
    # Test getting an API key from environment variables
    key = manager.get_api_key("alpha_vantage")
    assert key == "test_alpha_vantage_key"
    
    # Test getting a non-existent API key
    key = manager.get_api_key("non_existent")
    assert key is None

def test_system_config_from_dict():
    """Test the SystemConfig.from_dict method."""
    # Call the method
    config = SystemConfig.from_dict(TEST_CONFIG_DATA)
    
    # Verify the result
    assert isinstance(config, SystemConfig)
    assert config.environment == Environment.DEVELOPMENT
    assert config.debug is True
    assert config.log_level == "INFO"
    assert "alpha_vantage" in config.api_keys
    assert config.api_keys["alpha_vantage"] == "test_alpha_vantage_key"

def test_config_manager_load_config(temp_config_dir):
    """Test the ConfigManager._load_config method."""
    # Create a config manager with the temporary config directory
    with patch.object(ConfigManager, '_get_environment', 
                     return_value=Environment.DEVELOPMENT):
        manager = ConfigManager(config_dir=temp_config_dir)
        
        # Call the method
        config = manager._load_config()
        
        # Verify the result
        assert isinstance(config, SystemConfig)
        assert config.environment == Environment.DEVELOPMENT
        assert config.debug is True
        assert config.log_level == "DEBUG"  # Overridden in development.json
        
        # Test with production environment
        with patch.object(ConfigManager, '_get_environment', 
                         return_value=Environment.PRODUCTION):
            manager = ConfigManager(config_dir=temp_config_dir)
            config = manager._load_config()
            
            assert config.environment == Environment.PRODUCTION
            assert config.debug is False
            assert config.log_level == "WARNING"

def test_create_example_env_file():
    """Test the create_example_env_file function."""
    # Create a temporary file path
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_path = f.name
    
    try:
        # Call the function
        create_example_env_file(output_path=temp_path)
        
        # Verify the file was created
        assert os.path.exists(temp_path)
        
        # Verify the file content
        with open(temp_path, 'r') as f:
            content = f.read()
            assert "ENVIRONMENT=" in content
            assert "API Keys" in content
            assert "Database" in content
    
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def test_constants():
    """Test the Constants class."""
    # Verify some constants
    assert Constants.SECONDS_PER_MINUTE == 60
    assert Constants.SECONDS_PER_HOUR == 3600
    assert Constants.SECONDS_PER_DAY == 86400
    
    # Verify market hours
    assert 0 <= Constants.MARKET_OPEN_HOUR_JST < 24
    assert 0 <= Constants.MARKET_CLOSE_HOUR_JST < 24
    assert 0 <= Constants.MARKET_OPEN_HOUR_US < 24
    assert 0 <= Constants.MARKET_CLOSE_HOUR_US < 24
    
    # Verify data directories
    assert Constants.MARKET_DATA_DIR.startswith('data')
    assert Constants.STRATEGY_DATA_DIR.startswith('data')
    assert Constants.EVALUATION_DATA_DIR.startswith('data')
    assert Constants.TRADING_DATA_DIR.startswith('data')
    assert Constants.REPORT_DATA_DIR.startswith('data')