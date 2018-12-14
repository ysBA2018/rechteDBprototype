from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from myRDB.forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User, Question


# Register your models here.


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ['identity', ]


admin.site.register(Question)
admin.site.register(User, CustomUserAdmin)
AUTH_USER_MODEL = 'abstract_base_user_sample.User'
