from django_addanother.widgets import WidgetWrapperMixin
from django_addanother.views import BasePopupMixin
from django.forms import Widget
from django.contrib.admin.views.main import IS_POPUP_VAR
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

DEFAULT_ADD_ICON = 'images/add-icon.png'
DEFAULT_EDIT_ICON = 'images/edit-icon.png'
DEFAULT_DELETE_ICON = 'images/delete-icon.png'


class DeletePopupMixin(BasePopupMixin):
    POPUP_ACTION = 'delete'


class CRUDWidgetWrapper(WidgetWrapperMixin, Widget):
    template = 'crud/wrapper.html'

    class Media:
        css = {
            'all': ('django_addanother/addanother.css',)
        }
        js = (
            'django_addanother/django_jquery.js',
            'admin/js/admin/RelatedObjectLookups.js',
        )

    def __init__(self, widget, add_related_url,
                 edit_related_url,
                 delete_related_url,
                 add_icon=DEFAULT_ADD_ICON,
                 edit_icon=DEFAULT_EDIT_ICON,
                 delete_icon=DEFAULT_DELETE_ICON):

        if isinstance(widget, type):
            widget = widget()
            
        self.widget = widget
        self.attrs = widget.attrs
        self.add_related_url = add_related_url
        self.add_icon = add_icon
        self.edit_related_url = edit_related_url
        self.edit_icon = edit_icon
        self.delete_related_url = delete_related_url
        self.delete_icon = delete_icon

    def render(self, name, value, *args, **kwargs):
        url_params = "%s=%s" % (IS_POPUP_VAR, 1)
        context = {
            'widget': self.widget.render(name, value, *args, **kwargs),
            'name': name,
            'url_params': url_params,
            'add_related_url': self.add_related_url,
            'add_icon': self.add_icon,
            'edit_related_url': self.edit_related_url,
            'edit_icon': self.edit_icon,
            'delete_related_url': self.delete_related_url,
            'delete_icon': self.delete_icon,
        }
        return mark_safe(render_to_string(self.template, context))
