from todobot.slack_post import SlackPost
from todobot.todoist_proxy import Todoist

def post_tasks_test():
    slack_post = SlackPost()
    todoist = Todoist()
    tasks = todoist.get_tasks()
    slack_post.post_all_task_to_chat(tasks)

def post_reminder_test():
    slack_post = SlackPost()
    todoist = Todoist()
    open, closed, with_reminders = todoist.get_tasks()
    slack_post.post_reminder(with_reminders[0])


def update_timer_test():
    todoist = Todoist()
    tasks = Todoist.get_tasks()
    todoist.set_reminder(tasks['id'], )

def get_tasks_test():
    todoist = Todoist()
    tasks = todoist.get_tasks()
    print(tasks[0]['id'])
    print(todoist.task_by_id(tasks[0]['id']))

def update_home():
    slack_post = SlackPost()
    todoist = Todoist()
    pending, completed, with_reminders = todoist.get_tasks()
    slack_post.post_task_list_at_home(pending, completed, with_reminders)

def test_post_completed_task():
    slack_post = SlackPost()
    todoist = Todoist()
    pending, completed, with_reminders = todoist.get_tasks()
    slack_post.post_task_list_at_home(pending, completed, with_reminders)

def test_add_reminder():
    todoist = Todoist()
    api = todoist.api
    x = {'due': {'date': '2021-03-20T19:00:00',
             'is_recurring': False,
             'lang': 'en',
             'string': '20 Mar 19:00',
             'timezone': None},
     'id': 2341115736,
     'is_deleted': 0,
     'item_id': 4672920807,
     'notify_uid': 32981441,
     'service': 'default',
     'type': 'absolute'}
    api.reminders.add(4672920807, due=x['due'], notify_uid = 32981441, service='default', type='absolute')
    api.commit()

def test_set_reminder2():
    todoist = Todoist()
    todoist.set_reminder(4672920807, "20:00")


def test_get_activity_logs():
    todoist = Todoist()
    activity = todoist.api.activity.get(parent_project_id=2261029492)
    print(activity)



post_tasks_test()
#get_tasks_test()
#post_reminder_test()
#update_home()
#test_set_reminder2()
#test_get_activity_logs()