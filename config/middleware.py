import time
from collections import defaultdict

# Simple in-memory storage for rate limiting
rate_limit_data = defaultdict(list)


class SimpleRateLimiter:
    def __init__(self, max_requests, time_window):
        self.max_requests = max_requests
        self.time_window = time_window

    def check_rate_limit(self, request):
        # Get client IP (you might want to use other identifiers like user ID for authenticated users)
        client_ip = self._get_client_ip(request)

        # Get current timestamp
        current_time = time.time()

        # Clean up old records
        self._clean_old_records(client_ip, current_time)

        # Check if under limit
        if len(rate_limit_data[client_ip]) < self.max_requests:
            rate_limit_data[client_ip].append(current_time)
            return True
        return False

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _clean_old_records(self, client_ip, current_time):
        # Remove timestamps older than our time window
        rate_limit_data[client_ip] = [
            t for t in rate_limit_data[client_ip]
            if current_time - t < self.time_window
        ]
