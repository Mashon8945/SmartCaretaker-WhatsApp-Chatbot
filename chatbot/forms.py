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

        
""" 
choice_list = {
                    "type": "interactive",
                    "interactive": {
                        "type": "list",
                        "header": {
                            "type": "text",
                            "text": "Choose an action:"
                        },
                        "body": {
                            "text": f"Hello {firstname},\nWe hope you're doing well!\nTo better assist you, please select from the following options:"
                        },
                        "action": {
                            "button": "Actions",
                            "sections": [
                                {
                                    "title": "Options",
                                    "rows": [
                                        {
                                            "id": "1",
                                            "title": "Rent Payment",
                                            "description": "rent payment"
                                        },
                                        {
                                            "id": "2",
                                            "title": "Inquire rent arrears",
                                            "description": "rent arrears"
                                        },
                                        {
                                            "id": "3",
                                            "title": "Request Statement",
                                            "description": "statement"
                                        },
                                        {
                                            "id": "4",
                                            "title": "Other(Please specify)",
                                            "description": "other"
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
"""