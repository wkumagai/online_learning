#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration module for loading environment variables and system settings.
This module handles environment variables, configuration files, and system constants.
"""

import os
import json
import logging
import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from pathlib import Path

# Try to import dotenv for .env file loading
try:
    from dotenv import load_dotenv
except ImportError:
    # Create a simple fallback if python-dotenv is not installed
    def load_dotenv(dotenv_path=None):
        """Simple fallback for dotenv.load_dotenv."""
        if dotenv_path is None:
            dotenv_path = '.env'
        
        if not os.path.exists(dotenv_path):
            return False
        
        with open(dotenv_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
        
        return True

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('data', 'system', 'config.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Environment(str, Enum):
    """Enum for environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

@dataclass
class SystemConfig:
    """Class representing system configuration."""
    environment: Environment
    debug: bool
    log_level: str
    data_dir: str
    api_keys: Dict[str, str]
    database: Dict[str, Any]
    trading: Dict[str, Any]
    reporting: Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemConfig':
        """Create a SystemConfig instance from a dictionary."""
        # Convert environment string to enum
        if 'environment' in data and isinstance(data['environment'], str):
            data['environment'] = Environment(data['environment'])
        
        return cls(**data)

class ConfigManager:
    """Class for managing system configuration."""
    
    def __init__(self, env_file: str = '.env', config_dir: str = None):
        """
        Initialize the configuration manager.
        
        Args:
            env_file: Path to the .env file
            config_dir: Directory containing configuration files
        """
        self.env_file = env_file
        
        if config_dir is None:
            self.config_dir = os.path.join('src', 'system', 'config')
        else:
            self.config_dir = config_dir
        
        # Load environment variables
        self.load_env()
        
        # Set current environment
        self.environment = self._get_environment()
        
        # Load configuration
        self.config = self._load_config()
        
        logger.info(f"Initialized ConfigManager with environment: {self.environment.value}")
    
    def load_env(self) -> bool:
        """
        Load environment variables from .env file.
        
        Returns:
            True if .env file was loaded successfully, False otherwise
        """
        # Check if .env file exists
        if not os.path.exists(self.env_file):
            logger.warning(f".env file not found: {self.env_file}")
            return False
        
        # Load environment variables from .env file
        result = load_dotenv(self.env_file)
        
        if result:
            logger.info(f"Loaded environment variables from {self.env_file}")
        else:
            logger.warning(f"Failed to load environment variables from {self.env_file}")
        
        return result
    
    def _get_environment(self) -> Environment:
        """
        Get the current environment.
        
        Returns:
            Current environment (development, testing, or production)
        """
        # Get environment from environment variable
        env_str = os.environ.get('ENVIRONMENT', 'development').lower()
        
        # Map environment string to enum
        if env_str in ['prod', 'production']:
            return Environment.PRODUCTION
        elif env_str in ['test', 'testing']:
            return Environment.TESTING
        else:
            return Environment.DEVELOPMENT
    
    def _load_config(self) -> SystemConfig:
        """
        Load configuration based on current environment.
        
        Returns:
            SystemConfig instance
        """
        # Base configuration
        base_config = self._load_config_file('base.json')
        
        # Environment-specific configuration
        env_config = self._load_config_file(f"{self.environment.value}.json")
        
        # Merge configurations
        config_data = self._merge_configs(base_config, env_config)
        
        # Set environment
        config_data['environment'] = self.environment
        
        # Create SystemConfig instance
        return SystemConfig.from_dict(config_data)
    
    def _load_config_file(self, filename: str) -> Dict[str, Any]:
        """
        Load a configuration file.
        
        Args:
            filename: Name of the configuration file
        
        Returns:
            Dictionary containing configuration data
        """
        file_path = os.path.join(self.config_dir, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            logger.warning(f"Configuration file not found: {file_path}")
            return {}
        
        try:
            # Load JSON configuration
            with open(file_path, 'r') as f:
                config_data = json.load(f)
            
            logger.info(f"Loaded configuration from {file_path}")
            return config_data
        
        except Exception as e:
            logger.error(f"Error loading configuration from {file_path}: {str(e)}")
            return {}
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge two configuration dictionaries.
        
        Args:
            base: Base configuration
            override: Configuration to override base
        
        Returns:
            Merged configuration
        """
        result = base.copy()
        
        for key, value in override.items():
            # If both values are dictionaries, merge them recursively
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                # Otherwise, override the value
                result[key] = value
        
        return result
    
    def get_config(self) -> SystemConfig:
        """
        Get the current system configuration.
        
        Returns:
            SystemConfig instance
        """
        return self.config
    
    def get_api_key(self, service: str) -> Optional[str]:
        """
        Get an API key for a specific service.
        
        Args:
            service: Name of the service
        
        Returns:
            API key or None if not found
        """
        # Check if API key is in configuration
        if hasattr(self.config, 'api_keys') and service in self.config.api_keys:
            return self.config.api_keys[service]
        
        # Check if API key is in environment variables
        env_var = f"{service.upper()}_API_KEY"
        return os.environ.get(env_var)
    
    def is_development(self) -> bool:
        """Check if current environment is development."""
        return self.environment == Environment.DEVELOPMENT
    
    def is_testing(self) -> bool:
        """Check if current environment is testing."""
        return self.environment == Environment.TESTING
    
    def is_production(self) -> bool:
        """Check if current environment is production."""
        return self.environment == Environment.PRODUCTION

# System constants
class Constants:
    """Class containing system constants."""
    
    # Time constants
    SECONDS_PER_MINUTE = 60
    SECONDS_PER_HOUR = 3600
    SECONDS_PER_DAY = 86400
    
    # Market hours (UTC)
    MARKET_OPEN_HOUR_JST = 9  # 9:00 AM JST
    MARKET_CLOSE_HOUR_JST = 15  # 3:00 PM JST
    MARKET_OPEN_HOUR_US = 9  # 9:30 AM EST
    MARKET_CLOSE_HOUR_US = 16  # 4:00 PM EST
    
    # Data directories
    MARKET_DATA_DIR = os.path.join('data', 'market_infomation')
    STRATEGY_DATA_DIR = os.path.join('data', 'strategy')
    EVALUATION_DATA_DIR = os.path.join('data', 'evaluation')
    TRADING_DATA_DIR = os.path.join('data', 'trading')
    REPORT_DATA_DIR = os.path.join('data', 'report')
    
    # File patterns
    STOCK_DATA_PATTERN = "{symbol}_{date}.csv"
    NEWS_DATA_PATTERN = "news_{date}.json"
    MODEL_FILE_PATTERN = "{strategy_name}_{version}.pkl"
    
    # API endpoints
    STOCK_API_ENDPOINT = "https://api.example.com/stocks"
    NEWS_API_ENDPOINT = "https://api.example.com/news"
    
    # Trading parameters
    DEFAULT_ORDER_SIZE = 100
    MAX_ORDER_SIZE = 1000
    MAX_POSITION_VALUE = 100000
    
    # Evaluation parameters
    DEFAULT_BACKTEST_PERIOD_DAYS = 30
    MAX_BACKTEST_PERIOD_DAYS = 365
    
    # Reporting parameters
    DEFAULT_REPORT_FORMAT = "html"
    REPORT_RETENTION_DAYS = 30

def load_env(env_file: str = '.env') -> bool:
    """
    Load environment variables from .env file.
    
    Args:
        env_file: Path to the .env file
    
    Returns:
        True if .env file was loaded successfully, False otherwise
    """
    config_manager = ConfigManager(env_file=env_file)
    return config_manager.load_env()

def get_config() -> SystemConfig:
    """
    Get the current system configuration.
    
    Returns:
        SystemConfig instance
    """
    config_manager = ConfigManager()
    return config_manager.get_config()

def get_api_key(service: str) -> Optional[str]:
    """
    Get an API key for a specific service.
    
    Args:
        service: Name of the service
    
    Returns:
        API key or None if not found
    """
    config_manager = ConfigManager()
    return config_manager.get_api_key(service)

def get_environment() -> Environment:
    """
    Get the current environment.
    
    Returns:
        Current environment (development, testing, or production)
    """
    config_manager = ConfigManager()
    return config_manager.environment

def is_development() -> bool:
    """Check if current environment is development."""
    return get_environment() == Environment.DEVELOPMENT

def is_testing() -> bool:
    """Check if current environment is testing."""
    return get_environment() == Environment.TESTING

def is_production() -> bool:
    """Check if current environment is production."""
    return get_environment() == Environment.PRODUCTION

def create_example_env_file(output_path: str = '.env.example') -> None:
    """
    Create an example .env file.
    
    Args:
        output_path: Path to the output file
    """
    example_content = """# Environment
ENVIRONMENT=development  # development, testing, production

# API Keys
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
NEWSAPI_API_KEY=your_newsapi_api_key
TRADING_API_KEY=your_trading_api_key
TRADING_API_SECRET=your_trading_api_secret

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trading_system
DB_USER=user
DB_PASSWORD=password

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Trading
TRADING_MODE=paper  # paper, live
MAX_POSITION_VALUE=100000
DEFAULT_ORDER_SIZE=100

# Reporting
REPORT_FORMAT=html  # html, pdf, json, csv
ENABLE_EMAIL_ALERTS=false
EMAIL_SENDER=alerts@example.com
EMAIL_RECIPIENTS=user@example.com
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=username
SMTP_PASSWORD=password
"""
    
    with open(output_path, 'w') as f:
        f.write(example_content)
    
    logger.info(f"Created example .env file at {output_path}")

# Example usage
if __name__ == "__main__":
    # Load environment variables
    load_env()
    
    # Get current environment
    env = get_environment()
    print(f"Current environment: {env.value}")
    
    # Check environment type
    if is_development():
        print("Running in development mode")
    elif is_testing():
        print("Running in testing mode")
    elif is_production():
        print("Running in production mode")
    
    # Get system configuration
    config = get_config()
    print(f"Debug mode: {config.debug}")
    print(f"Log level: {config.log_level}")
    
    # Get API key
    alpha_vantage_key = get_api_key('alpha_vantage')
    if alpha_vantage_key:
        print(f"Alpha Vantage API key: {alpha_vantage_key[:4]}...")
    else:
        print("Alpha Vantage API key not found")
    
    # Create example .env file
    create_example_env_file()