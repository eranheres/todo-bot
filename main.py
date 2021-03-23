from todobot.slack_listener import start_listen
from flask import escape, Flask
from todobot.slack_listener import handler
from todobot.slack_listener import flask_app
from todobot.slack_listener import todoist_event
print(__name__)


def todobot(request):
    if 'todoist' in request.full_path:
        return todoist_event()
    else:
        return handler.handle(request)


if __name__ == '__main__':
    app = Flask(__name__)
    app.route('/hello', endpoint=todobot, methods=['GET'],)
    app.run(port=3000, debug=True)
