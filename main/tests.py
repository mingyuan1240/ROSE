import json
from django.test import TestCase

class Test(TestCase):
    def test_create_patient(self):
        data = dict(name='fucker', number='123',
                    images=[dict(url='p/a', type=1), dict(url='t/h', type=2)]
        )
        rsp = self.client.post('/v0/patient', json.dumps(data), content_type='application/json')
        self.assertEqual(200, rsp.status_code) 


