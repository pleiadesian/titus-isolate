import logging
import os
import unittest

from tests.utils import config_logs
from titus_isolate.predict.resource_usage_predictor import URL_FORMAT, get_predictions

config_logs(logging.DEBUG)

single_job_test_body = {
    "jobs": [{
        "job_id": "8505c545-1824-40dd-963d-aacc54a8502e",
        "job_descriptor": {
            "applicationName": "cnn_viz",
            "container": {
                "env": {},
                "image": {
                    "tag": "latest",
                    "name": "khsiao-tf-experiment",
                    "digest": ""
                },
                "entryPoint": ["/apps/cnn_viz/run.sh"],
                "hardConstraints": {
                    "expression": "",
                    "constraints": {}
                },
                "softConstraints": {
                    "expression": "",
                    "constraints": {}
                },
                "command": [],
                "securityProfile": {
                    "iamRole": "TitusContainerDefaultRole",
                    "attributes": {},
                    "securityGroups": ["sg-0be4816f", "sg-14e48170", "sg-c95861b0"]
                },
                "attributes": {},
                "resources": {
                    "allocateIP": False,
                    "shmSizeMB": 0,
                    "signedAddressAllocations": [],
                    "memoryMB": 512,
                    "networkMbps": 128,
                    "diskMB": 10000,
                    "gpu": 0,
                    "cpu": 1,
                    "efsMounts": []
                }
            },
            "service": {
                "enabled": True,
                "capacity": {
                    "max": 1,
                    "desired": 1,
                    "min": 1
                },
                "migrationPolicy": {
                    "systemDefault": {}
                },
                "serviceJobProcesses": {
                    "disableDecreaseDesired": True,
                    "disableIncreaseDesired": False
                },
                "retryPolicy": {
                    "delayed": {
                        "retries": 0,
                        "delayMs": "1000",
                        "initialDelayMs": "0"
                    }
                }
            },
            "jobGroupInfo": {
                "sequence": "",
                "stack": "",
                "detail": ""
            },
            "capacityGroup": "DEFAULT",
            "disruptionBudget": {
                "timeWindows": [],
                "containerHealthProviders": [],
                "rateUnlimited": {},
                "selfManaged": {
                    "relocationTimeMs": "60000"
                }
            },
            "owner": {
                "teamEmail": "khsiao@netflix.com"
            },
            "attributes": {
                "titus.noncompliant": "noSecurityGroups,noIamRole",
                "titus.stack": "main01",
                "titus.cell": "mainvpc",
                "source": "titusui"
            }
        }
    }],
    "resources": ["cpu"]
}


def should_skip() -> bool:
    if os.getenv("CI", None) is not None:
        return True

    if os.getenv("EC_INSTANCE_ID", None) is not None:
        return True

    return False


class TestResourcePredictor(unittest.TestCase):

    @unittest.skipIf(should_skip(), "only run on laptop")
    def test_single_prediction(self):
        client_cert_path = os.getenv("TITUS_ISOLATE_CLIENT_CERT_PATH")
        client_key_path = os.getenv("TITUS_ISOLATE_CLIENT_KEY_PATH")
        body = single_job_test_body
        url = URL_FORMAT.format('us-east-1', 'test')

        response = get_predictions(client_cert_path, client_key_path, url, body)
        self.assertEqual(dict, type(response))
