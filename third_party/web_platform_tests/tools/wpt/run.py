import argparse
import os
import platform
import shutil
import subprocess
import sys
import tarfile
from distutils.spawn import find_executable

wpt_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.insert(0, os.path.abspath(os.path.join(wpt_root, "tools")))

from . import browser, utils, virtualenv
logger = None


class WptrunError(Exception):
    pass


class WptrunnerHelpAction(argparse.Action):
    def __init__(self,
                 option_strings,
                 dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS,
                 help=None):
        super(WptrunnerHelpAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        from wptrunner import wptcommandline
        wptparser = wptcommandline.create_parser()
        wptparser.usage = parser.usage
        wptparser.print_help()
        parser.exit()


def create_parser():
    from wptrunner import wptcommandline

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("product", action="store",
                        help="Browser to run tests in")
    parser.add_argument("--yes", "-y", dest="prompt", action="store_false", default=True,
                        help="Don't prompt before installing components")
    parser.add_argument("--stability", action="store_true",
                        help="Stability check tests")
    parser.add_argument("--install-browser", action="store_true",
                        help="Install the latest development version of the browser")
    parser._add_container_actions(wptcommandline.create_parser())
    return parser


def exit(msg):
    logger.error(msg)
    sys.exit(1)


def args_general(kwargs):
    kwargs.set_if_none("tests_root", wpt_root)
    kwargs.set_if_none("metadata_root", wpt_root)
    kwargs.set_if_none("manifest_update", True)

    if kwargs["ssl_type"] == "openssl":
        if not find_executable(kwargs["openssl_binary"]):
            if os.uname()[0] == "Windows":
                raise WptrunError("""OpenSSL binary not found. If you need HTTPS tests, install OpenSSL from

https://slproweb.com/products/Win32OpenSSL.html

Ensuring that libraries are added to /bin and add the resulting bin directory to
your PATH.

Otherwise run with --ssl-type=none""")
            else:
                raise WptrunError("""OpenSSL not found. If you don't need HTTPS support run with --ssl-type=none,
otherwise install OpenSSL and ensure that it's on your $PATH.""")


def check_environ(product):
    if product not in ("firefox", "servo"):
        expected_hosts = ["web-platform.test",
                          "www.web-platform.test",
                          "www1.web-platform.test",
                          "www2.web-platform.test",
                          "xn--n8j6ds53lwwkrqhv28a.web-platform.test",
                          "xn--lve-6lad.web-platform.test",
                          "nonexistent-origin.web-platform.test"]
        missing_hosts = set(expected_hosts)
        if platform.uname()[0] != "Windows":
            hosts_path = "/etc/hosts"
        else:
            hosts_path = "C:\Windows\System32\drivers\etc\hosts"
        with open(hosts_path, "r") as f:
            for line in f:
                line = line.split("#", 1)[0].strip()
                parts = line.split()
                if len(parts) == 2:
                    host = parts[1]
                    missing_hosts.discard(host)
            if missing_hosts:
                raise WptrunError("""Missing hosts file configuration. Expected entries like:

%s

See README.md for more details.""" % "\n".join("%s\t%s" %
                                               ("127.0.0.1" if "nonexistent" not in host else "0.0.0.0", host)
                                               for host in expected_hosts))


class BrowserSetup(object):
    name = None
    browser_cls = None

    def __init__(self, venv, prompt=True, sub_product=None):
        self.browser = self.browser_cls()
        self.venv = venv
        self.prompt = prompt
        self.sub_product = sub_product

    def prompt_install(self, component):
        if not self.prompt:
            return True
        while True:
            resp = raw_input("Download and install %s [Y/n]? " % component).strip().lower()
            if not resp or resp == "y":
                return True
            elif resp == "n":
                return False

    def install(self, venv):
        if self.prompt_install(self.name):
            return self.browser.install(venv.path)

    def setup(self, kwargs):
        self.venv.install_requirements(os.path.join(wpt_root, "tools", "wptrunner", self.browser.requirements))
        self.setup_kwargs(kwargs)


class Firefox(BrowserSetup):
    name = "firefox"
    browser_cls = browser.Firefox

    def setup_kwargs(self, kwargs):
        if kwargs["binary"] is None:
            binary = self.browser.find_binary()
            if binary is None:
                raise WptrunError("""Firefox binary not found on $PATH.

Install Firefox or use --binary to set the binary path""")
            kwargs["binary"] = binary

        if kwargs["certutil_binary"] is None and kwargs["ssl_type"] != "none":
            certutil = self.browser.find_certutil()

            if certutil is None:
                # Can't download this for now because it's missing the libnss3 library
                raise WptrunError("""Can't find certutil.

This must be installed using your OS package manager or directly e.g.

Debian/Ubuntu:
    sudo apt install libnss3-tools

macOS/Homebrew:
    brew install nss

Others:
    Download the firefox archive and common.tests.zip archive for your platform
    from https://archive.mozilla.org/pub/firefox/nightly/latest-mozilla-central/

   Then extract certutil[.exe] from the tests.zip package and
   libnss3[.so|.dll|.dynlib] and but the former on your path and the latter on
   your library path.
""")
            else:
                print("Using certutil %s" % certutil)

            if certutil is not None:
                kwargs["certutil_binary"] = certutil
            else:
                print("Unable to find or install certutil, setting ssl-type to none")
                kwargs["ssl_type"] = "none"

        if kwargs["webdriver_binary"] is None and "wdspec" in kwargs["test_types"]:
            webdriver_binary = self.browser.find_webdriver()

            if webdriver_binary is None:
                install = self.prompt_install("geckodriver")

                if install:
                    print("Downloading geckodriver")
                    webdriver_binary = self.browser.install_webdriver(dest=self.venv.bin_path)
            else:
                print("Using webdriver binary %s" % webdriver_binary)

            if webdriver_binary:
                kwargs["webdriver_binary"] = webdriver_binary
            else:
                print("Unable to find or install geckodriver, skipping wdspec tests")
                kwargs["test_types"].remove("wdspec")

        if kwargs["prefs_root"] is None:
            print("Downloading gecko prefs")
            prefs_root = self.browser.install_prefs(self.venv.path)
            kwargs["prefs_root"] = prefs_root


class Chrome(BrowserSetup):
    name = "chrome"
    browser_cls = browser.Chrome

    def setup_kwargs(self, kwargs):
        if kwargs["webdriver_binary"] is None:
            webdriver_binary = self.browser.find_webdriver()

            if webdriver_binary is None:
                install = self.prompt_install("chromedriver")

                if install:
                    print("Downloading chromedriver")
                    webdriver_binary = self.browser.install_webdriver(dest=self.venv.bin_path)
            else:
                print("Using webdriver binary %s" % webdriver_binary)

            if webdriver_binary:
                kwargs["webdriver_binary"] = webdriver_binary
            else:
                raise WptrunError("Unable to locate or install chromedriver binary")


class Edge(BrowserSetup):
    name = "edge"
    browser_cls = browser.Edge

    def install(self, venv):
        raise NotImplementedError

    def setup_kwargs(self, kwargs):
        if kwargs["webdriver_binary"] is None:
            webdriver_binary = self.browser.find_webdriver()

            if webdriver_binary is None:
                raise WptrunError("""Unable to find WebDriver and we aren't yet clever enough to work out which
version to download. Please go to the following URL and install the correct
version for your Edge/Windows release somewhere on the %PATH%:

https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
""")
            kwargs["webdriver_binary"] = webdriver_binary


class Sauce(BrowserSetup):
    name = "sauce"
    browser_cls = browser.Sauce

    def install(self, venv):
        raise NotImplementedError

    def setup_kwargs(self, kwargs):
        kwargs.set_if_none("sauce_browser", self.sub_product[0])
        kwargs.set_if_none("sauce_version", self.sub_product[1])
        kwargs["test_types"] = ["testharness", "reftest"]


class Servo(BrowserSetup):
    name = "servo"
    browser_cls = browser.Servo

    def install(self, venv):
        raise NotImplementedError

    def setup_kwargs(self, kwargs):
        if kwargs["binary"] is None:
            binary = self.browser.find_binary()

            if binary is None:
                raise WptrunError("Unable to find servo binary on the PATH")
            kwargs["binary"] = binary


product_setup = {
    "firefox": Firefox,
    "chrome": Chrome,
    "edge": Edge,
    "servo": Servo,
    "sauce": Sauce,
}


def setup_wptrunner(venv, prompt=True, install=False, **kwargs):
    from wptrunner import wptrunner, wptcommandline

    global logger

    kwargs = utils.Kwargs(kwargs.items())

    product_parts = kwargs["product"].split(":")
    kwargs["product"] = product_parts[0]
    sub_product = product_parts[1:]

    wptrunner.setup_logging(kwargs, {"mach": sys.stdout})
    logger = wptrunner.logger

    check_environ(kwargs["product"])
    args_general(kwargs)

    if kwargs["product"] not in product_setup:
        raise WptrunError("Unsupported product %s" % kwargs["product"])

    setup_cls = product_setup[kwargs["product"]](venv, prompt, sub_product)

    if install:
        logger.info("Installing browser")
        kwargs["binary"] = setup_cls.install(venv)

    setup_cls.setup(kwargs)

    wptcommandline.check_args(kwargs)

    wptrunner_path = os.path.join(wpt_root, "tools", "wptrunner")

    venv.install_requirements(os.path.join(wptrunner_path, "requirements.txt"))

    return kwargs


def run(venv, **kwargs):
    #Remove arguments that aren't passed to wptrunner
    prompt = kwargs.pop("prompt", True)
    stability = kwargs.pop("stability", True)
    install_browser = kwargs.pop("install_browser", False)

    kwargs = setup_wptrunner(venv,
                             prompt=prompt,
                             install=install_browser,
                             **kwargs)

    if stability:
        import stability
        iterations, results, inconsistent = stability.run(venv, logger, **kwargs)

        def log(x):
            print(x)

        if inconsistent:
            stability.write_inconsistent(log, inconsistent, iterations)
        else:
            log("All tests stable")
        rv = len(inconsistent) > 0
    else:
        rv = run_single(venv, **kwargs) > 0

    return rv


def run_single(venv, **kwargs):
    from wptrunner import wptrunner
    return wptrunner.start(**kwargs)


def main():
    try:
        parser = create_parser()
        args = parser.parse_args()

        venv = virtualenv.Virtualenv(os.path.join(wpt_root, "_venv_%s") % platform.uname()[0])
        venv.start()
        venv.install_requirements(os.path.join(wpt_root, "tools", "wptrunner", "requirements.txt"))
        venv.install("requests")

        return run(venv, vars(args))
    except WptrunError as e:
        exit(e.message)


if __name__ == "__main__":
    import pdb
    from tools import localpaths
    try:
        main()
    except:
        pdb.post_mortem()
