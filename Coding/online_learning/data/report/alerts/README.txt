# Alerts Directory

This directory contains records of alerts and notifications sent by the system, including trading signals, system warnings, and error notifications.

## Contents

- Trading signal alerts
- System warning alerts
- Error notifications
- Performance threshold alerts
- Risk limit alerts
- Compliance alerts

## File Naming Convention

Files are named according to the following patterns:

1. Daily alert logs:
   - alerts_{DATE}.json
   - Example: alerts_20230315.json

2. Alert type specific logs:
   - alerts_{TYPE}_{DATE}.json
   - Example: alerts_trading_20230315.json, alerts_system_20230315.json

3. Notification delivery logs:
   - notifications_{CHANNEL}_{DATE}.json
   - Example: notifications_email_20230315.json, notifications_slack_20230315.json

## Data Formats

### Alert Log JSON Format

```json
[
  {
    "alert_id": "alert_20230315_001",
    "timestamp": "2023-03-15T09:45:00.123Z",
    "type": "trading_signal",
    "level": "info",
    "source": "momentum_strategy",
    "message": "Buy signal generated for AAPL",
    "details": {
      "symbol": "AAPL",
      "signal": "buy",
      "confidence": 0.85,
      "price": 150.25,
      "strategy_id": "momentum_v1.2"
    },
    "notification_channels": ["email", "slack"],
    "notification_status": "sent"
  },
  {
    "alert_id": "alert_20230315_002",
    "timestamp": "2023-03-15T10:15:30.456Z",
    "type": "system_warning",
    "level": "warning",
    "source": "data_pipeline",
    "message": "Delayed market data for NASDAQ symbols",
    "details": {
      "affected_symbols": ["AAPL", "MSFT", "GOOGL"],
      "delay_seconds": 120,
      "provider": "market_data_provider_a"
    },
    "notification_channels": ["slack", "sms"],
    "notification_status": "sent"
  },
  {
    "alert_id": "alert_20230315_003",
    "timestamp": "2023-03-15T14:22:15.789Z",
    "type": "risk_limit",
    "level": "critical",
    "source": "risk_manager",
    "message": "Portfolio drawdown exceeding threshold",
    "details": {
      "current_drawdown": 0.052,
      "threshold": 0.05,
      "affected_strategies": ["momentum_v1.2", "mean_reversion_v2.0"]
    },
    "notification_channels": ["email", "slack", "sms"],
    "notification_status": "sent"
  }
]
```

### Notification Delivery Log JSON Format

```json
[
  {
    "notification_id": "notif_20230315_001",
    "alert_id": "alert_20230315_001",
    "timestamp": "2023-03-15T09:45:01.234Z",
    "channel": "email",
    "recipients": ["trader@example.com", "risk@example.com"],
    "subject": "Trading Signal Alert: Buy AAPL",
    "status": "delivered",
    "delivery_timestamp": "2023-03-15T09:45:02.345Z"
  },
  {
    "notification_id": "notif_20230315_002",
    "alert_id": "alert_20230315_001",
    "timestamp": "2023-03-15T09:45:01.456Z",
    "channel": "slack",
    "recipients": ["#trading-alerts"],
    "status": "delivered",
    "delivery_timestamp": "2023-03-15T09:45:01.789Z"
  }
]
```

## Alert Levels

Alerts use the following severity levels:

- INFO: Informational alerts, such as regular trading signals
- WARNING: Alerts that require attention but are not critical
- ERROR: Alerts indicating problems that need to be addressed
- CRITICAL: Urgent alerts requiring immediate attention

## Notification Channels

The system can send alerts through multiple channels:

- Email: For detailed alerts that can be reviewed later
- Slack: For team communication and collaboration
- SMS: For urgent alerts requiring immediate attention
- Console: For local monitoring and debugging
- Dashboard: For visual monitoring of system status

## Notes

- Alert logs are useful for auditing and troubleshooting
- Consider implementing alert aggregation to prevent alert fatigue
- Critical alerts should be sent through multiple channels
- Alerts should include sufficient context for action
- Consider implementing alert acknowledgment tracking
- Notification delivery should be monitored for failures