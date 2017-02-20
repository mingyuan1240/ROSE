from .fields import Field
from .exceptions import ValidationError

class Validation:
    forbidden_fields = []
    def __new__(cls, *args, **kwargs):
        obj = super(Validation, cls).__new__(cls)
        obj._get_fields()
        return obj

    def _get_fields(self):
        self.fields = {}
        for k in self.__dir__():
            v = getattr(self, k)
            if isinstance(v, Field):
                self.fields[k] = v
        
    def _get_forbidden_keys(self, data):
        return [key for key in data.keys() if key in self.forbidden_fields]
        
    def validate(self, data):
        if not isinstance(data, dict):
            raise ValidationError('dict data required')
        
        errors = {}
        forbidden_keys = self._get_forbidden_keys(data)
        if forbidden_keys:
            errors['forbidden_keys'] = ValidationError(forbidden_keys)
            
        for name, field in self.fields.items():
            if name in self.forbidden_fields:
                continue
            
            if name not in data:
                if field.required:
                    errors[name] = ValidationError('missing "%s"' % name)
                continue

            try:
                field.validate(data[name])
            except ValidationError as e:
                errors[name] = e

        try:
            self.custom_validate(data)
        except ValidationError as e:
            errors['_'] = e

        if errors:
            raise ValidationError(errors)

    def custom_validate(self, data):
        pass

    def require_key(self, data, key):
        if not key in data:
            raise ValidationError('missing %s' % key)

