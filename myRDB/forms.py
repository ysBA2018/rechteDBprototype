from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('identity',)

    # Validation von xvnummer abgeschaltet da dieses bei passwortvalidierung mit dabei
    def clean_identity(self):
        identity = self.cleaned_data['identity']
        try:
            user = User.objects.exclude(pk=self.instance.pk).get(identity=identity)
            self.errors['identity'] = self.error_class()
        except User.DoesNotExist:
            pass
        return identity

    def save(self, commit=True):
        user = None
        identity = self.cleaned_data['identity']
        identity_upper = identity.upper()

        print(identity, identity_upper)
        try:
            user = User.objects.get(identity=identity)
            print("User: ", user.__str__(), " mit Identity_lower existiert")
            if user.password == "":
                print("User mit Identity_lower existiert - password is leer -> pw wird gesafet")
                user.set_password(self.cleaned_data['password1'])
                user.save()
            else:
                print("User mit Identity_lower existiert und hat pw!")
                forms.ValidationError("User mit Identity_lower existiert und hat pw!")
                return user
                # messages.info(HttpRequest(),"User exists and has a Password")
        except(KeyError, User.DoesNotExist):
            try:
                user = User.objects.get(identity=identity_upper)
                print("User: ", user.__str__(), " mit Identity_upper existiert")
                if user.password == "":
                    print("User mit Identity_upper existiert - password is leer -> pw wird gesafet")
                    user.set_password(self.cleaned_data['password1'])
                    user.save()
                else:
                    forms.ValidationError("User mit Identity_upper existiert und hat pw!")
                    print("User mit Identity_upper existiert und hat pw!")
                return user
                # messages.info(HttpRequest(),"User exists and has a Password")
            except(KeyError, User.DoesNotExist):
                print("User existiert nicht - wird neu angelegt")
                user = super(CustomUserCreationForm, self).save(commit=False)
                user.set_password(self.cleaned_data['password1'])

                if commit:
                    user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('identity',)
        error_css_class = 'error'


class SomeForm(forms.Form):
    start_import = forms.FileInput()
