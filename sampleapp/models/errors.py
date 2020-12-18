class Errors:
    def __init__(self):
        self.count = 0
        self.messages = {}

    def add(self, name, message):
        el = self.messages.get(name)
        if el is None:
            self.messages[name] = [message]
        else:
            el.append(message)
        self.count += 1

    def __str__(self):
        return f'Errors(count={self.count}, messages={self.messages})'

    def full_messages(self):
        messages = []
        for k,v in self.messages.items():
            messages += v
        return messages

    def has_errors(self):
        return self.count != 0

    def has_errors_with(self, name):
        errors = self.messages.get(name)
        return errors
