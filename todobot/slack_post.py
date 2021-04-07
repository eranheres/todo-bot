from slack_bolt import App
from todobot.tokens import get_tokens
from datetime import datetime


class SlackPost:
    app: App

    def __init__(self):
        # Initializes your app with your bot token and signing secret
        envs = get_tokens()
        self.app = App(
            token=envs.get("SLACK_BOT_TOKEN"),
            signing_secret=envs.get("SLACK_SIGNING_SECRET")
        )

    @staticmethod
    def divider_block():
        return [{"type": "divider"}]

    @staticmethod
    def item_url(item):
        return "https://todoist.com/app/project/2260616609/task/{}".format(item['id'])

    @staticmethod
    def text_block(text):
        return [{
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text
                    }
                }]

    @staticmethod
    def task_button_block(task):
        item=task['item']
        blocks = [{
                "type": "actions",
                "block_id": str(item['id']),
                "elements": [],
            }
            ]
        blocks[0]["elements"].append(
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Done :smile:",
                                    "emoji": True,
                                },
                                "style": "primary",
                                "value": str(item['id']),
                                "action_id": "done-action-button"
                            })
        if not('due' in task['item'] and 'is_recurring' in task['item']['due'] and task['item']['due']['is_recurring']):
            blocks[0]["elements"].append(
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Delay :expressionless:",
                                        "emoji": True,
                                    },
                                    "style": "danger",
                                    "value": str(item['id']),
                                    "action_id": "delay-action-button"
                                })
        blocks[0]["elements"].append(
                            {
                                "type": "timepicker",
                                "initial_time": datetime.now().strftime("%H:%M"),
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "snooze"
                                },
                                "action_id": "snooze-action-button"
                            })

        if not('due' in task['item'] and 'is_recurring' in task['item']['due'] and task['item']['due']['is_recurring']):
            blocks[0]["elements"].append(
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Delete :disappointed:",
                                        "emoji": True
                                    },
                                    "value": str(item['id']),
                                    "action_id": "delete-action-button",
                                    "style": "danger",
                                    "confirm": {
                                        "text": {
                                            "type": "mrkdwn",
                                            "text": "Are you sure :worried: ?"
                                        }
                                    }
                                })
        return blocks


    @staticmethod
    def task_text_block(task):
        item = task['item']
        if 'due' in item and 'datetime' in item['due']:
            time = item['due']['datetime']
        else:
            time = ""
        recuring_emoji = ''
        if 'due' in task['item'] and 'is_recurring' in task['item']['due'] and task['item']['due']['is_recurring']:
            recuring_emoji = ':arrows_counterclockwise:'

        text = ":white_check_mark:  *{}*  {} {}\n".format(
                            item['content'],
                            time,
                            recuring_emoji)
        return [{
            "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": text
                    }
                 }]

    @staticmethod
    def task_reminder_text_block(task):
        item = task['item']
        if 'due' in item and 'datetime' in item['due']:
            time = item['due']['datetime']
        else:
            time = ""
        text = "*{}* {}\n".format(
            item['content'],
            time)
        return [
            { "type": "divider"},
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": ":alarm_clock: Reminder :alarm_clock:"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text
            },
         },
        ]


    @staticmethod
    def task_to_block(task):
        blocks = []
        blocks.extend(SlackPost.task_text_block(task))
        blocks.extend(SlackPost.task_button_block(task))
        return blocks

    @staticmethod
    def completed_text_block(task):
        blocks = []
        item = task['item']
        txt = ":collision:~*{}*~".format(item['content'])
        blocks.extend(SlackPost.text_block(txt))
        return blocks

    @staticmethod
    def with_reminder_text_block(task):
        blocks = []
        item = task['item']
        txt = ":alarm_clock: *<{}|{}>*".format(
            SlackPost.item_url(item),
            item['content'])
        blocks.extend(SlackPost.text_block(txt))
        return blocks

    @staticmethod
    def home_blocks(task_list, completed_task_list, with_reminders):
        blocks = []
        # Open
        blocks.extend(SlackPost.text_block("These are your tasks *for today*, Eran :smiley:"))
        blocks.extend(SlackPost.divider_block())
        for task in task_list:
            blocks.extend(SlackPost.task_to_block(task))
            blocks.extend(SlackPost.divider_block())
        blocks.extend(SlackPost.divider_block())
        # With reminders
        blocks.extend(SlackPost.text_block("Will remind you later"))
        blocks.extend(SlackPost.divider_block())
        for task in with_reminders:
            blocks.extend(SlackPost.with_reminder_text_block(task))
        # Completed
        blocks.extend(SlackPost.text_block("Completed"))
        blocks.extend(SlackPost.divider_block())
        for task in completed_task_list:
            blocks.extend(SlackPost.completed_text_block(task))

        return blocks

    @staticmethod
    def all_tasks_to_block(task_list):
        blocks = []
        for task in task_list:
            blocks.extend(SlackPost.task_to_block(task))
            blocks.extend(SlackPost.divider_block())
        return blocks

    @staticmethod
    def task_reminder_block(task):
        blocks = []
        blocks.extend(SlackPost.task_reminder_text_block(task))
        blocks.extend(SlackPost.task_button_block(task))
        return blocks

    def post_reminder(self, task):
        return self.post_message("reminder text", SlackPost.task_reminder_block(task))

    def post_home_blocks(self, blocks):
        return self.app.client.views_publish(
          user_id='U01RAF5JF29',
          text="",
          view={"type": "home", "callback_id": "home_view", "blocks": blocks}
        )

    def post_message(self, text, blocks=None):
        print("Posting a message {}".format(text))
        if blocks==None:
            blocks = [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": text
                        }
                    }
            ]
        #pprint.PrettyPrinter(indent=1,sort_dicts=False).pprint(blocks)
        return self.app.client.chat_postMessage(channel="D01RS7E53K3", text=text, blocks=blocks)

    def post_task_list_at_home(self, task_list, completed_task_list, with_reminders):
        blocks = SlackPost.home_blocks(task_list, completed_task_list, with_reminders)
        print("Posting task list to home")
        #pprint.PrettyPrinter(indent=4).pprint(blocks)
        return self.post_home_blocks(blocks)

    def post_task_to_chat(self, task):
        return self.post_message("", SlackPost.task_to_block(task))

    def post_all_task_to_chat(self, task):
        return self.post_message("", SlackPost.all_tasks_to_block(task))
