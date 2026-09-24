from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory

from .models import CalibrationResult, Certificate, Instrument, Job, JobDocument, JobLineItem, User


class SignUpForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.Role.choices)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "role", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data["role"]
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        if commit:
            user.save()
        return user


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["customer_name", "customer_address", "po_number", "quantity", "committed_date"]
        widgets = {
            "customer_address": forms.Textarea(attrs={"rows": 2}),
            "committed_date": forms.DateInput(attrs={"type": "date"}),
        }


class JobLineItemForm(forms.ModelForm):
    class Meta:
        model = JobLineItem
        fields = ["instrument", "model",  "range_from", "range_to", "unit", "quantity", "assigned_to",  "calibration_points",
            "calibration_validity", "reference_procedure",]

        widgets = {
            "range_from": forms.NumberInput(attrs={
                "placeholder": "From",
                "step": "any",
            }),
            "range_to": forms.NumberInput(attrs={
                "placeholder": "To",
                "step": "any",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["instrument"].queryset = Instrument.objects.filter(is_active=True)
        self.fields["assigned_to"].queryset = User.objects.filter(role=User.Role.TECHNICIAN)
        for f in self.fields.values():
            f.widget.attrs.setdefault("class", "form-control")


JobLineItemFormSet = inlineformset_factory(
    Job,
    JobLineItem,
    form=JobLineItemForm,
    extra=1,
    can_delete=True,
)


class JobDocumentForm(forms.ModelForm):
    class Meta:
        model = JobDocument
        fields = ["name", "file"]
        widgets = {"name": forms.TextInput(attrs={"placeholder": "Document name"})}


JobDocumentFormSet = inlineformset_factory(
    Job,
    JobDocument,
    form=JobDocumentForm,
    extra=1,
    can_delete=True,
)


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = [
            "device_serial", "device_manufacturer", "device_resolution", "device_accuracy",
            "working_standard_name", "working_standard_serial", "working_standard_certificate_no",
            "lab_temperature", "lab_humidity", "ambient_pressure", "reference_procedure",
            "temperature_variation", "condition_notes",
            "calibration_date", "issue_date", "calibrated_by", "approved_signatory",
        ]
        widgets = {
            "condition_notes": forms.Textarea(attrs={"rows": 2}),
            "calibration_date": forms.DateInput(attrs={"type": "date"}),
            "issue_date": forms.DateInput(attrs={"type": "date"}),
        }


class CalibrationResultForm(forms.ModelForm):
    class Meta:
        model = CalibrationResult

        fields = [
            "applied_value",
            "upward_reading",
            "downward_reading",
            "mean_value",
            "deviation",
            "uncertainty",
            "remarks",
        ]

        


CalibrationResultFormSet = inlineformset_factory(
    Certificate,
    CalibrationResult,
    form=CalibrationResultForm,
    extra=1,
    can_delete=True,
)


class InstrumentForm(forms.ModelForm):
    class Meta:
        model = Instrument
        # is_active is intentionally excluded: new instruments are active by
        # default (model default) and are deactivated later via the toggle
        # button, not through this add form.
        fields = ["name", "default_model", "default_range"]


class TechnicianForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.TECHNICIAN
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
