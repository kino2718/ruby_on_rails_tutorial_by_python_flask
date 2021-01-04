import hashlib
import html

def template_functions():
    def gravatar_for(user, size=80):
        email_bytes = user.email.lower().encode(encoding='utf-8')
        gravatar_id = hashlib.md5(email_bytes).hexdigest()
        gravatar_url = f'https://secure.gravatar.com/avatar/{gravatar_id}?s={size}'
        user_name = html.escape(user.name, quote=True)
        return f'<img src="{gravatar_url}" alt="{user_name}" class="gravatar"/>'

    def make_form_label(user, name, contents):
        prefix = suffix = ''
        if user.errors.has_errors_with(name):
            prefix = '<div class="has-error field_with_errors">'
            suffix = '</div>'
        name = html.escape(name, quote=True)
        contents = html.escape(contents, quote=True)
        s = f'<label for="user_{name}">{contents}</label>'
        return prefix + s + suffix

    def make_form_input(user, el_type, name, el_id):
        prefix = suffix = ''
        if user.errors.has_errors_with(name):
            prefix = '<div class="has-error field_with_errors">'
            suffix = '</div>'
        value = getattr(user, name, None)

        el_type = html.escape(el_type, quote=True)
        name = html.escape(name, quote=True)
        el_id = html.escape(el_id, quote=True)
        s1 = f'<input type="{el_type}" '
        s2 = f'name="{name}" id="{el_id}" class="form-control" />'
        if (value is not None) and (el_type != 'password'):
            value = html.escape(value, quote=True)
            s = s1 + f'value="{value}" ' + s2
        else:
            s = s1 + s2
        return prefix + s + suffix

    return dict(gravatar_for=gravatar_for,
                make_form_label=make_form_label,
                make_form_input=make_form_input)
