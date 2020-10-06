import urllib.request
import flask
import parselist
import requests
import yaml
from apscheduler.schedulers.background import BackgroundScheduler

app = flask.Flask(__name__)
# app.config["DEBUG"] = True
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True


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
    l = parselist.convert_list_file_to_json(f)
    parser = parselist.hbbjsonparser()
    parser.load_json(l)
    return flask.jsonify(l)


@app.route('/v1/<host>/package/<app_name>', methods=['GET'], strict_slashes=False)
def one_package(host, app_name):
    test_list_url = url(host)

    f, headers = urllib.request.urlretrieve(test_list_url)
    l = parselist.convert_list_file_to_json(f)
    parser = parselist.hbbjsonparser()
    parser.load_json(l)
    return flask.jsonify(parser.dictionary(app_name))


@app.route('/v1/<host>/category/<category>/packages', methods=['GET'], strict_slashes=False)
def category_packages(host, category):
    test_list_url = url(host)

    f, headers = urllib.request.urlretrieve(test_list_url)
    l = parselist.convert_list_file_to_json(f)
    parser = parselist.hbbjsonparser()
    parser.load_json(l)
    return flask.jsonify(parser.get_category(category))


app.run(port=80)
