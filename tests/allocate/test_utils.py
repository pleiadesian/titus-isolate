import json
import unittest

from kubernetes.client import V1Pod

from titus_isolate.allocate.utils import parse_pod

test_pod_json = {
    "apiVersion": "v1",
    "kind": "Pod",
    "metadata": {
        "annotations": {
            "EniId": "eni-085f82953c8a85369",
            "EniIpAddress": "100.122.85.243",
            "IpAddress": "100.122.85.243",
            "IsRoutableIp": "true",
            "ResourceId": "resource-eni-10",
            "containerInfo": "CgZ1YnVudHUiAHINc2xlZXBfZm9yZXZlcnoAggEAigE4YXJuOmF3czppYW06OjE3OTcyNzEwMTE5NDpyb2xlL1RpdHVzQ29udGFpbmVyRGVmYXVsdFJvbGWSATAKATAaC3NnLWYwZjE5NDk0GgtzZy1mMmYxOTQ5NhoLc2ctOGUxZDI4ZTgggAEqATCaAQCgAQDKATQKDFRJVFVTX0pPQl9JRBIkMTYyYWE2ZTctYjMzYS00Y2E1LWE5ZjAtZjg0ODM3OWQ0MTEyygE1Cg1USVRVU19UQVNLX0lEEiQxMjI0MTNkNi03OWYyLTRhMjQtODJlMy0zMDQwYjk4OTBiNDPKARkKEE5FVEZMSVhfRVhFQ1VUT1ISBXRpdHVzygE7ChNORVRGTElYX0lOU1RBTkNFX0lEEiQxMjI0MTNkNi03OWYyLTRhMjQtODJlMy0zMDQwYjk4OTBiNDPKAT4KFlRJVFVTX1RBU0tfSU5TVEFOQ0VfSUQSJDEyMjQxM2Q2LTc5ZjItNGEyNC04MmUzLTMwNDBiOTg5MGI0M8oBPgoWVElUVVNfVEFTS19PUklHSU5BTF9JRBIkMTIyNDEzZDYtNzlmMi00YTI0LTgyZTMtMzA0MGI5ODkwYjQz0gFHc2hhMjU2OjdjMzA4YzhmZWI0MGEyYTA0YTZlZjE1ODI5NTcyN2I2MTYzZGE4NzA4ZThmNjEyNWFiOTU3MTU1N2U4NTdiMjnYAQDgAQroAQHwAQD6AT5yZWdpc3RyeS51cy1lYXN0LTEuc3RyZWFtaW5ndGVzdC50aXR1cy5uZXRmbGl4Lm5ldDo3MDAyL3VidW50dYACAIgCAKoCLwoWdGl0dXMuYWdlbnQub3duZXJFbWFpbBIVZ2hhcnRtYW5uQG5ldGZsaXguY29tqgIeChN0aXR1cy5hZ2VudC5qb2JUeXBlEgdTRVJWSUNFqgI5ChF0aXR1cy5hZ2VudC5qb2JJZBIkMTYyYWE2ZTctYjMzYS00Y2E1LWE5ZjAtZjg0ODM3OWQ0MTEyqgIsCht0aXR1cy5hZ2VudC5hcHBsaWNhdGlvbk5hbWUSDXNsZWVwX2ZvcmV2ZXKyAhESBXNsZWVwEghpbmZpbml0ecACQNAC7t7yzJAu",
            "jobDescriptor": "H4sIAAAAAAAAAK1US3PTMBC+8ysyPpdiubHj5ERLCpQhTAfa4cAwjGyvHVFZMpKcNHTy31nJ7z5u6LbfPrT77ePh1Wzmyb0A5a1mDyigaICWlyVlHCGv2FJlSirEWwEm5+z+NJWlh4bHE+tKq4qzlBomxRdagvXQHKD6lUsFO4zqrFJa0ZSZwwcl68rarC/fn99+vmm0v2XiFFcil0MW2tD0zto6IwQyMG1OHaLhTw0idb+OUjJGsaQ2oEclMVPr01QBNZBdHF4urIssa9XEdZ416xRtIOAukQx2/tIKvk+GBFIpMNMJpQqaiENK1q6qUSSn/kmHFA4Z5BJKqQ6bCwRDEvRwxvSdA4mPr4exjr1Ud5ukst+QIO41lHOJTYKra1TklGvoVZDrjayFsS4/fvaw3pbf2F9wv0TzAWaFgOw8y7Agfd5ExdY3zs7o2PcmrRW2/FrJnHEY192pXNOdq6eL17mfk+V8OfdOZk4MnBi1YgwkC2KIvSFFRsuv0kX2qBIrutcrhFYrslguggXxCfqvFFq8ubFNe9d1ZQ05rblxvgNDT4cGa5lUxEpaTOoQ7cDXCfJXD7EMLUZT6vpVgDZuN7Y0CKPVIj3z4zTOIZn7NKD+nEaQkzAOliGmnkQkOstovPCx4DwiQUgTVJAwXEAcLpJg6U0Seyb3TgXCqMO1ZMKM2osDWuLgZw3zdlstyUzkTGBXOobRd/cknpa5QSK1UUilmU7zs/BxGLT7yg4NTku3rkNYXMXsf4btV1GD2rF06Fp/icZflMz6kmHr6P1EzkAzBZYu8ohcmnCHG1W3G4Wb7hjHozj5IwNOD862g+xEId+M8rXVbWx5nt8PTefT4HbRxyr7C3P99p+d1ZIVym3m00z0QRso2yV4cdhb4j7JBBcY75aeni68QLb2K2FPqoZ1z9D0uLRma3jW7FGv0FjVlU36os4KGHLDZHi+oQLXb0wgktDdnxtWQkNUZC/idLiQCLgVnJXMjPw7rUHX70xkcq+nK9Jei49AudkiCTuWgeoP3fHV8R85L9lROwcAAA==",
            "titus.agent.applicationName": "sleep_forever",
            "titus.agent.jobId": "162aa6e7-b33a-4ca5-a9f0-f848379d4112",
            "titus.agent.jobType": "SERVICE",
            "titus.agent.ownerEmail": "email@address.com"
        },
        "creationTimestamp": "2020-03-23T22:56:36Z",
        "name": "122413d6-79f2-4a24-82e3-3040b9890b43",
        "namespace": "default",
        "resourceVersion": "20494089",
        "selfLink": "/api/v1/namespaces/default/pods/122413d6-79f2-4a24-82e3-3040b9890b43",
        "uid": "8c361a70-6d59-11ea-8f49-0efcd15f3973"
    },
    "spec": {
        "containers": [
            {
                "image": "imageIsInContainerInfo",
                "imagePullPolicy": "IfNotPresent",
                "name": "122413d6-79f2-4a24-82e3-3040b9890b43",
                "resources": {
                    "limits": {
                        "cpu": "1",
                        "memory": "512",
                        "titus/disk": "10k",
                        "titus/gpu": "0",
                        "titus/network": "128"
                    },
                    "requests": {
                        "cpu": "1",
                        "memory": "512",
                        "titus/disk": "10k",
                        "titus/gpu": "0",
                        "titus/network": "128"
                    }
                },
                "terminationMessagePath": "/dev/termination-log",
                "terminationMessagePolicy": "File"
            }
        ],
        "dnsPolicy": "ClusterFirst",
        "enableServiceLinks": True,
        "nodeName": "i-0a76c510b81646393",
        "priority": 0,
        "restartPolicy": "Never",
        "schedulerName": "default-scheduler",
        "securityContext": {},
        "terminationGracePeriodSeconds": 600,
        "tolerations": [
            {
                "effect": "NoExecute",
                "key": "node.kubernetes.io/not-ready",
                "operator": "Exists",
                "tolerationSeconds": 300
            },
            {
                "effect": "NoExecute",
                "key": "node.kubernetes.io/unreachable",
                "operator": "Exists",
                "tolerationSeconds": 300
            }
        ]
    },
    "status": {
        "containerStatuses": [
            {
                "image": "",
                "imageID": "",
                "lastState": {},
                "name": "122413d6-79f2-4a24-82e3-3040b9890b43",
                "ready": True,
                "restartCount": 0,
                "state": {
                    "running": {
                        "startedAt": "2020-03-23T22:56:37Z"
                    }
                }
            }
        ],
        "message": "running",
        "phase": "Running",
        "podIP": "100.122.85.243",
        "qosClass": "Guaranteed",
        "reason": "TASK_RUNNING"
    }
}


class TestAllocateUtils(unittest.TestCase):

    def test_parse_pod_json(self):
        self.maxDiff = None
        pod_str = json.dumps(test_pod_json)
        parsed_pod = parse_pod(pod_str)
        self.assertEqual(V1Pod, type(parsed_pod))
