#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for the report module.
"""

import os
import json
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Import the module to test
from src.report.report import (
    collect_logs,
    create_report,
    send_alert,
    detect_anomalies,
    LogCollector,
    ReportGenerator,
    AlertManager,
    AnomalyDetector,
    ReportFormat,
    AlertLevel,
    AlertChannel
)

# Test data
TEST_LOG_DIR = os.path.join('data', 'report')
TEST_REPORT_TITLE = "Test Report"

@pytest.fixture
def setup_test_dirs():
    """Create temporary directories for test data."""
    os.makedirs(os.path.join('data', 'report', 'generated_reports'), exist_ok=True)
    os.makedirs(os.path.join('data', 'report', 'alerts'), exist_ok=True)
    yield
    # Cleanup could be added here if needed

@pytest.fixture
def sample_logs():
    """Create sample logs for testing."""
    return {
        'market_infomation': [
            {
                'timestamp': '2023-01-01T10:00:00',
                'level': 'INFO',
                'message': 'Successfully fetched stock data for AAPL'
            },
            {
                'timestamp': '2023-01-01T10:05:00',
                'level': 'ERROR',
                'message': 'Failed to fetch news data: API rate limit exceeded'
            }
        ],
        'strategy': [
            {
                'timestamp': '2023-01-01T10:10:00',
                'level': 'INFO',
                'message': 'Strategy test_strategy generated buy signal for AAPL'
            }
        ],
        'trading': [
            {
                'timestamp': '2023-01-01T10:15:00',
                'level': 'INFO',
                'message': 'Order placed: Buy 10 AAPL at $150.00'
            },
            {
                'timestamp': '2023-01-01T10:20:00',
                'level': 'INFO',
                'message': 'Order filled: Buy 10 AAPL at $150.25'
            }
        ]
    }

@pytest.fixture
def sample_market_data():
    """Create sample market data for testing."""
    return {
        'symbols': ['AAPL', 'MSFT', 'GOOGL'],
        'timestamps': [
            '2023-01-01T09:30:00',
            '2023-01-01T09:31:00',
            '2023-01-01T09:32:00'
        ],
        'prices': [
            [150.0, 151.0, 149.5],
            [250.0, 252.0, 251.0],
            [2800.0, 2805.0, 2790.0]
        ]
    }

def test_log_collector():
    """Test the LogCollector class."""
    # Create a log collector
    collector = LogCollector()
    
    # Verify the initialization
    assert hasattr(collector, 'log_dirs')
    assert len(collector.log_dirs) > 0
    
    # Test with custom log directories
    custom_dirs = ['/tmp/logs1', '/tmp/logs2']
    custom_collector = LogCollector(log_dirs=custom_dirs)
    assert custom_collector.log_dirs == custom_dirs

def test_collect_logs():
    """Test the collect_logs function."""
    # Mock the LogCollector.collect_logs method
    with patch('src.report.report.LogCollector.collect_logs') as mock_collect:
        # Configure the mock to return sample data
        mock_collect.return_value = {
            'market_infomation': [{'message': 'test'}],
            'strategy': [{'message': 'test'}]
        }
        
        # Call the function
        logs = collect_logs(start_date='2023-01-01', end_date='2023-01-31')
        
        # Verify the result
        assert isinstance(logs, dict)
        assert 'market_infomation' in logs
        assert 'strategy' in logs
        
        # Verify the mock was called with expected arguments
        mock_collect.assert_called_once_with('2023-01-01', '2023-01-31')

def test_report_generator(setup_test_dirs):
    """Test the ReportGenerator class."""
    # Create a report generator
    generator = ReportGenerator()
    
    # Verify the initialization
    assert hasattr(generator, 'output_dir')
    assert os.path.exists(generator.output_dir)
    
    # Test with custom output directory
    custom_dir = '/tmp/reports'
    custom_generator = ReportGenerator(output_dir=custom_dir)
    assert custom_generator.output_dir == custom_dir

def test_create_report(sample_logs, setup_test_dirs):
    """Test the create_report function."""
    # Mock the ReportGenerator.create_report method
    with patch('src.report.report.ReportGenerator.create_report') as mock_create:
        # Configure the mock to return a file path
        mock_create.return_value = os.path.join('data', 'report', 'generated_reports', 'test_report.html')
        
        # Call the function
        report_path = create_report(
            data=sample_logs,
            report_format=ReportFormat.HTML,
            title=TEST_REPORT_TITLE
        )
        
        # Verify the result
        assert isinstance(report_path, str)
        assert report_path.endswith('.html')
        
        # Verify the mock was called with expected arguments
        mock_create.assert_called_once()

def test_alert_manager():
    """Test the AlertManager class."""
    # Create an alert manager
    manager = AlertManager()
    
    # Verify the initialization
    assert hasattr(manager, 'config')
    
    # Test with custom configuration
    custom_config = {
        'email': {
            'smtp_server': 'smtp.example.com',
            'smtp_port': 587,
            'sender': 'alerts@example.com',
            'recipients': ['user@example.com']
        }
    }
    custom_manager = AlertManager(config=custom_config)
    assert custom_manager.config == custom_config

def test_send_alert():
    """Test the send_alert function."""
    # Mock the AlertManager.send_alert method
    with patch('src.report.report.AlertManager.send_alert') as mock_send:
        # Configure the mock to return success status
        mock_send.return_value = {
            'console': True,
            'email': False
        }
        
        # Call the function
        result = send_alert(
            message="Test alert message",
            level=AlertLevel.WARNING,
            channels=[AlertChannel.CONSOLE, AlertChannel.EMAIL]
        )
        
        # Verify the result
        assert isinstance(result, dict)
        assert 'console' in result
        assert 'email' in result
        
        # Verify the mock was called with expected arguments
        mock_send.assert_called_once()

def test_anomaly_detector():
    """Test the AnomalyDetector class."""
    # Create an anomaly detector
    detector = AnomalyDetector()
    
    # Verify the initialization
    assert hasattr(detector, 'thresholds')
    assert len(detector.thresholds) > 0
    
    # Test with custom thresholds
    custom_thresholds = {
        'error_count': 10,
        'api_latency': 5.0
    }
    custom_detector = AnomalyDetector(thresholds=custom_thresholds)
    assert custom_detector.thresholds['error_count'] == 10
    assert custom_detector.thresholds['api_latency'] == 5.0

def test_detect_anomalies(sample_logs, sample_market_data):
    """Test the detect_anomalies function."""
    # Prepare test data
    data = {
        'logs': sample_logs,
        'market_data': sample_market_data,
        'api_metrics': {
            'endpoints': ['/market/data', '/orders'],
            'latencies': [0.2, 3.0],  # Second endpoint has high latency
            'error_rates': [0.0, 0.2]  # Second endpoint has high error rate
        },
        'system_metrics': {
            'cpu_usage': 95.0,  # High CPU usage
            'memory_usage': 80.0,
            'disk_usage': 70.0
        }
    }
    
    # Mock the AnomalyDetector.detect_anomalies method
    with patch('src.report.report.AnomalyDetector.detect_anomalies') as mock_detect:
        # Configure the mock to return anomalies
        mock_detect.return_value = [
            {
                'type': 'api_latency',
                'endpoint': '/orders',
                'latency': 3.0,
                'threshold': 2.0,
                'description': 'High API latency for /orders: 3.00s'
            },
            {
                'type': 'high_cpu_usage',
                'usage': 95.0,
                'threshold': 90.0,
                'description': 'High CPU usage: 95.0%'
            }
        ]
        
        # Call the function
        anomalies = detect_anomalies(data)
        
        # Verify the result
        assert isinstance(anomalies, list)
        assert len(anomalies) == 2
        assert anomalies[0]['type'] == 'api_latency'
        assert anomalies[1]['type'] == 'high_cpu_usage'
        
        # Verify the mock was called with expected arguments
        mock_detect.assert_called_once_with(data)