from .exceptions import ValidationError

class Field:
    allowed_type = None
    
    def __init__(self, required=False, null=False, strict=True, message=None, validators=[]):
        self.required = required
        self.null = null
        self.strict = strict
        self.validators = validators
        self.message = message

    def validate(self, value):
        if value is None:
            if not self.null:
                raise ValidationError('null')
            else:
                return
        
        if self.allowed_type:
            if self.strict and not isinstance(value, self.allowed_type):
                raise ValidationError('expect type "%s" but get "%s"' % (self.allowed_type.__name__, type(value).__name__))
            try:
                value = self.allowed_type(value)
            except ValueError:
                raise ValidationError('value can not convert to "%s"' % self.allowed_type)
            
        self._validate(value)
                
        for validator in self.validators:
            validator(value)

    def _validate(self, value):
        pass

class CharField(Field):
    allowed_type = str
    
    def __init__(self, max_length=None, empty=False, *args, **kwargs):
        self.max_length = max_length
        self.empty = empty
        
        super(CharField, self).__init__(*args, **kwargs)

    def _validate(self, value):
        if self.max_length and len(value) > self.max_length:
            raise ValidationError('str length over then %d' % self.max_length)
        if not self.empty and value == '':
            raise ValidationError('str empty')

class IntegerField(Field):
    allowed_type = int

    def __init__(self, min_value=None, max_value=None, *args, **kwargs):
        self.max_value = max_value
        self.min_value = min_value
        
        super(IntegerField, self).__init__(*args, **kwargs)

    def _validate(self, value):
        if self.max_value and value > self.max_value:
            raise ValidationError('integer over then max value: %d' % self.max_value)
        if self.min_value and value < self.min_value:
            raise ValidationError('integer little then min value: %d' % self.max_value)

class IdField(IntegerField):
    def __init__(self, model, require_exist=True, *args, **kwargs):
        super(IdField, self).__init__(*args, **kwargs)
        self.model = model
        self.require_exist = require_exist

    def _validate(self, value):
        super(IdField, self)._validate(value)

        if self.require_exist and value is not None and value != 0:
            if self.model.objects.filter(id=value).first() is None:
                raise ValidationError('object not exist')

class ListField(Field):
    allowed_type = list

    def __init__(self, item_field=None, min_length=0, max_length=None, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)
        self.max_length = max_length
        self.min_length = min_length
        self.item_field = item_field

    def _validate(self, value):
        if len(value) < self.min_length:
            raise ValidationError('list size less then %d' % self.min_length)
            
        if self.max_length and len(value) > self.max_length:
            raise ValidationError('list size over then %d' % self.max_length)

        if self.item_field:
            errors = {}
            for idx, item in enumerate(value):
                try:
                    self.item_field.validate(item)
                except ValidationError as e:
                    errors[idx] = e
            if errors:
                raise ValidationError(errors)
                    
class ValidationField(Field):
    allowed_type = dict
    def __init__(self, validation_class, *args, **kwargs):
        super(ValidationField, self).__init__(*args, **kwargs)
        self.validation_class = validation_class

    def _validate(self, value):
        validation = self.validation_class()
        validation.validate(value)


class BoolField(Field):
    allowed_type = bool
    
    def __init__(self, *args, **kwargs):
        super(BoolField, self).__init__(*args, **kwargs)

class ChoiceField(Field):
    def __init__(self, choices=None, *args, **kwargs):
        super(ChoiceField, self).__init__(*args, **kwargs)
        self.choices = choices

    def _validate(self, value):
        if self.choices:
            if value not in self.choices:
                raise ValidationError("'%s' is not a valid value" % value)
            
        
