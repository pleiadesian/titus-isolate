# CPU ALLOCATOR CONSTANTS
ALLOCATOR_KEY = 'TITUS_ISOLATE_ALLOCATOR'
AB_TEST = 'AB_TEST'
IP = 'IP'
GREEDY = 'GREEDY'
NOOP = 'NOOP'
NOOP_RESET = 'NOOP_RESET'
DEFAULT_ALLOCATOR = NOOP
CPU_ALLOCATORS = [AB_TEST, IP, GREEDY, NOOP, NOOP_RESET]

CPU_ALLOCATOR_A = 'CPU_ALLOCATOR_A'
CPU_ALLOCATOR_B = 'CPU_ALLOCATOR_B'

PROPERTY_URL_ROOT = 'http://localhost:3002/properties'

# CGROUP FILE
WAIT_CGROUP_FILE_KEY = 'TITUS_ISOLATE_WAIT_CGROUP_FILE_SEC'
DEFAULT_WAIT_CGROUP_FILE_SEC = 90

# JSON FILE
WAIT_JSON_FILE_KEY = 'TITUS_ISOLATE_WAIT_JSON_FILE_SEC'
DEFAULT_WAIT_JSON_FILE_SEC = 10

# Static environment variables
EC2_INSTANCE_ID = "EC2_INSTANCE_ID"

PROPERTIES = [
    ALLOCATOR_KEY,
    CPU_ALLOCATOR_A,
    CPU_ALLOCATOR_B,
    EC2_INSTANCE_ID,
    WAIT_CGROUP_FILE_KEY,
    WAIT_JSON_FILE_KEY]

