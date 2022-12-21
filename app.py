import uuid
import os

from flask import Flask
from flask import request
from flask.views import MethodView
from flask import jsonify
from celery import Celery
from celery.result import AsyncResult

from upscale import example

app_name = 'app'
app = Flask(app_name)
app.config['UPLOAD_FOLDER'] = 'files'
celery = Celery(app_name, backend="redis://127.0.0.1:6379/1", broker="redis://127.0.0.1:6379/2")
celery.conf.update(app.config)

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextTask

@celery.task()
def match_photos(path_1, path_2):

    result = example(path_1, "lama_new.png")
    return result

class Comparison(MethodView):

    def get(self, task_id):
        task = AsyncResult(task_id, app=celery)
        return jsonify({"status": task.status, "result": task.result})

    def post(self):
        image_pathes = [self.save_image(field) for field in ("image_1")]
        task = match_photos.delay(*image_pathes)
        return jsonify({"task_id": task.id})

    def save_image(self, field):
        image = request.files.get(field)
        extension = image.filename.split('.')[-1]
        path = os.path.join('files', f'{uuid.uuid4()}.{extension}')
        image.save(path)
        return path

comparison_view = Comparison.as_view("comparison")
app.add_url_rule(
    "/comparison/<string:task_id>", view_func=comparison_view, methods=["GET"]
)
app.add_url_rule("/comparison/", view_func=comparison_view, methods=["POST"])

if __name__ == '__main__':
    app.run()