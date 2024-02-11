import datetime
from datetime import timedelta, datetime
from django.db.models import Max, Min

today = datetime.now().date()


def this_week():
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return [start_of_week + timedelta(days=x) for x in range((end_of_week - start_of_week).days + 1)]


def next_week():
    start_of_next_week = today + timedelta(days=(7 - today.weekday()))
    end_of_next_week = start_of_next_week + timedelta(days=6)
    return [start_of_next_week + timedelta(days=x) for x in range((end_of_next_week - start_of_next_week).days + 1)]


def this_month():
    start_of_month = today.replace(day=1)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    return [start_of_month + timedelta(days=x) for x in range((end_of_month - start_of_month).days + 1)]


def next_month():
    start_of_next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
    end_of_next_month = (start_of_next_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    return [start_of_next_month + timedelta(days=x) for x in
            range((end_of_next_month - start_of_next_month).days + 1)]


def half_year():
    start_of_previous_month = today - timedelta(days=90)
    end_of_previous_month = today - timedelta(days=1)
    start_of_next_month = today + timedelta(days=91)
    days = [start_of_previous_month + timedelta(days=x) for x in
            range((end_of_previous_month - start_of_previous_month).days + 1)]
    days += [today + timedelta(days=x) for x in range((start_of_next_month - today).days + 1)]
    return days


def get_days(tasks):
    min_max_dates = tasks.aggregate(Min('created_at'), Max('deadline'))

    if min_max_dates['created_at__min'] is not None and min_max_dates['deadline__max'] is not None:
        start_date = min_max_dates['created_at__min'].date()
        end_date = min_max_dates['deadline__max']
        days = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

        return days

    return []


def get_custom_days(start_date_str, end_date_str):
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

        days = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
        return days
    except (ValueError, TypeError):
        return []
