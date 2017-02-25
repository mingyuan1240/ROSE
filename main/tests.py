import json
from django.test import TestCase

class Test(TestCase):
    def test_create_patient(self):
        data = dict(name='fucker', number='123',
                    images=[dict(url='p/a', type=1), dict(url='t/h', type=2)]
        )
        rsp = self.client.post('/v0/patient', json.dumps(data), content_type='application/json')
        self.assertEqual(200, rsp.status_code) 

    def test_get_upload_token(self):
        bucket = 'cobra-travo'
        filename = 'file0'
        expires = 3600 * 24 * 365 * 100
        rsp = self.client.get('/v0/upload/file/token?bucket=%s&filename=%s&expires=%d' % (bucket, filename, expires))
        self.assertEqual(200, rsp.status_code)
