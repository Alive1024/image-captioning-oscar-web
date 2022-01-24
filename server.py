import os
import os.path as osp
import json
import random
from functools import partial
import logging
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from oscar.infer_on_single import prepare, infer


app = Flask(__name__)
app.config['SECRET_KEY'] = '12345'
upload_folder = './temp'
app.config['UPLOAD_FOLDER'] = upload_folder
if not osp.exists(upload_folder):
    os.mkdir(upload_folder)
BASE_DIR = os.environ.get('BASE_DIR', '')

ERROR_MSG = {
    'WrongFile': '上传的文件错误',
    'EmptyFile': '上传文件为空',
    'BackendException': '后台异常',
    'WrongFileType': '上传的数据格式不正确, 支持 .jpg, .jpeg, .png'
}

@app.route(f'{BASE_DIR}/v1/debug', methods=['GET'])
def debug():
    return '<p>' + '<br/>'.join(LOG_LIST) + '</p>'


@app.route(f'{BASE_DIR}/v1/index', methods=['GET', 'POST'])
def home():
    logger.info(f'{BASE_DIR}/v1/index {request.method}')

    if request.method == 'GET':
        return render_template('index.html', base_dir=BASE_DIR)
    elif request.method == 'POST':
        success, info = True, ''

        if 'image' not in request.files:
            success, info = False, ERROR_MSG['WrongFile']

        image_file = request.files['image']
        if image_file.filename == '':
            success, info = False, ERROR_MSG['EmptyFile']
        
        if image_file and is_allowed_file(image_file.filename):
            try:
                filename = generate_filename(image_file.filename)
                file_path = osp.join(app.config['UPLOAD_FOLDER'], filename)
                image_file.save(file_path)
                infer_result = infer_func(img_path=file_path)[0]
                success, info = True, infer_result
            except Exception:
                success, info = False, ERROR_MSG['BackendException']
        else:
            success, info = False, ERROR_MSG['WrongFileType']
        
        if success:
            logger.info(f'{file_path}: {info}')
        else:
            logger.error(info)

        return json.dumps({'success': success, 'info': info})


def is_allowed_file(filename):
    valid_extensions = ['.jpg', '.jpeg', '.png']
    return osp.splitext(filename)[1].lower() in valid_extensions


def generate_filename(filename):
    LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    ext = osp.split(filename)[1]
    random_indexes = [random.randint(0, len(LETTERS) - 1) for _ in range(10)]
    random_chars = "".join([LETTERS[index] for index in random_indexes])
    new_name = "{name}.{extension}".format(name=random_chars, extension=ext)
    return secure_filename(new_name)


@app.errorhandler(500)
def server_error(error_info):
    logger.error(f'Server ERROR: 500. {error_info}')
    return render_template("error.html", error_info=error_info), 500


class ListHandler(logging.Handler):
    def __init__(self, log_list, **kwargs) -> None:
        super().__init__(**kwargs)
        self.log_list = log_list
    
    def emit(self, record) -> None:
        self.log_list.append(self.format(record))


def setup_global_logger(log_list):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    list_handler = ListHandler(log_list)
    list_handler.setLevel(logging.DEBUG)
    list_handler.setFormatter(formatter)
    logger.addHandler(list_handler)

    return logger


class SimpleLogger:
    """
    Just for debugging, use with caution
    """
    def __init__(self, log_list):
        self.log_list = log_list
    
    def info(self, data):
        self.log_list.append(data)

    def error(self, data):
        self.log_list.append(data)


if __name__ == '__main__':
    LOG_LIST = []
    logger = setup_global_logger(LOG_LIST)

    logger.info('Preparing models...')
    try:
        predictor, vg_classes, args, model, tokenizer, tensorizer, inputs_param = \
            prepare(run_from_cmd=False, eval_model_dir='inference_models/Oscar')
    except ValueError as e:
        logger.error(f'ValueError while preparing models: {e.args}')
        server_error(e.args)

    infer_func = partial(infer, predictor=predictor, vg_classes=vg_classes, args=args,
                         model=model, tokenizer=tokenizer, tensorizer=tensorizer, inputs_param=inputs_param)
    logger.info('Models loaded. Ready to infer images.')
    logger.info(f'Launching the server...BASE_DIR: {BASE_DIR}')
    app.run('0.0.0.0')  # Code behind app.run() won't be executed!!! Thus, must load models before app.run()
