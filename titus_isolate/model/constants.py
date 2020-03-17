WORKLOAD_JSON_FORMAT = '/var/lib/titus-environments/{}.json'
WORKLOAD_ENV_FORMAT = '/var/lib/titus-environments/{}.env'
WORKLOAD_ENV_LINE_REGEXP = r'(\w+)="([^"]*)"'

WORKLOAD_ENV_CPU_KEY = 'TITUS_NUM_CPU'
WORKLOAD_ENV_MEM_KEY = 'TITUS_NUM_MEM'
WORKLOAD_ENV_DISK_KEY = 'TITUS_NUM_DISK'
WORKLOAD_ENV_NETWORK_KEY = 'TITUS_NUM_NETWORK_BANDWIDTH'

WORKLOAD_JSON_APP_NAME_KEY = 'appName'
WORKLOAD_JSON_PASSTHROUGH_KEY = 'passthroughAttributes'
WORKLOAD_JSON_OWNER_KEY = 'titus.agent.ownerEmail'
WORKLOAD_JSON_IMAGE_KEY = 'fullyQualifiedImage'
WORKLOAD_JSON_IMAGE_DIGEST_KEY = 'imageDigest'
WORKLOAD_JSON_PROCESS_KEY = 'process'
WORKLOAD_JSON_COMMAND_KEY = 'command'
WORKLOAD_JSON_ENTRYPOINT_KEY = 'entrypoint'
WORKLOAD_JSON_JOB_TYPE_KEY = 'titus.agent.jobType'
WORKLOAD_JSON_CPU_BURST_KEY = 'allowCpuBursting'
WORKLOAD_JSON_OPPORTUNISTIC_CPU_KEY = 'task.opportunisticCpuCount'
WORKLOAD_JSON_RUNTIME_PREDICTIONS_KEY = 'titus.agent.runtimePredictionsAvailable'
WORKLOAD_JSON_READ_ATTEMPTS = 5
WORKLOAD_JSON_READ_SLEEP_SECONDS = 0.1

WORKLOAD_JSON_RUNSTATE_KEY = 'runState'
WORKLOAD_JSON_LAUNCHTIME_KEY = 'launchTimeUnixSec'

CPU = "cpu"
MEMORY = "memory"
EPHEMERAL_STORAGE = "ephemeral-storage"
TITUS_DISK = "titus/disk"
TITUS_NETWORK = "titus/network"

APP_NAME = "applicationName"
COMMAND = "command"
CONTAINER = "container"
CPU_BURSTING = "titusParameter.agent.allowCpuBursting"
ENTRYPOINT = "entryPoint"
IMAGE = "image"
JOB_DESCRIPTOR = "jobDescriptor"
NAME = "name"
OWNER_EMAIL = "titus.agent.ownerEmail"
