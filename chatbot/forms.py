# forms.py

from django import forms
from .models import Assignment, Customers, Houses

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['tenant', 'house']

    def __init__(self, *args, **kwargs):
        super(AssignmentForm, self).__init__(*args, **kwargs)
        self.fields['tenant'].label_from_instance = lambda obj: f"{obj.firstname} {obj.lastname}"
        self.fields['house'].label_from_instance = lambda obj: f"H({obj.id}) -- {obj.house_type}"

        self.fields['tenant'].queryset = Customers.objects.filter(is_active=False)
        self.fields['house'].queryset = Houses.objects.filter(vacancy__in=['VACANT', 'BOOKED'])
