from common.view import JsonView, ListModelView
from common.models import update_foreigns
from django.conf import settings
from lib.alicloud import get_token
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
            smear.save()
            smear.images = self._save_images(s.get('images') or [])
            
        return patient.detail()

    def _save_images(self, images_d):
        images = [Image.from_dict(im) for im in images_d]
        [im.save() for im in images]
        return images

class UpdatePatientView(JsonView):
    def put(self, request, _id):
        data = request.json
        patient = Patient.objects.filter(pk=_id).first()
        if not patient:
            return JsonView.NOT_FOUND
        patient.merge(data)
        patient.save()
        update_foreigns(patient, 'images', (data.get('images') or []))
        self._update_smears(patient, data.get('smears') or [])
        return patient.detail()

    def _update_smears(self, patient, smears):
        smear_ids = [s['id'] for s in smears if s.get('id')]
        patient.smear_set.exclude(id__in=smear_ids).delete()

        for smear_d in smears:
            if smear_d.get('id'):
                smear = Smear.objects.get(pk=smear_d['id'])
                smear.merge(smear_d)
                smear.save()
                update_foreigns(smear, 'images', smear_d.get('images') or [])
            else:
                smear = Smear.from_dict(smear_d)
                smear.patient = patient
                smear.save()
                images = [Image.from_dict(image) for image in smear_d.get('images') or []]
                [im.save() for im in images]
                smear.images = images

class PatientDetailView(JsonView):
    def get(self, request, _id):
        try:
            return Patient.objects.get(pk=_id).detail()
        except ObjectDoesNotExist as e:
            return JsonView.NOT_FOUND
            
class DeletePatientView(JsonView):
    def delete(self, request, _id):
        try:
           Patient.objects.get(pk=_id).delete()
           return 'ok'            
        except ObjectDoesNotExist as e:
            return JsonView.NOT_FOUND
        
class GetQiniuTokenView(JsonView):
    def get(self, request):
        return get_token()

class ListPatientView(ListModelView):
    def get_model_list(self, request):
        query = Patient.objects.all()
        p = request.GET.get('pathology')
        if p:
            query = query.filter(pathology_diagnosis=p)
        return query
        
