import unittest

from titus_isolate.predict.resource_usage_prediction import ResourceUsagePredictions, CPU

simple_test_input = {
    'model_version': '0.1',
    'model_instance_id': 'af66ac6b-feaa-4e90-877e-6b3c910f175a',
    'prediction_ts_ms': '1584979201000',
    'predictions': [{
        'job_id': '8505c545-1824-40dd-963d-aacc54a8502e',
        'cpu': [{
            'quantile': 'p50',
            'horizon_minutes': ['0-10', '10-30', '30-60', '60-360'],
            'preds': [0.693147, 0.693147, 0.693147, 0.693147]
        }, {
            'quantile': 'p95',
            'horizon_minutes': ['0-10', '10-30', '30-60', '60-360'],
            'preds': [0.71392, 0.713309, 0.713462, 0.712815]
        }],
        'memMB': None,
        'net_transMbps': None,
        'net_recvMbps': None
    }],
    'meta_data': None
}


class TestResourceUsagePredictionObjects(unittest.TestCase):

    def test_simple_parse(self):
        p = ResourceUsagePredictions(simple_test_input)
        self.assertEqual('0.1', p.model_version)
        self.assertEqual('af66ac6b-feaa-4e90-877e-6b3c910f175a', p.model_instance_id)
        self.assertEqual(1584979201000, p.prediction_ts_ms)
        self.assertEqual(1, len(p.predictions))

        p0 = p.predictions['8505c545-1824-40dd-963d-aacc54a8502e']
        t0 = p0.resource_type_predictions
        self.assertEqual(4, len(t0))
        self.assertEqual(4, len(t0[CPU].horizons['p95']))
        self.assertEqual(4, len(t0[CPU].predictions['p95']))
        self.assertEqual('0-10', t0[CPU].horizons['p95'][0])
        self.assertEqual(0.71392, t0[CPU].predictions['p95'][0])
