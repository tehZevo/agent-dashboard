#!/usr/bin/env python3
"""
Create comprehensive test data for the Agent Dashboard
Tests all features including teams, statuses, history, and webhooks
"""
import json
from pathlib import Path
from datetime import datetime, timedelta

DATA_FILE = Path(__file__).parent / "agent_data.json"

def create_comprehensive_test_data():
    """Create comprehensive test agent data"""

    now = datetime.now()

    # Create agents with various teams and statuses
    test_data = {
        "agents": {
            # Production Team - Working
            "prod-web-001": {
                "status_message": "Processing customer requests",
                "task_status": "working",
                "last_checkin": now.isoformat(),
                "team": "Production Team"
            },
            "prod-api-002": {
                "status_message": "Handling API traffic",
                "task_status": "working",
                "last_checkin": (now - timedelta(seconds=10)).isoformat(),
                "team": "Production Team"
            },

            # Production Team - Idle
            "prod-worker-003": {
                "status_message": "Waiting for tasks",
                "task_status": "idle",
                "last_checkin": (now - timedelta(seconds=30)).isoformat(),
                "team": "Production Team"
            },

            # Development Team - Warning
            "dev-test-001": {
                "status_message": "Test suite running slowly",
                "task_status": "warning",
                "last_checkin": (now - timedelta(minutes=1)).isoformat(),
                "team": "Development Team"
            },

            # Development Team - Working
            "dev-build-002": {
                "status_message": "Compiling project",
                "task_status": "working",
                "last_checkin": (now - timedelta(seconds=45)).isoformat(),
                "team": "Development Team"
            },

            # Analytics Team - Error
            "analytics-etl-001": {
                "status_message": "Database connection timeout",
                "task_status": "error",
                "last_checkin": (now - timedelta(minutes=2)).isoformat(),
                "team": "Analytics Team"
            },

            # Analytics Team - Working
            "analytics-ml-002": {
                "status_message": "Training ML model",
                "task_status": "working",
                "last_checkin": (now - timedelta(seconds=5)).isoformat(),
                "team": "Analytics Team"
            },

            # Analytics Team - Stale (over 5 minutes)
            "analytics-data-003": {
                "status_message": "Last seen over 5 minutes ago",
                "task_status": "working",
                "last_checkin": (now - timedelta(minutes=10)).isoformat(),
                "team": "Analytics Team"
            },

            # Monitoring Team - Idle
            "monitor-health-001": {
                "status_message": "No alerts",
                "task_status": "idle",
                "last_checkin": (now - timedelta(seconds=15)).isoformat(),
                "team": "Monitoring Team"
            },

            # Monitoring Team - Working
            "monitor-metrics-002": {
                "status_message": "Collecting metrics",
                "task_status": "working",
                "last_checkin": (now - timedelta(seconds=20)).isoformat(),
                "team": "Monitoring Team"
            },

            # Unassigned agents
            "standalone-001": {
                "status_message": "Independent task processor",
                "task_status": "idle",
                "last_checkin": (now - timedelta(minutes=1)).isoformat()
            },

            "legacy-system-002": {
                "status_message": "Legacy integration running",
                "task_status": "warning",
                "last_checkin": (now - timedelta(minutes=3)).isoformat()
            },

            "backup-agent-003": {
                "status_message": "Running backup job",
                "task_status": "working",
                "last_checkin": (now - timedelta(seconds=25)).isoformat()
            }
        },

        # Create history for agents
        "history": {
            # Individual agent history
            "prod-web-001": [
                {
                    "timestamp": (now - timedelta(minutes=30)).isoformat(),
                    "status": "idle",
                    "message": "Started up"
                },
                {
                    "timestamp": (now - timedelta(minutes=25)).isoformat(),
                    "status": "working",
                    "message": "Processing requests"
                },
                {
                    "timestamp": (now - timedelta(minutes=20)).isoformat(),
                    "status": "working",
                    "message": "High load"
                },
                {
                    "timestamp": (now - timedelta(minutes=15)).isoformat(),
                    "status": "warning",
                    "message": "Memory usage high"
                },
                {
                    "timestamp": (now - timedelta(minutes=10)).isoformat(),
                    "status": "working",
                    "message": "Optimized, back to normal"
                }
            ],
            "dev-test-001": [
                {
                    "timestamp": (now - timedelta(minutes=20)).isoformat(),
                    "status": "idle",
                    "message": "Waiting"
                },
                {
                    "timestamp": (now - timedelta(minutes=15)).isoformat(),
                    "status": "working",
                    "message": "Running tests"
                },
                {
                    "timestamp": (now - timedelta(minutes=10)).isoformat(),
                    "status": "working",
                    "message": "Still testing"
                },
                {
                    "timestamp": (now - timedelta(minutes=5)).isoformat(),
                    "status": "warning",
                    "message": "Tests taking longer than expected"
                }
            ],
            "analytics-etl-001": [
                {
                    "timestamp": (now - timedelta(minutes=25)).isoformat(),
                    "status": "working",
                    "message": "ETL job started"
                },
                {
                    "timestamp": (now - timedelta(minutes=20)).isoformat(),
                    "status": "working",
                    "message": "Processing data"
                },
                {
                    "timestamp": (now - timedelta(minutes=15)).isoformat(),
                    "status": "warning",
                    "message": "Slow query detected"
                },
                {
                    "timestamp": (now - timedelta(minutes=10)).isoformat(),
                    "status": "warning",
                    "message": "Connection unstable"
                },
                {
                    "timestamp": (now - timedelta(minutes=5)).isoformat(),
                    "status": "error",
                    "message": "Database connection lost"
                }
            ],

            # Team history
            "team:Production Team": [
                {
                    "timestamp": (now - timedelta(minutes=30)).isoformat(),
                    "status": "idle",
                    "message": "Team starting up"
                },
                {
                    "timestamp": (now - timedelta(minutes=25)).isoformat(),
                    "status": "working",
                    "message": "Team active"
                },
                {
                    "timestamp": (now - timedelta(minutes=20)).isoformat(),
                    "status": "working",
                    "message": "Handling traffic"
                },
                {
                    "timestamp": (now - timedelta(minutes=15)).isoformat(),
                    "status": "warning",
                    "message": "High load detected"
                },
                {
                    "timestamp": (now - timedelta(minutes=10)).isoformat(),
                    "status": "working",
                    "message": "Load normalized"
                }
            ],
            "team:Development Team": [
                {
                    "timestamp": (now - timedelta(minutes=20)).isoformat(),
                    "status": "idle",
                    "message": "Ready for builds"
                },
                {
                    "timestamp": (now - timedelta(minutes=15)).isoformat(),
                    "status": "working",
                    "message": "Build started"
                },
                {
                    "timestamp": (now - timedelta(minutes=10)).isoformat(),
                    "status": "working",
                    "message": "Running tests"
                },
                {
                    "timestamp": (now - timedelta(minutes=5)).isoformat(),
                    "status": "warning",
                    "message": "Tests running slow"
                }
            ],
            "team:Analytics Team": [
                {
                    "timestamp": (now - timedelta(minutes=25)).isoformat(),
                    "status": "working",
                    "message": "Processing analytics"
                },
                {
                    "timestamp": (now - timedelta(minutes=20)).isoformat(),
                    "status": "working",
                    "message": "Training models"
                },
                {
                    "timestamp": (now - timedelta(minutes=15)).isoformat(),
                    "status": "warning",
                    "message": "Data pipeline slow"
                },
                {
                    "timestamp": (now - timedelta(minutes=10)).isoformat(),
                    "status": "warning",
                    "message": "Connection issues"
                },
                {
                    "timestamp": (now - timedelta(minutes=5)).isoformat(),
                    "status": "error",
                    "message": "Agent offline"
                }
            ]
        },

        # Create some test webhooks
        "webhooks": [
            {
                "url": "https://example.com/webhook1",
                "events": ["status_update"],
                "created_at": (now - timedelta(days=1)).isoformat()
            },
            {
                "url": "https://example.com/webhook2",
                "events": ["agent_online", "agent_offline"],
                "created_at": (now - timedelta(hours=2)).isoformat()
            },
            {
                "url": "https://example.com/webhook3",
                "events": ["all"],
                "created_at": (now - timedelta(minutes=30)).isoformat()
            }
        ]
    }

    with open(DATA_FILE, 'w') as f:
        json.dump(test_data, f, indent=2)

    print(f"✓ Comprehensive test data created in {DATA_FILE}")
    print(f"\n=== Summary ===")
    print(f"Total agents: {len(test_data['agents'])}")

    # Count by team
    teams = {}
    unassigned = 0
    for agent_id, agent_data in test_data['agents'].items():
        team = agent_data.get('team')
        if team:
            teams[team] = teams.get(team, 0) + 1
        else:
            unassigned += 1

    print(f"\nTeams:")
    for team, count in teams.items():
        print(f"  - {team}: {count} agents")
    print(f"  - Unassigned: {unassigned} agents")

    # Count by status
    statuses = {}
    for agent_id, agent_data in test_data['agents'].items():
        status = agent_data.get('task_status')
        statuses[status] = statuses.get(status, 0) + 1

    print(f"\nStatuses:")
    for status, count in statuses.items():
        print(f"  - {status}: {count} agents")

    print(f"\nHistory entries:")
    total_history = sum(len(entries) if isinstance(entries, list) else 0
                       for entries in test_data['history'].values())
    print(f"  - Total: {total_history} entries")

    print(f"\nWebhooks: {len(test_data['webhooks'])}")

    print(f"\n✓ Dashboard is running at http://localhost:5000")
    print(f"✓ You can now test all features!")

if __name__ == "__main__":
    print("Creating comprehensive test data for Agent Dashboard...\n")
    create_comprehensive_test_data()
