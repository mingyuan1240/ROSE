from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import RegexValidator as DjangoRegexValidator
from .exceptions import ValidationError
from utils.re import EMAIL_PATTERN, PHONE_NUMBER_PATTERN

class RegexValidator(DjangoRegexValidator):
    def __call__(self, value):
        try:
            super(RegexValidator, self).__call__(value)
        except DjangoValidationError:
            raise ValidationError('regex not match')

class EmailValidator(RegexValidator):
    regex = EMAIL_PATTERN

class DateValidator(RegexValidator):
    regex = r'^\d{4}-\d{2}-\d{2}$'

class PhoneNumberValidator(RegexValidator):
    regex = PHONE_NUMBER_PATTERN

class DateTimeValidator(RegexValidator):
    regex = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(\.\d{3,5})?$'
