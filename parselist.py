# LyfeOnEdge 2020
# Written for Open Shop Channel Project

import io, json
import metadata

# load metadata json
metadata = metadata.Metadata()
metadata.load()


# python object to parse converted hbb list file
class hbbjsonparser(object):
    def __init__(self):
        self.init()

    def init(self):
        self.all = []
        self.demos = []
        self.emulators = []
        self.games = []
        self.media = []
        self.utilities = []

        self.map = {
            "demos": self.demos,
            "emulators": self.emulators,
            "games": self.games,
            "media": self.media,
            "utilities": self.utilities,
        }

        self.list_list = [self.all, self.demos, self.emulators, self.games, self.media, self.utilities]

    def clear(self):
        self.init()

    # Loads appstore json as a large list of dicts
    def load_json(self, repo_json):
        if not repo_json:
            raise
        self.clear()
        self.all = repo_json
        self.sort()
        num_entries = len(self.all)
        print(f"Loaded {num_entries} packages")

    def get_package_dict(self, packagename: str):
        for package in self.all:
            if package["internal_name"] == packagename:
                return package

    def get_category(self, category):
        packages = []
        for package in self.all:
            if package["category"] == category:
                packages.append(package)

        return packages

    def get_developer(self, coder):
        packages = []
        for package in self.all:
            if package["coder"] == coder:
                packages.append(package)

        return packages

    def get_developer_category(self, category, coder):
        packages = []
        for package in self.all:
            if package["coder"] == coder:
                if package["category"] == category:
                    packages.append(package)

        return packages

    def query_packages(self, query):
        packages = []
        for package in self.all:
            if query in package["internal_name"]:
                packages.append(package)

        return packages

    def query_packages_category(self, query, category):
        packages = []
        for package in self.all:
            if query in package["internal_name"]:
                if package["category"] == category:
                    packages.append(package)

        return packages

    def query_packages_coder(self, query, coder):
        packages = []
        for package in self.all:
            if query in package["internal_name"]:
                if package["coder"] == coder:
                    packages.append(package)

        return packages

    def query_packages_category_coder(self, query, category, coder):
        packages = []
        for package in self.all:
            if query in package["internal_name"]:
                if package["coder"] == coder:
                    if package["category"] == category:
                        packages.append(package)

        return packages

    # sorts list into smaller chunks
    def sort(self):
        if self.all:
            for entry in self.all:
                try:
                    self.map[entry["category"]].append(entry)
                except:
                    pkg = entry["internal_name"]
                    print(f"Error sorting {pkg}")
        else:
            raise

    def list(self):
        packages = []
        for p in self.all:
            packages.append(p["internal_name"])
        return packages

    def dictionary(self, app_name):
        return self.get_package_dict(app_name)


def convert_list_file_to_json(list_file, hostname):
    with open(list_file) as f:
        contents = io.StringIO(f.read())
    return convert_list_to_json(contents, hostname)


def convert_list_to_json(hbblist, hostname):
    def repo_entry():
        entry = {
            "internal_name": "",  # String
            "display_name": "",  # String
            "coder": "",  # String
            "version": "",  # String
            "short_description": "",  # String
            "long_description": "",  # String
            "release_date": "",  # String
            "contributors": "",  # String
            "updated": "",  # timestamp int
            "category": "",  # String
            "package_type": "",
            "extracted": 0,  # Extracted size, int
            "zip_size": 0,  # Zip size, int
            "downloads": 0,  # dl's, int
            "controllers": "",
            "rating": "",
            "zip_url" : "",
            "icon_url": "",
            "extra_directories": "",
            "shop_title_id": "",
            "shop_title_version": 1,
        }
        return entry

    # First line is header, 'Homebrew' expected as first item
    header = hbblist.readline().split()

    if not header[0] == "Homebrew":
        raise valueError("Invalid Repo File")

    # Not documented, small int
    unknown = header[1]

    repo_version = header[2]
    if len(header) > 3:
        changenotes = header[2:]
    else:
        changenotes = []

    # Category changes as we cycle through homebrew
    TRANSITIONS = {
        "=Demos=": "emulators",
        "=Emulators=": "games",
        "=Games=": "media",
        "=Media=": "utilities",
        "=Utilities=": None,
    }
    current_category = "demos"

    packages = []
    while True:
        line = hbblist.readline()
        if line.strip().strip("\\n") in TRANSITIONS:  # Check if the line is a footer line
            current_category = TRANSITIONS[line.strip().strip("\\n")]  # If so, update category
            if not current_category:  # Stop if there are no more categories to read
                break
            continue  # Skip processing line if it's a transition

        line = line.split()
        name = line[0]
        updated = int(line[1])
        unknown = line[2]
        boot_file_size = line[3]
        package_type = line[4]
        folder_size = line[5]
        downloads = line[6]
        rating = line[7]
        controllers = line[8]
        # extra_directories = line[9].replace(";", " ").split()
        display_name = hbblist.readline().strip().strip("\\\n")
        author = hbblist.readline().strip().strip("\\\n")
        version = hbblist.readline().strip().strip("\\\n")
        extracted = hbblist.readline().strip().strip("\\\n")
        description = hbblist.readline().strip().strip("\\\n")
        details = hbblist.readline().strip().strip("\\\n")
        zip_url = f"https://{hostname}/hbb/{name}/{name}.zip"
        icon_url = f"https://{hostname}/hbb/{name}.png"
        extra_directories = line[9].replace(";", " ").split()
        shop_title_id = metadata.title_id_by_name(name)
        shop_title_version = metadata.title_version_by_name(name)

        # Clear list if the are no extra directories
        if extra_directories == ['.']:
            extra_directories = []

        entry = repo_entry()
        entry["internal_name"] = name
        entry["display_name"] = display_name
        entry["coder"] = author
        entry["version"] = version
        entry["short_description"] = description
        entry["long_description"] = details
        entry["release_date"] = updated
        entry["category"] = current_category
        entry["package_type"] = package_type
        entry["extracted"] = int(extracted)
        entry["updated"] = updated  # str(date.strftime(updated, "%m/%d/%Y"))
        entry["zip_size"] = int(folder_size)
        entry["downloads"] = int(downloads)
        entry["controllers"] = controllers
        entry["zip_url"] = zip_url
        entry["icon_url"] = icon_url
        entry["extra_directories"] = extra_directories
        entry["shop_title_id"] = shop_title_id
        entry["shop_title_version"] = shop_title_version

        # Collect all generated libget-style repo entries from the list
        packages.append(entry)

    return packages


if __name__ == "__main__":
    import urllib.request

    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)

    test_list_url = "https://hbb1.oscwii.org/hbb/homebrew_browser/listv036.txt"

    f, headers = urllib.request.urlretrieve(test_list_url)
    l = convert_list_file_to_json(f)
    parser = hbbjsonparser()
    parser.load_json(l)
