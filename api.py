import urllib.request
import flask
from flask import request

import parselist
import requests
import yaml
import config
from apscheduler.schedulers.background import BackgroundScheduler

app = flask.Flask(__name__)
# app.config["DEBUG"] = True
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True

# Init sentry
#sentry_sdk.init(
#    dsn="https://ba10567a81304d18a0f2304269d3ae23@o456896.ingest.sentry.io/5454934",
#    integrations=[FlaskIntegration()],
#    traces_sample_rate=1.0
#)

# All Packages:
# /v1/<host>/packages
#
# All Packages in category:
# /v1/<host>/packages/category/<category>
#
# Specific Package:
# /v1/<host>/package/<name>
#
# Hosts:
# /v1/hosts


# Get host list
def get_hosts():
    global parsed_hosts
    hosts_file = requests.get("https://raw.githubusercontent.com/dhtdht020/oscdl-updateserver/master/v1/announcement"
                                     "/repositories.yml").text
    parsed_hosts = yaml.load(hosts_file, Loader=yaml.FullLoader)
    print("Loaded hosts list")


get_hosts()


# Schedule hosts list for refresh once per 30 minutes
scheduler = BackgroundScheduler()
scheduler.add_job(func=get_hosts, trigger="interval", minutes=30)
scheduler.start()


def get_hostname(host):
    if host == "codemii":
        return "hbb2.oscwii.org"
    else:
        return parsed_hosts["repositories"][host]["host"]


def url(host):
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)

    try:
        test_list_url = f"https://{get_hostname(host)}/hbb/homebrew_browser/listv036.txt"
        return test_list_url
    except KeyError:
        test_list_url = f"https://hbb1.oscwii.org/hbb/homebrew_browser/listv036.txt"
        return test_list_url

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>Error 404: Opened the shop but there were no apps." \
           "</h1><p>That doesn't look like our API. Did you follow the documentation?</p>", 404


@app.route('/', methods=['GET'])
def home():
    return "<h1>Open Shop Channel API</h1><p>Welcome to the OSC API Public Beta!\n" \
           "For documentation, go to our docs. api-docs.oscwii.org</p>"


# Version 2 (Current)
@app.route('/v2/<host>/packages', methods=['GET'], strict_slashes=False)
def v2_packages(host):
    test_list_url = url(host)

    query = request.args.get("query")
    coder = request.args.get("coder")
    category = request.args.get("category")
    package = request.args.get("package")


    f, headers = urllib.request.urlretrieve(test_list_url)
    l = parselist.convert_list_file_to_json(f, get_hostname(host))
    parser = parselist.hbbjsonparser()
    parser.load_json(l)

    # Query
    if query and coder and category:
        return flask.jsonify(parser.query_packages_category_coder(query, coder, category))

    if query and coder:
        return flask.jsonify(parser.query_packages_coder(query, coder))

    if query and category:
        return flask.jsonify(parser.query_packages_category(query, category))

    if query:
        return flask.jsonify(parser.query_packages(query))

    # Coder
    if coder and category:
        return flask.jsonify(parser.get_developer_category(category, coder))

    if coder:
        return flask.jsonify(parser.get_developer(coder))

    # Basic
    if category:
        return flask.jsonify(parser.get_category(category))

    if package:
        return flask.jsonify(parser.dictionary(package))

    return flask.jsonify(l)


@app.route('/v2/hosts', methods=['GET'], strict_slashes=False)
def v2_api_hosts():
    return flask.jsonify(parsed_hosts)


# Version 1 (For backwards compatiblity, do not change!)
@app.route('/v1', methods=['GET'])
def v1():
    return "<h1>Open Shop Channel API</h1><p>Oh boy, version 1.\n" \
           "For documentation, go to our docs. api-docs.oscwii.org</p>"


@app.route('/v1/hosts', methods=['GET'], strict_slashes=False)
def api_hosts():
    return flask.jsonify(parsed_hosts)


@app.route('/v1/<host>/packages', methods=['GET'], strict_slashes=False)
def all_packages(host):
    test_list_url = url(host)

    f, headers = urllib.request.urlretrieve(test_list_url)
    l = parselist.convert_list_file_to_json(f, get_hostname(host))
    parser = parselist.hbbjsonparser()
    parser.load_json(l)
    return flask.jsonify(l)


@app.route('/v1/<host>/package/<app_name>', methods=['GET'], strict_slashes=False)
def one_package(host, app_name):
    test_list_url = url(host)

    f, headers = urllib.request.urlretrieve(test_list_url)
    l = parselist.convert_list_file_to_json(f, get_hostname(host))
    parser = parselist.hbbjsonparser()
    parser.load_json(l)
    return flask.jsonify(parser.dictionary(app_name))


@app.route('/v1/<host>/category/<category>/packages', methods=['GET'], strict_slashes=False)
def category_packages(host, category):
    test_list_url = url(host)

    f, headers = urllib.request.urlretrieve(test_list_url)
    l = parselist.convert_list_file_to_json(f, get_hostname(host))
    parser = parselist.hbbjsonparser()
    parser.load_json(l)
    return flask.jsonify(parser.get_category(category))


@app.route('/v1/<host>/coder/<coder>/packages', methods=['GET'], strict_slashes=False)
def coder_packages(host, coder):
    test_list_url = url(host)

    f, headers = urllib.request.urlretrieve(test_list_url)
    l = parselist.convert_list_file_to_json(f, get_hostname(host))
    parser = parselist.hbbjsonparser()
    parser.load_json(l)
    return flask.jsonify(parser.get_developer(coder))


@app.route('/v1/<host>/category/<category>/coder/<coder>/packages', methods=['GET'], strict_slashes=False)
def coder_packages_categories(host, category, coder):
    test_list_url = url(host)

    f, headers = urllib.request.urlretrieve(test_list_url)
    l = parselist.convert_list_file_to_json(f, get_hostname(host))
    parser = parselist.hbbjsonparser()
    parser.load_json(l)
    return flask.jsonify(parser.get_developer_category(category, coder))


app.run(port=config.port)
