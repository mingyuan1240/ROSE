from django.db import models
from common.models import ConvertMixin

class Patient(ConvertMixin, models.Model):
    name = models.CharField(max_length=10)
    number = models.CharField(max_length=10)
    no = models.CharField(max_length=10)
    date = models.DateField(null=True)
    age = models.SmallIntegerField(null=True)
    gender = models.SmallIntegerField(null=True)
    cell_diagnosis = models.TextField()
    pathology_diagnosis = models.CharField(max_length=256, null=True)
    images = models.ManyToManyField('Image')
    create_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-create_timestamp']

    def detail(self):
        d = self.to_dict(exclude=['create_timestamp', 'images'])
        d['images'] = [image.detail() for image in self.images.all()]
        d['smears'] = [s.detail() for s in self.smear_set.all()]
        return d

    def brief(self):
        d = self.to_dict(exclude=['images'])
        smear = self.smear_set.first()
        if smear:
            d['diagnosis'] = smear.diagnosis
            d['weasand_lens'] = smear.weasand_lens
        else:
            d['diagnosis'] = None
            d['weasand_lens'] = None
        return d

class Image(ConvertMixin, models.Model):
    url = models.URLField()
    type = models.SmallIntegerField(default=0)
    create_timestamp = models.DateTimeField(auto_now_add=True)
    
    def detail(self):
        return self.to_dict(exclude=['create_timestamp'])

    class Meta:
        ordering = ['-create_timestamp']
    
class Smear(ConvertMixin, models.Model):
    location = models.CharField(max_length=32)
    type = models.SmallIntegerField(default=0)
    weasand_lens = models.SmallIntegerField()
    diagnosis = models.TextField()
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, null=False)
    images = models.ManyToManyField('Image')

    def detail(self):
        d = self.to_dict(exclude=['images'])
        d['images'] = [image.detail() for image in self.images.all()]
        return d
    
