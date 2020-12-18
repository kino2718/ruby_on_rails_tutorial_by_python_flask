def template_functions():
    def full_title(page_title = ''):
        base_title = 'Ruby on Rails Tutorial Sample App'
        if not page_title:
            return base_title
        else:
            return f'{page_title} | {base_title}'

    return dict(full_title=full_title)
