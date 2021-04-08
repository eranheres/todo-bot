import os
from flask import Flask, request
# Use the package we installed
from todobot.todoist_proxy import Todoist
from todobot.slack_post import SlackPost
import yaml
from slack_bolt.adapter.flask import SlackRequestHandler

slack_post = SlackPost()
app = slack_post.app
handler = SlackRequestHandler(app)
todoist = Todoist()

def get_yaml():
    with open(r'./token.yml') as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        return yaml.load(file, Loader=yaml.FullLoader)


@app.action("done-action-button")
def done_action_response(ack, action, respond):
    print("Got action on done button")
    ack()
    todoist.mark_task_complete(action['value'])
    id = int(action['value'])
    slack_post.post_message(":+1: the task *{}* is now marked as completed :smile:".format(
        todoist.task_name(id),
    ))


@app.action("delay-action-button")
def delete_action_response(ack, action, respond):
    print("Got action on delay button")
    ack()
    todoist.delay_task(action['value'])
    id = int(action['value'])
    slack_post.post_message(":+1: the task *{}* is delayed for tomorrow".format(
        todoist.task_name(id),
    ))


@app.action("delete-action-button")
def delete_action_response(ack, action, respond):
    print("Got action on delete button")
    ack()
    todoist.mark_task_complete(action['value'])
    id = int(action['value'])
    slack_post.post_message(":+1: the task *{}* is now deleted :boom::boom:".format(
        todoist.task_name(id),
    ))


@app.action("snooze-action-button")
def snooze_action_response(ack, action, respond):
    print("Got action on snooze button")
    ack()
    selected_time = action['selected_time']
    task_id = int(action['block_id'])
    todoist.set_reminder(task_id, selected_time)
    refresh_home()
    slack_post.post_message(":+1: reminder for *{}* was set to {}".format(
        todoist.task_name(task_id),
        selected_time))


def refresh_home():
    print("refreshing home")
    pending, completed, with_reminders = todoist.get_tasks()
    slack_post.post_task_list_at_home(pending, completed, with_reminders)

@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    print("got message home tab was opened")
    try:
        #refresh_home()
        pass
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


@app.event("message")
def update_home_tab(body, say, logger):
    print("got message to update home tab")
    try:
        user = body["event"]["user"]
        # single logger call
        # global logger is passed to listener
        logger.debug(body)
        #say(f"{user} mentioned your app")
        slack_post.post_all_task_to_chat(todoist.get_tasks())

    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


flask_app = Flask(__name__)
print("dd {}".format(__name__))
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    # handler runs App's dispatch method
    return handler.handle(request)


@flask_app.route("/todoist", methods=["POST"])
def todoist_event():
    # handler runs App's dispatch method
    data = request.json
    print("got todoist event: {}".format(data['event_name']))
    if data['event_name']=="reminder:fired":
        reminder = data['event_data']
        task = todoist.task_by_id(reminder['item_id'])
        slack_post.post_reminder(task=task)
    todoist.sync()
    refresh_home()
    return "ok"


def start_listen():
    flask_app.run(port=3000)


if __name__ == '__main__':
    start_listen()
