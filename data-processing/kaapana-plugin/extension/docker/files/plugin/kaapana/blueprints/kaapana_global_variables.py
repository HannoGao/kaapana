import os
BATCH_NAME = 'batch'
WORKFLOW_DIR = '/data'
INSTANCE_NAME = os.getenv('INSTANCE_NAME', None)
assert INSTANCE_NAME
ADMIN_NAMESPACE = os.getenv('ADMIN_NAMESPACE', None)
assert ADMIN_NAMESPACE
SERVICES_NAMESPACE = os.getenv('SERVICES_NAMESPACE', None)
assert SERVICES_NAMESPACE
JOBS_NAMESPACE = os.getenv('JOBS_NAMESPACE', None)
assert JOBS_NAMESPACE
EXTENSIONS_NAMESPACE = os.getenv('EXTENSIONS_NAMESPACE', None)
assert EXTENSIONS_NAMESPACE

