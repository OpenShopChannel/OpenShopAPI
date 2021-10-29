from flask import Blueprint, send_from_directory

v3 = Blueprint("v3", "v3")


@v3.route('/hosts', methods=['GET'], strict_slashes=False)
def hosts():
    return send_from_directory('', 'repos.json')


@v3.route('/', methods=['GET'], strict_slashes=False)
def landing():
    return "Open Shop Channel API v3 is currently not finalized, work in progress, and should not be used. " \
           "Please use the officially documented v2 API instead. https://docs.oscwii.org/api<br><br>" \
           "Endpoints:<br>" \
           "\"/hosts\" - Experimental incompatible changes to the former hosts endpoint."
