import time
import json
import os

class AuditLog:
    def __init__(self):
        self.logs = []
        self.log_file = 'audit_logs.json'
        self.load_logs()

    def load_logs(self):
        """Load logs from JSON file if it exists."""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    self.logs = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.logs = []

    def save_logs(self):
        """Save logs to JSON file."""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.logs, f, indent=4)
        except IOError as e:
            print(f"Error saving logs: {e}")

    def log_action(self, user, action, details):
        """Log an action and save to file."""
        log_entry = {
            'timestamp': time.time(),
            'user': user,
            'action': action,
            'details': details
        }
        self.logs.append(log_entry)
        self.save_logs()

    def get_logs(self):
        """Return all logs."""
        return self.logs