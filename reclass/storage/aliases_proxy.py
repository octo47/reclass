#
# -*- coding: utf-8 -*-
#
# This file is part of reclass (http://github.com/madduck/reclass)
#
# Copyright © 2007–14 martin f. krafft <madduck@madduck.net>
# Released under the terms of the Artistic Licence 2.0
#
import os
import sys

from reclass.storage import NodeStorageBase

STORAGE_NAME = 'alias_proxy'

def vvv(msg):
    #print >>sys.stderr, msg
    pass

class AliasesProxy(NodeStorageBase):

    def __init__(self, real_storage, node_storage_uri, suffix=".aliases"):
        name = '{0}({1})'.format(STORAGE_NAME, real_storage.name)
        super(AliasesProxy, self).__init__(name)
        self._real_storage = real_storage
        self._suffix = suffix
        self._mapping = self._find_aliases(node_storage_uri)

    name = property(lambda self: self._real_storage.name)

    def get_node(self, name, merge_base=None):
        return self._lookup_node(name, self._real_storage.get_node)

    def get_class(self, name):
        return self._real_storage.get_class(name)

    def enumerate_nodes(self):
        return self._mapping.keys() + self._real_storage.enumerate_nodes()

    def _find_aliases(self, node_storage_uri):
        mapping = {}
        for root, subFolders, files in os.walk(node_storage_uri):
            vvv("Lookup for aliases at %s" % root)
            for f in filter(lambda f: f.endswith(self._suffix), files):
                target_node = os.path.basename(os.path.splitext(f)[0])
                vvv("Reading %s for %s" % (f, target_node))
                with open(os.path.join(node_storage_uri, f), 'r') as fin:
                    for alias in fin:
                        alias = alias.rstrip()
                        vvv("%s=>%s" % (alias, target_node))
                        mapping[alias] = target_node
        return mapping

    def _lookup_node(self, name, getter):

        try:
            ret = self._mapping[name]
            vvv("Found alias for %s => %s" % (name, ret))

        except KeyError, e:
            ret = name

        return getter(ret)

