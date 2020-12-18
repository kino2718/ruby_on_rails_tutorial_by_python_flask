import hashlib
import html

def template_functions():
    def gravatar_for(user, size=80):
        email_bytes = user.email.lower().encode(encoding='utf-8')
        gravatar_id = hashlib.md5(email_bytes).hexdigest()
        gravatar_url = f'https://secure.gravatar.com/avatar/{gravatar_id}?s={size}'
        user_name = html.escape(user.name, quote=True)
        return f'<img src="{gravatar_url}" alt="{user_name}" class="gravatar"/>'

    def emphasize_error_field(user, name, contents):
        if user.errors.has_errors_with(name):
            return f'<div class="has-error field_with_errors">{contents}</div>'
        else:
            return contents

    return dict(gravatar_for=gravatar_for,
                emphasize_error_field=emphasize_error_field)
