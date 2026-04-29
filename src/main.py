import os
from flask import Flask, render_template, send_from_directory, abort, redirect, url_for
from dotenv import load_dotenv
from datetime import datetime, timezone

from source_espn import espn_get
from source_yahoo import yahoo_get
from source_cbs import cbs_get
from source_fantrax import fantrax_get
from config_source_keys import source_keys

load_dotenv(override=True)

nocodb_url = os.getenv('NOCODB_URL', 'http://localhost:8080')
dashboard_url = nocodb_url + '/dashboard/#/nc/view/' + os.getenv('NOCODB_PUBLIC_ID')

nocodb_base_id = os.getenv('NOCODB_BASE_ID')
nocodb_table_id = os.getenv('NOCODB_TABLE_ID')

if nocodb_base_id:
    dashboard_editor_url = f"{nocodb_url}/dashboard/#/nc/{nocodb_base_id}/{nocodb_table_id}"
else:
    dashboard_editor_url = nocodb_url

app = Flask(__name__, template_folder='../templates', static_folder='../static')


@app.route('/')
def home():
    return render_template(
        'pages/dashboard.html',
        source_keys=source_keys,
        dashboard_url=dashboard_url,
        dashboard_editor_url=dashboard_editor_url
    )


@app.route('/index')
def index():
    return render_template(
        'pages/index.html',
        source_keys=source_keys,
        dashboard_url=dashboard_url,
        dashboard_editor_url=dashboard_editor_url
    )


@app.route('/<source>')
def source_page(source):
    source_data = next(
        (s for s in source_keys if s['source'].lower() == source.lower()), None
    )
    if not source_data:
        abort(404)

    return render_template(
        'pages/sources.html',
        source=source_data['source'],
        trend_keys=source_data['trends'],
        dashboard_url=dashboard_url,
        dashboard_editor_url=dashboard_editor_url
    )


@app.route('/<source>/<int:func_id>')
def show_source_func(source, func_id):
    source_key = source.lower()
    source_data = next((s for s in source_keys if s['source'].lower() == source_key), None)
    if not source_data:
        abort(404)

    try:
        trend_type = source_data['trends'][func_id - 1]['key']
        handler = source + '_get'
        if not handler:
            abort(501, f"Data handler for source '{source}' is not implemented.")

        data = handler(trend_type)
        return data
    except IndexError:
        abort(404)


@app.route('/dashboard')
def dashboard_redirect():
    return redirect(url_for('home'))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


def get_file_version(filename):
    filepath = os.path.join(app.static_folder, filename)
    if os.path.exists(filepath):
        ts = os.path.getmtime(filepath)
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        return dt.strftime('%Y%m%d%H%M%S')
    else:
        return datetime.now(tz=timezone.utc).strftime('%Y%m%d%H%M%S')

@app.context_processor
def inject_version_cache():
    return {
        "version_cache": get_file_version("style-common.css"),
        "version_dark": get_file_version("style-dark.css"),
        "version_light": get_file_version("style-light.css"),
    }


# Tests with `pipenv run flask run` or `pipenv run python src/main.py` or `pipenv run flask shell`
if __name__ == '__main__':
    app.run(host=os.getenv('FLASK_RUN_HOST'), port=os.getenv('FLASK_RUN_PORT'), debug=os.getenv('FLASK_DEBUG'))
