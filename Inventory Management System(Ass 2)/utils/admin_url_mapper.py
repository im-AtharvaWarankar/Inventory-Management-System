from django.utils.html import format_html
from django.urls import reverse


def link_field(field_name):
    """
    Converts a foreign key value into clickable links.

    If field_name is 'parent', link text will be str(obj.parent)
    Link will be admin url for the admin url for obj.parent.id:change
    """
    def _link_field(obj):
        linked_obj = getattr(obj, field_name)
        if linked_obj is None:
            return '-'
        app_label = linked_obj._meta.app_label
        model_name = linked_obj._meta.model_name
        view_name = f'admin:{app_label}_{model_name}_change'
        link_url = reverse(view_name, args=[linked_obj.pk])
        return format_html('<a href="{}">{}</a>', link_url, linked_obj)

    _link_field.short_description = field_name  # Sets column name
    return _link_field

    # search_fields = ('userId__firstName', 'userId__lastName', 'userId__username', 'userId__email')
    # list_per_page = 10
    #
    # add pagination, linkify, add/filter
    """
    from django.utils.html import format_html
    def profile(self, obj):
        return format_html('<img src="{}" width="100" height="100" alt="image not availabile"/>', obj.profilePicture)
    """
