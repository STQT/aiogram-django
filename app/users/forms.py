from ckeditor.widgets import CKEditorWidget

from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User


class UserAdminCreationForm(admin_forms.UserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        error_messages = {
            "username": {"unique": _("This username has already been taken.")},
        }


class CustomCKEditorWidget(CKEditorWidget):
    def use_required_attribute(self, initial):
        return False

    def value_from_datadict(self, data, files, name):
        value = data.get(name, None)
        if not value:
            return None
        value = value.replace("<p>", "").replace("</p>", "").replace("&#39;", "’").replace("&rsquo;", "’").replace("&nbsp;", "")  # noqa
        return value
