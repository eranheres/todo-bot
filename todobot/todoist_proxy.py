from todobot.tokens import get_tokens
from todoist.api import TodoistAPI
from datetime import datetime


class Todoist:
    api: TodoistAPI
    token: str

    def __init__(self):
        self.token = get_tokens()['TODOIST']
        self.api = TodoistAPI(self.token)
        self.api.sync()

    def sync(self):
        self.api.sync()

    def get_tasks(self):

        def today_and_overdue_filter(task):
            data = task.data
            today_date = datetime.today().strftime("%Y-%m-%d")
            if data['checked'] and (data['date_completed'][:10] == today_date):
                return True
            if not data['due']:
                return False
            task_date = data['due']['date'][:10]
            if task_date == today_date:
                return True
            if task_date < today_date and data['checked'] == 0:
                return True
            return False

        def task_in_reminders(task, reminders, closed):
            for close in closed:
                if close['item']['id'] == task['id']:
                    return False
            for reminder in reminders:
                if task.data['id'] == reminder['item_id']:
                    return True
            return False
        today_and_overdue = self.api.items.all(filt=today_and_overdue_filter)
        reminders = self.api.reminders.all()
        # pending = [self.api.items.get(task['id']) for task in today_and_overdue if not task['completed']]
        closed = [self.api.items.get(task['id']) for task in today_and_overdue if task['checked']]
        open = [self.api.items.get(task['id']) for task in today_and_overdue
                    if not task['checked'] and not task_in_reminders(task, reminders, closed)]
        with_reminders = [self.api.items.get(task['id']) for task in today_and_overdue
                                if task_in_reminders(task, reminders, closed)]
        return open, closed, with_reminders

    def delete_task(self, task_id):
        self.api.items.delete(task_id)
        self.api.commit()
        print('deleted task {}'.format(task_id))

    def delay_task(self, task_id):
        task = self.task_by_id(task_id)
        if 'due' in task['item'] and task['item']['due'] and task['item']['due']['is_recurring']:
            print('cant delay recuring tasks {}'.format(task_id))
            return
        item = self.api.items.get_by_id(int(task_id))
        item.update(due={"string":  "tomorrow"})
        self.api.commit()
        print('completed updated {}'.format(task_id))


    def mark_task_complete(self, task_id):
        task = self.task_by_id(task_id)
        if 'due' in task['item'] and task['item']['due'] and task['item']['due']['is_recurring']:
            item = self.api.items.get_by_id(int(task_id))
            item.close()
        else:
            self.api.items.complete(task_id)
        self.api.commit()
        print('completed task {}'.format(task_id))

    def set_reminder(self, task_id, time):
        now = datetime.now()
        due_date = now.strftime('%Y-%m-%dT') + time + ":00"
        due_string = now.strftime('%d %b %H:%M')
        due = {'date': due_date,
             'is_recurring': False,
             'lang': 'en',
             'string': due_string,
             'timezone': None}

        #PrettyPrinter(indent=3).pprint(due)

        self.api.reminders.add(task_id, due=due, notify_uid=32981441, service='default', type='absolute')
        self.api.commit()
        print('updated reminder for {} to {}'.format(task_id, time))

    def task_by_id(self, task_id):
        return self.api.items.get(task_id)

    def task_name(self, task_id):
        return self.task_by_id(task_id)['item']['content']

    def task_url(self, task_id):
        return "https://todoist.com/app/project/2260616609/task/{}".format(task_id)