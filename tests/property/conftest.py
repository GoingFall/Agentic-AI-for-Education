"""属性测试：禁用 API 限流，避免 hypothesis 多例触发 429。"""
import os
os.environ.setdefault("API_RATE_LIMIT_DISABLED", "1")
