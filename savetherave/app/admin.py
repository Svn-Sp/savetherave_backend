from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin

from app.models import User


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets,  # original form fieldsets, expanded
        (  # new fieldset added on to the bottom
            "Personal data",  # group heading of your choice; set to None for a blank space instead of a header
            {
                "fields": (
                    "profile_picture",
                    "birthday",
                    "gender",
                    "phone_number",
                    "received_requests",
                    "friends",
                    "instagram",
                ),
            },
        ),
    )


admin.site.register(User, CustomUserAdmin)
