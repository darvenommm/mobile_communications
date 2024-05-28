from django.views.generic import FormView
from django.forms import ModelForm
from django.http.response import HttpResponse
from django.urls import reverse_lazy

from auth_users.forms import RegistrationForm
from auth_users.models import User


class RegistrationView(FormView):
    success_url = reverse_lazy("calls:home")
    template_name = "auth_users/registration.html"
    form_class = RegistrationForm

    def form_valid(self, form: ModelForm) -> HttpResponse:
        cleaned_data = form.clean()
        (password, _) = (cleaned_data.pop("password"), cleaned_data.pop("repeated_password"))

        new_user = User(**cleaned_data)
        new_user.set_password(password)

        new_user.save()

        return super().form_valid(form)