#
# -*- coding: utf-8 -*-
#
# This file is part of reclass (http://github.com/madduck/reclass)
#
# Copyright © 2007–14 martin f. krafft <madduck@madduck.net>
# Released under the terms of the Artistic Licence 2.0
#

from output import OutputLoader
from storage.loader import StorageBackendLoader
from storage.memcache_proxy import MemcacheProxy
from storage.aliases_proxy import AliasesProxy

def get_storage(storage_type, nodes_uri, classes_uri, **kwargs):
    storage_class = StorageBackendLoader(storage_type).load()
    aliases_proxy = AliasesProxy(storage_class(nodes_uri, classes_uri, **kwargs), nodes_uri)
    return MemcacheProxy(aliases_proxy)


def output(data, fmt, pretty_print=False):
    output_class = OutputLoader(fmt).load()
    outputter = output_class()
    return outputter.dump(data, pretty_print=pretty_print)
