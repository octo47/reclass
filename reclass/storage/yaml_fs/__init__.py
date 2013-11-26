#
# -*- coding: utf-8 -*-
#
# This file is part of reclass (http://github.com/madduck/reclass)
#
# Copyright © 2007–13 martin f. krafft <madduck@madduck.net>
# Released under the terms of the Artistic Licence 2.0
#
from reclass.storage import NodeStorageBase
from yamlfile import YamlFile
from directory import Directory
from reclass.datatypes import Entity
import reclass.errors


class ExternalNodeStorage(NodeStorageBase):
    def __init__(self, nodes_uri, classes_uri):
        super(ExternalNodeStorage, self).__init__(nodes_uri, classes_uri)
        self._classes_directory = Directory(self._classes_uri, read_groups=False, use_namespaces=True)
        self._nodes_directory = Directory(self._nodes_uri)

    def _read_nodeinfo(self, name):
        return self.__read_nodeinfo(name, self._nodes_directory, {})

    def _read_classinfo(self, klass):
        return self.__read_nodeinfo(klass, self._classes_directory, {})

    def __read_nodeinfo(self, name, directory, seen, nodename=None):
        try:
            entity = directory.read_entity(name)
            seen[name] = True

            merge_base = Entity()
            for klass in entity.classes.as_list():
                if klass not in seen:
                    ret = self.__read_nodeinfo(klass, self._classes_directory, seen,
                                              name if nodename is None else nodename)[0]
                    # on every iteration, we merge the result of the
                    # recursive descend into what we have so far…
                    merge_base.merge(ret)

            # … and finally, we merge what we have at this level into the
            # result of the iteration, so that elements at the current level
            # overwrite stuff defined by parents
            merge_base.merge(entity)
            return merge_base, directory.node_uri(name)

        except IOError:
            if directory == self._classes_directory:
                raise reclass.errors.ClassNotFound('yaml_fs', name, self._classes_uri, nodename)
            else:
                raise reclass.errors.NodeNotFound('yaml_fs', name, self._nodes_uri)

    def _list_inventory(self):
        d = Directory(self.nodes_uri)

        entities = d.entities()
        nodeinfos = {}
        applications = {}
        classes = {}
        for nodename, entity in entities.iteritems():
            nodeinfo = self.nodeinfo(nodename)
            nodeinfos[nodename] = nodeinfo
            for a in nodeinfo['applications']:
                if a in applications:
                    applications[a].append(nodename)
                else:
                    applications[a] = [nodename]
            for c in nodeinfo['classes']:
                if c in classes:
                    classes[c].append(nodename)
                else:
                    classes[c] = [nodename]

        return nodeinfos, applications, classes
