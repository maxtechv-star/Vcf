# Server-side configuration (top-side lines). Use environment variables in production.
import os

ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '1542')

# Optional: allow a different VCF filename prefix
VCF_PREFIX = os.environ.get('VCF_PREFIX', 'status_views_contacts')