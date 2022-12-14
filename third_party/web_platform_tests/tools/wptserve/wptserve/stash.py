import base64
import json
import os
import six
import uuid
from multiprocessing.managers import BaseManager, DictProxy

if six.PY2:
    base64.encodebytes = base64.encodestring
    base64.decodebytes = base64.decodestring

class ServerDictManager(BaseManager):
    shared_data = {}

def _get_shared():
    return ServerDictManager.shared_data

ServerDictManager.register("get_dict",
                           callable=_get_shared,
                           proxytype=DictProxy)

class ClientDictManager(BaseManager):
    pass

ClientDictManager.register("get_dict")

class StashServer(object):
    def __init__(self, address=None, authkey=None):
        self.address = address
        self.authkey = authkey
        self.manager = None

    def __enter__(self):
        self.manager, self.address, self.authkey = start_server(self.address, self.authkey)
        store_env_config(self.address, self.authkey)

    def __exit__(self, *args, **kwargs):
        if self.manager is not None:
            self.manager.shutdown()

def load_env_config():
    address, authkey = json.loads(os.environ["WPT_STASH_CONFIG"])
    if isinstance(address, list):
        address = tuple(address)
    else:
        address = str(address)
    authkey = base64.decodebytes(authkey.encode())
    return address, authkey

def store_env_config(address, authkey):
    authkey = base64.encodebytes(authkey)
    if isinstance(address, bytes):
        address = address.decode()
    os.environ["WPT_STASH_CONFIG"] = json.dumps((address, authkey.decode("ascii")))

def start_server(address=None, authkey=None):
    manager = ServerDictManager(address, authkey.encode())
    manager.start()

    return (manager, manager._address, manager._authkey)


#TODO: Consider expiring values after some fixed time for long-running
#servers

class Stash(object):
    """Key-value store for persisting data across HTTP/S and WS/S requests.

    This data store is specifically designed for persisting data across server
    requests. The synchronization is achieved by using the BaseManager from
    the multiprocessing module so different processes can acccess the same data.

    Stash can be used interchangeably between HTTP, HTTPS, WS and WSS servers.
    A thing to note about WS/S servers is that they require additional steps in
    the handlers for accessing the same underlying shared data in the Stash.
    This can usually be achieved by using load_env_config(). When using Stash
    interchangeably between HTTP/S and WS/S request, the path part of the key
    should be expliclitly specified if accessing the same key/value subset.

    The store has several unusual properties. Keys are of the form (path,
    uuid), where path is, by default, the path in the HTTP request and
    uuid is a unique id. In addition, the store is write-once, read-once,
    i.e. the value associated with a particular key cannot be changed once
    written and the read operation (called "take") is destructive. Taken together,
    these properties make it difficult for data to accidentally leak
    between different resources or different requests for the same
    resource.
    """

    _proxy = None

    def __init__(self, default_path, address=None, authkey=None):
        self.default_path = default_path
        self.data = self._get_proxy(address, authkey)

    def _get_proxy(self, address=None, authkey=None):
        if address is None and authkey is None:
            Stash._proxy = {}

        if Stash._proxy is None:
            manager = ClientDictManager(address, authkey)
            manager.connect()
            Stash._proxy = manager.get_dict()

        return Stash._proxy

    def _wrap_key(self, key, path):
        if path is None:
            path = self.default_path
        # This key format is required to support using the path. Since the data
        # passed into the stash can be a DictProxy which wouldn't detect changes
        # when writing to a subdict.
        return (str(path), str(uuid.UUID(key)))

    def put(self, key, value, path=None):
        """Place a value in the shared stash.

        :param key: A UUID to use as the data's key.
        :param value: The data to store. This can be any python object.
        :param path: The path that has access to read the data (by default
                     the current request path)"""
        if value is None:
            raise ValueError("SharedStash value may not be set to None")
        internal_key = self._wrap_key(key, path)
        if internal_key in self.data:
            raise StashError("Tried to overwrite existing shared stash value "
                             "for key %s (old value was %s, new value is %s)" %
                             (internal_key, self.data[str(internal_key)], value))
        else:
            self.data[internal_key] = value

    def take(self, key, path=None):
        """Remove a value from the shared stash and return it.

        :param key: A UUID to use as the data's key.
        :param path: The path that has access to read the data (by default
                     the current request path)"""
        internal_key = self._wrap_key(key, path)
        value = self.data.get(internal_key, None)
        if value is not None:
            try:
                self.data.pop(internal_key)
            except KeyError:
                # Silently continue when pop error occurs.
                pass

        return value

class StashError(Exception):
    pass
