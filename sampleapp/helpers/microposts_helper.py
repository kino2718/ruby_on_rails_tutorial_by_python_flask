from datetime import datetime, timezone

def template_functions():
    # 大まかな値で正確ではない
    def time_ago_in_words(t):
        dt = datetime.now(timezone.utc) - t
        ddays = dt.days
        dminutes = dt.seconds // 60

        if ddays == 0:
            if dminutes == 0:
                return 'less than a minute'
            if dminutes == 1:
                return '1 minute'
            if dminutes < 60:
                return f'{dminutes} minutes'
            if dminutes < 120:
                return '1 hour'
            return f'{dminutes//60} hours'

        if ddays == 1:
            return '1 day'
        if ddays < 7:
            return f'{ddays} days'
        if ddays < 14:
            return '1 week'
        if ddays < 30:
            return f'{ddays//7} weeks'
        if ddays < 60:
            return '1 month'
        if ddays < 365:
            return f'{ddays//30} month'
        if ddays < 730:
            return '1 year'
        return f'ddays//365 years'

    return dict(time_ago_in_words=time_ago_in_words)
