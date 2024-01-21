import datetime
from config.env import env
from datetime import timedelta

# For more settings
# Read everything from here - https://styria-digital.github.io/django-rest-framework-jwt/#additional-settings

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}