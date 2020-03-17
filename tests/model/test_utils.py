import unittest

from titus_isolate.model.utils import get_duration_predictions, decode_job_descriptor, parse_kubernetes_value


class TestWorkload(unittest.TestCase):

    def test_get_duration_predictions(self):
        input = "0.05=1.0;0.1=2.0;0.15=3.0;0.2=4.0;0.25=5.0;0.3=6.0;0.35=7.0;0.4=8.0;0.45=9.0;0.5=10.0;0.55=11.0;0.6=12.0;0.65=13.0;0.7=14.0;0.75=15.0;0.8=16.0;0.85=17.0;0.9=18.0;0.95=19.0"
        predictions = get_duration_predictions(input)
        self.assertEqual(19, len(predictions))

        percentile_step = 0.05
        duration_step = 1.0
        expected_percentile = 0
        expected_duration = 0

        for p in predictions:
            expected_percentile += percentile_step
            expected_duration += duration_step
            self.assertAlmostEqual(expected_percentile, p.get_percentile())
            self.assertAlmostEqual(expected_duration, p.get_duration())

    def test_empty_predictions_input(self):
        input = ""
        predictions = get_duration_predictions(input)
        self.assertEqual(0, len(predictions))

    def test_deserialize_job_descriptor(self):
        encoded_job_descriptor = 'H4sIAAAAAAAAAH1UXXOrNhD9K4yeqQtcf2CemjRp607dybjp9KHpdAQsWA1IVBJ2mIz/+z0SOPX1TcML0u7qaPfsWb0ydZSkWfbKLPH2vuWiYRmr91zblkv5nSRbNeJlVqiWnULGu64RBbdCyV95Swg1DVH3d6U0HYATsoJ3vBB2+FGrvoP/7v6Hm99/eYTnH5V740ZWyl1oLC+eEQFXSXa8GGtD//YkC4ftbiyUhG/K8W2zI6N6XZDx1q5nWTyLQla7Ff4ttUoP21uWLeIE8MI8u00c4QsZajoq/bzNOxyPkzRkVJmt6qXF/s+/UGXTKBRJmweWVbwxhKz2rUNYzrEUtaRy092UpSZjbsZgMOJPn1wFRa9BwYNWlWjI1zqZPAEujpn6myqq4vV8PXdFY5f43XLcpRSXSUopQzqCtzvlcBjXMuNHk8GSZfFqvUpWcRTjWKYR8O2jsL35/szRHVW8b6w/ipqs1SLvrafshCxFy2ufmxwb2ecgoEek5TW2Deo31vVG1G6BTu95slhmq+JTlBZpRfk84gmP5nxJVbxIk/UC6eTLePmp5OkqQvLVMk4WPIcjXixWlC5WebL2MvoiGfAvrR4elJB2bADUBvWVnienL6QhZCUkGHSEkDyM54yqLOo1VqNiO4FBu+WV8eQ1oPvOtem2L2uyrvJr24OCuAc/DEPnxU1NteUSRJVIQdO504+ipS2Ql05Q74DvQN4FTC8b0QoLEMRanP1DyFIdzbnYqWE/EW/sHqo5iJL0WU30YkmaUV4XiemDKOhnld+/2IupcyGtkJC1GyojNO5065a/4O+Z5nnjjFb35EryxF+VXVLDByp3F85wNLqiYz9E7qRw/Yu84s/pIHtMpRkHE7S42zay0MQN3Z0TmmZqct/Re26gtqLWnu6v+zIYS+0k8O1V2OlaYKAcczFzt6AHt8P/PnDhFCmVxBYvHZd2Nr5NZvblCO/wSrlsEfvb1WyzsyGovSWQygaG7Mfw05Bf4G7exn5zsw3cgF8gjc8ffB6yFx+DX+tz1lDNi+GNuf8UFeCVDo7C7oMxJHhrQtB5erPg9cm34YllTx824omd3s+qQh967VrD3ic1vCIj/Gp4z7gFNY0X7CFau3UUxej/ZyNzNvjWBgAA'
        decoded_job_descriptor = decode_job_descriptor(encoded_job_descriptor)
        self.assertEqual('sleep_forever', decoded_job_descriptor['applicationName'])

    def test_parse_kubernetes_values(self):
        parsed_value = parse_kubernetes_value("10k")
        self.assertEqual("10000", parsed_value)
