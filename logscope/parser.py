import re
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class LogEntry:
    level: str
    message: str
    raw: str
    timestamp: Optional[datetime] = None

def parse_line(line: str) -> LogEntry:
    """Parse a single line of log and extract severity level."""
    line = line.strip()
    
    # 1. Check if JSON log object (common in docker/kubernetes/modern APIs)
    if line.startswith('{') and line.endswith('}'):
        try:
            data = json.loads(line)
            # Find level key
            level = str(data.get('level', data.get('severity', data.get('log.level', 'UNKNOWN')))).upper()
            # Find message key
            message = str(data.get('message', data.get('msg', data.get('text', line))))
            
            # Find timestamp
            timestamp_str = data.get('timestamp', data.get('time', data.get('@timestamp')))
            timestamp = None
            if timestamp_str:
                try:
                    # Basic ISO parsing
                    timestamp = datetime.fromisoformat(str(timestamp_str).replace('Z', '+00:00'))
                except ValueError:
                    pass

            if level == "WARNING": level = "WARN"
            if level == "EMERGENCY": level = "FATAL"
            if level == "ERR": level = "ERROR"
            return LogEntry(level=level, message=message, raw=line, timestamp=timestamp)
        except json.JSONDecodeError:
            pass

    # 2. Try typical log formats like [INFO], (WARN), ERROR:
    match = re.search(r'\[(TRACE|DEBUG|INFO|NOTICE|WARN|WARNING|ERROR|ERR|CRITICAL|ALERT|FATAL|EMERGENCY)\]', line, re.IGNORECASE)
    if not match:
        # Try finding without brackets as a fallback, e.g. "INFO:" or "INFO - "
        match = re.search(r'\b(TRACE|DEBUG|INFO|NOTICE|WARN|WARNING|ERROR|ERR|CRITICAL|ALERT|FATAL|EMERGENCY)\b', line, re.IGNORECASE)

    if match:
        level = match.group(1).upper()
        
        # Normalize levels
        if level == "WARNING":
            level = "WARN"
        if level == "EMERGENCY":
            level = "FATAL"
        if level == "ERR":
            level = "ERROR"
            
        # Remove the [LEVEL] part from the message for cleaner display
        message = line.replace(match.group(0), '', 1).strip()
        
        # Clean up common separators left behind like ": " or "- "
        if message.startswith(':') or message.startswith('-'):
            message = message[1:].strip()
            
        return LogEntry(level=level, message=message, raw=line, timestamp=extract_timestamp(line))
    
    # fallback
    return LogEntry(level="UNKNOWN", message=line, raw=line, timestamp=extract_timestamp(line))

def extract_timestamp(text: str) -> Optional[datetime]:
    """Helper to extract a timestamp from a raw string using regex."""
    pattern = r"(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)"
    match = re.search(pattern, text)
    if match:
        try:
            return datetime.fromisoformat(match.group(1).replace('Z', '+00:00'))
        except ValueError:
            return None
    return None
