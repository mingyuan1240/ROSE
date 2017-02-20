from common.view import JsonView
from .validations import *
from main.models import *

class CreatePatientView(JsonView):
    validation_class = CreatePatientValidation

    def post(self, request):
        patient = Patient.from_dict(request.json)
        patient.save()
        patient.images = self._save_images(request.json.get('images') or [])

        for s in (request.json.get('smears') or []):
            smear = Smear.from_dict(s)
            smear.patient = patient
            smear.images = self._save_images(s.get('images') or [])
            
        return 'ok'

    def _save_images(self, images_d):
        images = [Image.from_dict(im) for im in images_d]
        [im.save() for im in images]
        return images
