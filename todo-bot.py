from todoist_proxy import Todoist
from slack_post import SlackPost


tasks = Todoist.get_tasks()
slack_post = SlackPost()
slack_post.post_task_list_at_home(tasks)