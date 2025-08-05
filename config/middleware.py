import time
from collections import defaultdict
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

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

    def get_remaining_requests(self, request):
        """Get number of remaining requests for this client"""
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        self._clean_old_records(client_ip, current_time)
        return max(0, self.max_requests - len(rate_limit_data[client_ip]))

    def get_reset_time(self, request):
        """Get when the rate limit resets for this client"""
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        self._clean_old_records(client_ip, current_time)

        if rate_limit_data[client_ip]:
            oldest_request = min(rate_limit_data[client_ip])
            return int(oldest_request + self.time_window)
        return int(current_time + self.time_window)


class APIRateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting middleware specifically for API endpoints
    """

    def __init__(self, get_response):
        super().__init__(get_response)
        # Different rate limits for different types of requests
        self.rate_limiters = {
            # Contact API endpoints
            # 100 requests per 5 minutes
            '/api/v1/contacts/': SimpleRateLimiter(max_requests=100, time_window=300),

            # General API rate limit (fallback)
            # 200 requests per 5 minutes for other APIs
            '/api/': SimpleRateLimiter(max_requests=200, time_window=300),

            # Admin endpoints (more restrictive)
            # 50 requests per 5 minutes
            '/admin/': SimpleRateLimiter(max_requests=50, time_window=300),
        }

    def process_request(self, request):
        """Check rate limits before processing the request"""
        path = request.path

        # Find the most specific rate limiter for this path
        rate_limiter = None
        matched_path = None

        for pattern, limiter in self.rate_limiters.items():
            if path.startswith(pattern):
                if matched_path is None or len(pattern) > len(matched_path):
                    rate_limiter = limiter
                    matched_path = pattern

        # If no specific rate limiter found, skip rate limiting
        if rate_limiter is None:
            return None

        # Check if request is within rate limit
        if not rate_limiter.check_rate_limit(request):
            # Rate limit exceeded
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': f'Too many requests. Maximum {rate_limiter.max_requests} requests per {rate_limiter.time_window} seconds.',
                'retry_after': rate_limiter.get_reset_time(request) - int(time.time()),
                'remaining_requests': 0,
                'limit': rate_limiter.max_requests,
                'window_seconds': rate_limiter.time_window
            }, status=429)

        return None

    def process_response(self, request, response):
        """Add rate limit headers to response"""
        path = request.path

        # Find the rate limiter used for this request
        rate_limiter = None
        for pattern, limiter in self.rate_limiters.items():
            if path.startswith(pattern):
                rate_limiter = limiter
                break

        if rate_limiter:
            # Add rate limit headers
            response['X-RateLimit-Limit'] = str(rate_limiter.max_requests)
            response['X-RateLimit-Window'] = str(rate_limiter.time_window)
            response['X-RateLimit-Remaining'] = str(
                rate_limiter.get_remaining_requests(request))
            response['X-RateLimit-Reset'] = str(
                rate_limiter.get_reset_time(request))

        return response
