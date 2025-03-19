#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Report module for generating reports, sending alerts, and detecting anomalies.
This module handles log collection, report generation, alert notifications, and system monitoring.
"""

import os
import re
import json
import time
import logging
import smtplib
import datetime
import requests
import pandas as pd
import numpy as np
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('data', 'report', 'report.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ReportFormat(str, Enum):
    """Enum for report formats."""
    HTML = "html"
    PDF = "pdf"
    JSON = "json"
    CSV = "csv"

class AlertLevel(str, Enum):
    """Enum for alert levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertChannel(str, Enum):
    """Enum for alert channels."""
    EMAIL = "email"
    SLACK = "slack"
    SMS = "sms"
    CONSOLE = "console"

class LogCollector:
    """Class for collecting and aggregating logs from different modules."""
    
    def __init__(self, log_dirs: List[str] = None):
        """
        Initialize the log collector.
        
        Args:
            log_dirs: List of directories containing log files
        """
        if log_dirs is None:
            # Default log directories
            self.log_dirs = [
                os.path.join('data', 'market_infomation'),
                os.path.join('data', 'strategy', 'logs'),
                os.path.join('data', 'evaluation'),
                os.path.join('data', 'trading', 'order_logs'),
                os.path.join('data', 'report')
            ]
        else:
            self.log_dirs = log_dirs
        
        logger.info(f"Initialized LogCollector with directories: {self.log_dirs}")
    
    def collect_logs(self, start_date: Optional[str] = None, 
                    end_date: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Collect logs from all configured directories.
        
        Args:
            start_date: Start date for log collection (YYYY-MM-DD)
            end_date: End date for log collection (YYYY-MM-DD)
        
        Returns:
            Dictionary mapping module names to lists of log entries
        """
        if start_date is None:
            # Default to today
            start_date = datetime.datetime.now().strftime('%Y-%m-%d')
        
        if end_date is None:
            # Default to today
            end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Collecting logs from {start_date} to {end_date}")
        
        # Convert dates to datetime objects for comparison
        start_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        
        # Dictionary to store logs by module
        logs_by_module = {}
        
        # Process each log directory
        for log_dir in self.log_dirs:
            if not os.path.exists(log_dir):
                logger.warning(f"Log directory does not exist: {log_dir}")
                continue
            
            # Extract module name from directory path
            module_name = os.path.basename(log_dir)
            logs_by_module[module_name] = []
            
            # Process log files in the directory
            for filename in os.listdir(log_dir):
                # Check if the file is a log file
                if self._is_log_file(filename):
                    file_path = os.path.join(log_dir, filename)
                    
                    # Extract date from filename if possible
                    file_date = self._extract_date_from_filename(filename)
                    
                    # Skip files outside the date range if date is available
                    if file_date is not None:
                        file_dt = datetime.datetime.strptime(file_date, '%Y-%m-%d')
                        if file_dt < start_dt or file_dt > end_dt:
                            continue
                    
                    # Process the log file
                    logs = self._process_log_file(file_path, module_name)
                    
                    # Filter logs by date if needed
                    if logs and file_date is None:
                        logs = self._filter_logs_by_date(logs, start_dt, end_dt)
                    
                    # Add logs to the module's list
                    logs_by_module[module_name].extend(logs)
        
        # Count logs by module
        for module, logs in logs_by_module.items():
            logger.info(f"Collected {len(logs)} logs for module {module}")
        
        return logs_by_module
    
    def _is_log_file(self, filename: str) -> bool:
        """Check if a file is a log file based on extension."""
        return filename.endswith('.log') or filename.endswith('.json')
    
    def _extract_date_from_filename(self, filename: str) -> Optional[str]:
        """Extract date from filename if present."""
        # Look for YYYY-MM-DD pattern in filename
        match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
        if match:
            return match.group(1)
        return None
    
    def _process_log_file(self, file_path: str, module_name: str) -> List[Dict[str, Any]]:
        """Process a log file and extract log entries."""
        logs = []
        
        try:
            # Handle JSON log files
            if file_path.endswith('.json'):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Handle different JSON formats
                if isinstance(data, list):
                    # List of log entries
                    for entry in data:
                        entry['module'] = module_name
                        logs.append(entry)
                elif isinstance(data, dict):
                    # Single log entry or dictionary of entries
                    for key, value in data.items():
                        if isinstance(value, dict):
                            value['module'] = module_name
                            logs.append(value)
                        else:
                            # Create a log entry with the key-value pair
                            logs.append({
                                'module': module_name,
                                'key': key,
                                'value': value,
                                'timestamp': datetime.datetime.now().isoformat()
                            })
            
            # Handle text log files
            else:
                with open(file_path, 'r') as f:
                    for line in f:
                        # Parse log line (assuming standard format)
                        log_entry = self._parse_log_line(line, module_name)
                        if log_entry:
                            logs.append(log_entry)
        
        except Exception as e:
            logger.error(f"Error processing log file {file_path}: {str(e)}")
        
        return logs
    
    def _parse_log_line(self, line: str, module_name: str) -> Optional[Dict[str, Any]]:
        """Parse a log line into a structured log entry."""
        # Skip empty lines
        if not line.strip():
            return None
        
        try:
            # Try to match standard log format: timestamp - name - level - message
            match = re.match(
                r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) - (\w+) - (.*)',
                line
            )
            
            if match:
                timestamp, name, level, message = match.groups()
                return {
                    'timestamp': timestamp,
                    'name': name,
                    'level': level,
                    'message': message,
                    'module': module_name
                }
            
            # Fallback: just store the raw line
            return {
                'timestamp': datetime.datetime.now().isoformat(),
                'message': line.strip(),
                'module': module_name
            }
        
        except Exception as e:
            logger.error(f"Error parsing log line: {str(e)}")
            return None
    
    def _filter_logs_by_date(self, logs: List[Dict[str, Any]], 
                            start_dt: datetime.datetime, 
                            end_dt: datetime.datetime) -> List[Dict[str, Any]]:
        """Filter logs by date range."""
        filtered_logs = []
        
        for log in logs:
            # Skip logs without timestamp
            if 'timestamp' not in log:
                continue
            
            # Parse timestamp
            try:
                # Handle different timestamp formats
                timestamp = log['timestamp']
                if 'T' in timestamp:
                    # ISO format
                    log_dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                elif ',' in timestamp:
                    # Standard logging format
                    log_dt = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f')
                else:
                    # Simple date format
                    log_dt = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                
                # Convert to date for comparison
                log_date = log_dt.date()
                
                # Check if log is within date range
                if start_dt.date() <= log_date <= end_dt.date():
                    filtered_logs.append(log)
            
            except Exception as e:
                logger.error(f"Error parsing timestamp {log.get('timestamp')}: {str(e)}")
        
        return filtered_logs

class ReportGenerator:
    """Class for generating reports from collected logs and data."""
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the report generator.
        
        Args:
            output_dir: Directory to save generated reports
        """
        if output_dir is None:
            self.output_dir = os.path.join('data', 'report', 'generated_reports')
        else:
            self.output_dir = output_dir
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info(f"Initialized ReportGenerator with output directory: {self.output_dir}")
    
    def create_report(self, data: Dict[str, Any], 
                     report_format: ReportFormat = ReportFormat.HTML,
                     title: str = "Trading System Report") -> str:
        """
        Create a report from the provided data.
        
        Args:
            data: Data to include in the report
            report_format: Format of the report
            title: Title of the report
        
        Returns:
            Path to the generated report file
        """
        # Generate timestamp for filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create filename based on format
        filename = f"{title.replace(' ', '_')}_{timestamp}.{report_format.value}"
        file_path = os.path.join(self.output_dir, filename)
        
        logger.info(f"Creating {report_format.value} report: {file_path}")
        
        try:
            # Generate report based on format
            if report_format == ReportFormat.HTML:
                self._create_html_report(data, file_path, title)
            elif report_format == ReportFormat.PDF:
                self._create_pdf_report(data, file_path, title)
            elif report_format == ReportFormat.JSON:
                self._create_json_report(data, file_path)
            elif report_format == ReportFormat.CSV:
                self._create_csv_report(data, file_path)
            else:
                raise ValueError(f"Unsupported report format: {report_format}")
            
            logger.info(f"Report generated successfully: {file_path}")
            return file_path
        
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise
    
    def _create_html_report(self, data: Dict[str, Any], file_path: str, title: str) -> None:
        """Create an HTML report."""
        # Simple HTML template
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333366; }}
                h2 {{ color: #666699; margin-top: 30px; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .error {{ color: red; }}
                .warning {{ color: orange; }}
                .info {{ color: blue; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <p>Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        
        # Add sections based on data
        for section, section_data in data.items():
            html += f"<h2>{section}</h2>"
            
            if isinstance(section_data, list):
                # Table for list data
                if section_data and isinstance(section_data[0], dict):
                    # Get all unique keys
                    keys = set()
                    for item in section_data:
                        keys.update(item.keys())
                    
                    # Create table
                    html += "<table>"
                    html += "<tr>" + "".join([f"<th>{key}</th>" for key in keys]) + "</tr>"
                    
                    for item in section_data:
                        html += "<tr>"
                        for key in keys:
                            value = item.get(key, "")
                            
                            # Apply styling based on log level
                            css_class = ""
                            if key == "level" or key == "status":
                                if value.lower() in ["error", "critical", "rejected"]:
                                    css_class = "error"
                                elif value.lower() in ["warning", "partially_filled"]:
                                    css_class = "warning"
                                elif value.lower() in ["info", "filled"]:
                                    css_class = "info"
                            
                            html += f"<td class='{css_class}'>{value}</td>"
                        html += "</tr>"
                    
                    html += "</table>"
                else:
                    # Simple list
                    html += "<ul>"
                    for item in section_data:
                        html += f"<li>{item}</li>"
                    html += "</ul>"
            
            elif isinstance(section_data, dict):
                # Table for dictionary data
                html += "<table>"
                for key, value in section_data.items():
                    html += f"<tr><th>{key}</th><td>{value}</td></tr>"
                html += "</table>"
            
            else:
                # Simple text
                html += f"<p>{section_data}</p>"
        
        html += """
        </body>
        </html>
        """
        
        # Write HTML to file
        with open(file_path, 'w') as f:
            f.write(html)
    
    def _create_pdf_report(self, data: Dict[str, Any], file_path: str, title: str) -> None:
        """Create a PDF report."""
        # For a real implementation, you would use a library like reportlab or weasyprint
        # Here we'll create an HTML file and note that it should be converted to PDF
        
        # Create HTML version first
        html_path = file_path.replace('.pdf', '.html')
        self._create_html_report(data, html_path, title)
        
        # Mock PDF conversion
        logger.info(f"PDF generation would convert {html_path} to {file_path}")
        logger.info("Note: Actual PDF conversion requires additional libraries like reportlab or weasyprint")
        
        # In a real implementation, you would use code like:
        # from weasyprint import HTML
        # HTML(html_path).write_pdf(file_path)
        
        # For now, just create a placeholder PDF file
        with open(file_path, 'w') as f:
            f.write(f"PDF Report: {title}\nGenerated on: {datetime.datetime.now()}\n")
            f.write("This is a placeholder for a PDF report.\n")
            f.write(f"See HTML version at: {html_path}\n")
    
    def _create_json_report(self, data: Dict[str, Any], file_path: str) -> None:
        """Create a JSON report."""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _create_csv_report(self, data: Dict[str, Any], file_path: str) -> None:
        """Create a CSV report."""
        # For each section in data, create a separate CSV file
        base_path = file_path.replace('.csv', '')
        
        for section, section_data in data.items():
            section_path = f"{base_path}_{section}.csv"
            
            if isinstance(section_data, list) and section_data and isinstance(section_data[0], dict):
                # Convert list of dicts to DataFrame
                df = pd.DataFrame(section_data)
                df.to_csv(section_path, index=False)
            
            elif isinstance(section_data, dict):
                # Convert dict to DataFrame
                df = pd.DataFrame([section_data])
                df.to_csv(section_path, index=False)
            
            else:
                # Simple data, just write to file
                with open(section_path, 'w') as f:
                    f.write(f"{section}\n{section_data}\n")
        
        # Create a manifest file
        with open(file_path, 'w') as f:
            f.write("Report Sections:\n")
            for section in data.keys():
                f.write(f"{section}: {base_path}_{section}.csv\n")

class AlertManager:
    """Class for sending alerts and notifications."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the alert manager.
        
        Args:
            config: Configuration for alert channels
        """
        self.config = config or {}
        logger.info("Initialized AlertManager")
    
    def send_alert(self, message: str, level: AlertLevel = AlertLevel.INFO,
                  channels: List[AlertChannel] = None) -> Dict[str, bool]:
        """
        Send an alert through specified channels.
        
        Args:
            message: Alert message
            level: Alert level
            channels: List of channels to send the alert through
        
        Returns:
            Dictionary mapping channel names to success status
        """
        if channels is None:
            # Default to console
            channels = [AlertChannel.CONSOLE]
        
        logger.info(f"Sending {level.value} alert through {[c.value for c in channels]}: {message}")
        
        results = {}
        
        for channel in channels:
            try:
                if channel == AlertChannel.EMAIL:
                    success = self._send_email_alert(message, level)
                elif channel == AlertChannel.SLACK:
                    success = self._send_slack_alert(message, level)
                elif channel == AlertChannel.SMS:
                    success = self._send_sms_alert(message, level)
                elif channel == AlertChannel.CONSOLE:
                    success = self._send_console_alert(message, level)
                else:
                    logger.warning(f"Unsupported alert channel: {channel}")
                    success = False
                
                results[channel.value] = success
            
            except Exception as e:
                logger.error(f"Error sending alert through {channel.value}: {str(e)}")
                results[channel.value] = False
        
        return results
    
    def _send_email_alert(self, message: str, level: AlertLevel) -> bool:
        """Send an alert via email."""
        # Check if email configuration is available
        if 'email' not in self.config:
            logger.warning("Email configuration not available")
            return False
        
        email_config = self.config['email']
        required_fields = ['smtp_server', 'smtp_port', 'sender', 'recipients']
        
        for field in required_fields:
            if field not in email_config:
                logger.warning(f"Missing required email configuration field: {field}")
                return False
        
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = email_config['sender']
            msg['To'] = ', '.join(email_config['recipients'])
            msg['Subject'] = f"[{level.value.upper()}] Trading System Alert"
            
            # Add message body
            msg.attach(MIMEText(message, 'plain'))
            
            # Connect to SMTP server
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                # Use TLS if configured
                if email_config.get('use_tls', False):
                    server.starttls()
                
                # Login if credentials are provided
                if 'username' in email_config and 'password' in email_config:
                    server.login(email_config['username'], email_config['password'])
                
                # Send email
                server.send_message(msg)
            
            logger.info(f"Email alert sent to {email_config['recipients']}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending email alert: {str(e)}")
            return False
    
    def _send_slack_alert(self, message: str, level: AlertLevel) -> bool:
        """Send an alert via Slack."""
        # Check if Slack configuration is available
        if 'slack' not in self.config:
            logger.warning("Slack configuration not available")
            return False
        
        slack_config = self.config['slack']
        if 'webhook_url' not in slack_config:
            logger.warning("Missing Slack webhook URL")
            return False
        
        try:
            # Prepare payload
            payload = {
                "text": f"*[{level.value.upper()}]* {message}",
                "mrkdwn": True
            }
            
            # Add color based on level
            if level == AlertLevel.ERROR or level == AlertLevel.CRITICAL:
                payload["color"] = "danger"
            elif level == AlertLevel.WARNING:
                payload["color"] = "warning"
            else:
                payload["color"] = "good"
            
            # Send to Slack webhook
            response = requests.post(
                slack_config['webhook_url'],
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info("Slack alert sent successfully")
                return True
            else:
                logger.warning(f"Slack API returned status code {response.status_code}: {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Error sending Slack alert: {str(e)}")
            return False
    
    def _send_sms_alert(self, message: str, level: AlertLevel) -> bool:
        """Send an alert via SMS."""
        # This is a mock implementation
        logger.info(f"Would send SMS alert: [{level.value.upper()}] {message}")
        logger.info("Note: Actual SMS implementation requires a service like Twilio")
        
        # In a real implementation, you would use code like:
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # client.messages.create(body=message, from_=from_number, to=to_number)
        
        return True
    
    def _send_console_alert(self, message: str, level: AlertLevel) -> bool:
        """Send an alert to the console."""
        # Format based on level
        if level == AlertLevel.ERROR or level == AlertLevel.CRITICAL:
            print(f"\033[91m[{level.value.upper()}] {message}\033[0m")  # Red
        elif level == AlertLevel.WARNING:
            print(f"\033[93m[{level.value.upper()}] {message}\033[0m")  # Yellow
        else:
            print(f"\033[94m[{level.value.upper()}] {message}\033[0m")  # Blue
        
        return True

class AnomalyDetector:
    """Class for detecting anomalies in system data and logs."""
    
    def __init__(self, thresholds: Dict[str, Any] = None):
        """
        Initialize the anomaly detector.
        
        Args:
            thresholds: Dictionary of thresholds for different anomaly types
        """
        self.thresholds = thresholds or {
            'error_count': 5,  # Number of errors to trigger an anomaly
            'api_latency': 2.0,  # API latency threshold in seconds
            'data_gap': 60,  # Maximum allowed gap in data in minutes
            'price_change': 0.05  # Maximum allowed price change (5%)
        }
        
        logger.info(f"Initialized AnomalyDetector with thresholds: {self.thresholds}")
    
    def detect_anomalies(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect anomalies in the provided data.
        
        Args:
            data: Data to analyze for anomalies
        
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Check for log-based anomalies
        if 'logs' in data:
            log_anomalies = self._detect_log_anomalies(data['logs'])
            anomalies.extend(log_anomalies)
        
        # Check for data-based anomalies
        if 'market_data' in data:
            data_anomalies = self._detect_data_anomalies(data['market_data'])
            anomalies.extend(data_anomalies)
        
        # Check for API-based anomalies
        if 'api_metrics' in data:
            api_anomalies = self._detect_api_anomalies(data['api_metrics'])
            anomalies.extend(api_anomalies)
        
        # Check for system-based anomalies
        if 'system_metrics' in data:
            system_anomalies = self._detect_system_anomalies(data['system_metrics'])
            anomalies.extend(system_anomalies)
        
        logger.info(f"Detected {len(anomalies)} anomalies")
        return anomalies
    
    def _detect_log_anomalies(self, logs: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Detect anomalies in log data."""
        anomalies = []
        
        # Count errors by module
        error_counts = {}
        for module, module_logs in logs.items():
            error_count = 0
            for log in module_logs:
                level = log.get('level', '').lower()
                if level in ['error', 'critical']:
                    error_count += 1
            
            error_counts[module] = error_count
            
            # Check if error count exceeds threshold
            if error_count >= self.thresholds['error_count']:
                anomalies.append({
                    'type': 'log_error_count',
                    'module': module,
                    'count': error_count,
                    'threshold': self.thresholds['error_count'],
                    'timestamp': datetime.datetime.now().isoformat(),
                    'description': f"High error count in {module}: {error_count} errors"
                })
        
        return anomalies
    
    def _detect_data_anomalies(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies in market data."""
        anomalies = []
        
        # Check for missing data
        if 'timestamps' in market_data:
            timestamps = market_data['timestamps']
            if len(timestamps) >= 2:
                # Check for gaps in timestamps
                for i in range(1, len(timestamps)):
                    t1 = datetime.datetime.fromisoformat(timestamps[i-1].replace('Z', '+00:00'))
                    t2 = datetime.datetime.fromisoformat(timestamps[i].replace('Z', '+00:00'))
                    gap_minutes = (t2 - t1).total_seconds() / 60
                    
                    if gap_minutes > self.thresholds['data_gap']:
                        anomalies.append({
                            'type': 'data_gap',
                            'start_time': t1.isoformat(),
                            'end_time': t2.isoformat(),
                            'gap_minutes': gap_minutes,
                            'threshold': self.thresholds['data_gap'],
                            'timestamp': datetime.datetime.now().isoformat(),
                            'description': f"Data gap of {gap_minutes:.1f} minutes detected"
                        })
        
        # Check for unusual price changes
        if 'prices' in market_data and 'symbols' in market_data:
            prices = market_data['prices']
            symbols = market_data['symbols']
            
            for i, symbol in enumerate(symbols):
                if i < len(prices) and len(prices[i]) >= 2:
                    symbol_prices = prices[i]
                    
                    # Calculate percentage changes
                    for j in range(1, len(symbol_prices)):
                        if symbol_prices[j-1] > 0:
                            pct_change = abs(symbol_prices[j] - symbol_prices[j-1]) / symbol_prices[j-1]
                            
                            if pct_change > self.thresholds['price_change']:
                                anomalies.append({
                                    'type': 'price_change',
                                    'symbol': symbol,
                                    'from_price': symbol_prices[j-1],
                                    'to_price': symbol_prices[j],
                                    'pct_change': pct_change,
                                    'threshold': self.thresholds['price_change'],
                                    'timestamp': datetime.datetime.now().isoformat(),
                                    'description': f"Unusual price change for {symbol}: {pct_change:.1%}"
                                })
        
        return anomalies
    
    def _detect_api_anomalies(self, api_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies in API metrics."""
        anomalies = []
        
        # Check for high API latency
        if 'latencies' in api_metrics and 'endpoints' in api_metrics:
            latencies = api_metrics['latencies']
            endpoints = api_metrics['endpoints']
            
            for i, endpoint in enumerate(endpoints):
                if i < len(latencies):
                    latency = latencies[i]
                    
                    if latency > self.thresholds['api_latency']:
                        anomalies.append({
                            'type': 'api_latency',
                            'endpoint': endpoint,
                            'latency': latency,
                            'threshold': self.thresholds['api_latency'],
                            'timestamp': datetime.datetime.now().isoformat(),
                            'description': f"High API latency for {endpoint}: {latency:.2f}s"
                        })
        
        # Check for API errors
        if 'error_rates' in api_metrics and 'endpoints' in api_metrics:
            error_rates = api_metrics['error_rates']
            endpoints = api_metrics['endpoints']
            
            for i, endpoint in enumerate(endpoints):
                if i < len(error_rates):
                    error_rate = error_rates[i]
                    
                    if error_rate > 0.1:  # 10% error rate threshold
                        anomalies.append({
                            'type': 'api_error_rate',
                            'endpoint': endpoint,
                            'error_rate': error_rate,
                            'threshold': 0.1,
                            'timestamp': datetime.datetime.now().isoformat(),
                            'description': f"High API error rate for {endpoint}: {error_rate:.1%}"
                        })
        
        return anomalies
    
    def _detect_system_anomalies(self, system_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies in system metrics."""
        anomalies = []
        
        # Check for high CPU usage
        if 'cpu_usage' in system_metrics:
            cpu_usage = system_metrics['cpu_usage']
            
            if cpu_usage > 90:  # 90% CPU usage threshold
                anomalies.append({
                    'type': 'high_cpu_usage',
                    'usage': cpu_usage,
                    'threshold': 90,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'description': f"High CPU usage: {cpu_usage:.1f}%"
                })
        
        # Check for high memory usage
        if 'memory_usage' in system_metrics:
            memory_usage = system_metrics['memory_usage']
            
            if memory_usage > 90:  # 90% memory usage threshold
                anomalies.append({
                    'type': 'high_memory_usage',
                    'usage': memory_usage,
                    'threshold': 90,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'description': f"High memory usage: {memory_usage:.1f}%"
                })
        
        # Check for disk space
        if 'disk_usage' in system_metrics:
            disk_usage = system_metrics['disk_usage']
            
            if disk_usage > 90:  # 90% disk usage threshold
                anomalies.append({
                    'type': 'high_disk_usage',
                    'usage': disk_usage,
                    'threshold': 90,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'description': f"High disk usage: {disk_usage:.1f}%"
                })
        
        return anomalies

def collect_logs(start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Collect logs from all modules.
    
    Args:
        start_date: Start date for log collection (YYYY-MM-DD)
        end_date: End date for log collection (YYYY-MM-DD)
    
    Returns:
        Dictionary mapping module names to lists of log entries
    """
    collector = LogCollector()
    return collector.collect_logs(start_date, end_date)

def create_report(data: Dict[str, Any], 
                 report_format: Union[ReportFormat, str] = ReportFormat.HTML,
                 title: str = "Trading System Report") -> str:
    """
    Create a report from the provided data.
    
    Args:
        data: Data to include in the report
        report_format: Format of the report
        title: Title of the report
    
    Returns:
        Path to the generated report file
    """
    # Convert string format to enum if needed
    if isinstance(report_format, str):
        report_format = ReportFormat(report_format)
    
    generator = ReportGenerator()
    return generator.create_report(data, report_format, title)

def send_alert(message: str, 
              level: Union[AlertLevel, str] = AlertLevel.INFO,
              channels: List[Union[AlertChannel, str]] = None,
              config: Dict[str, Any] = None) -> Dict[str, bool]:
    """
    Send an alert through specified channels.
    
    Args:
        message: Alert message
        level: Alert level
        channels: List of channels to send the alert through
        config: Configuration for alert channels
    
    Returns:
        Dictionary mapping channel names to success status
    """
    # Convert string level to enum if needed
    if isinstance(level, str):
        level = AlertLevel(level)
    
    # Convert string channels to enums if needed
    if channels is not None:
        channels = [
            AlertChannel(c) if isinstance(c, str) else c
            for c in channels
        ]
    
    manager = AlertManager(config)
    return manager.send_alert(message, level, channels)

def detect_anomalies(data: Dict[str, Any], thresholds: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Detect anomalies in the provided data.
    
    Args:
        data: Data to analyze for anomalies
        thresholds: Dictionary of thresholds for different anomaly types
    
    Returns:
        List of detected anomalies
    """
    detector = AnomalyDetector(thresholds)
    return detector.detect_anomalies(data)

# Example usage
if __name__ == "__main__":
    # Collect logs
    logs = collect_logs()
    
    # Sample market data
    market_data = {
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
    
    # Sample API metrics
    api_metrics = {
        'endpoints': ['/market/data', '/orders', '/account'],
        'latencies': [0.2, 0.5, 0.3],
        'error_rates': [0.0, 0.05, 0.0]
    }
    
    # Sample system metrics
    system_metrics = {
        'cpu_usage': 45.0,
        'memory_usage': 60.0,
        'disk_usage': 75.0
    }
    
    # Combine data
    data = {
        'logs': logs,
        'market_data': market_data,
        'api_metrics': api_metrics,
        'system_metrics': system_metrics
    }
    
    # Detect anomalies
    anomalies = detect_anomalies(data)
    
    # Add anomalies to data
    data['anomalies'] = anomalies
    
    # Create report
    report_path = create_report(data, ReportFormat.HTML, "Daily Trading System Report")
    print(f"Report generated: {report_path}")
    
    # Send alert if anomalies were detected
    if anomalies:
        alert_message = f"Detected {len(anomalies)} anomalies. See report: {report_path}"
        send_alert(alert_message, AlertLevel.WARNING, [AlertChannel.CONSOLE])