#
# -*- coding: utf-8 -*-
#
# This file is part of reclass (http://github.com/madduck/reclass)
#
# Copyright © 2007–13 martin f. krafft <madduck@madduck.net>
# Released under the terms of the Artistic Licence 2.0
#
import os
import sys
from reclass.errors import NotFoundError
from reclass.storage.yaml_fs import YamlFile

SKIPDIRS = ( '.git' , '.svn' , 'CVS', 'SCCS', '.hg', '_darcs' )
FILE_EXTENSION = '.yml'
HOSTS_FILE_EXTENSION = '.hosts'


def vvv(msg):
#    print >>sys.stderr, msg
    pass


class Directory(object):

    def __init__(self, path, read_groups = True, use_namespaces = False):
        ''' Initialise a directory object '''
        if not os.path.isdir(path):
            raise NotFoundError('No such directory: %s' % path)
        if not os.access(path, os.R_OK|os.X_OK):
            raise NotFoundError('Cannot change to or read directory: %s' % path)
        self._path = os.path.abspath(path)
        self._nodes = {}
        self._use_namespaces = use_namespaces
        self._groups = {}
        self._entity_cache = {}
        self._read_groups = read_groups
        self._walk()

    def read_entity(self, name):
        if not self._nodes.has_key(name):
            raise NotFoundError("No node %s defined" % name)
        fname = self._nodes[name]
        if self._entity_cache.has_key(fname):
            vvv('CACHE HIT {0}'.format(fname))
            return self._entity_cache[fname]
        vvv('READING {0}'.format(fname))
        entity = YamlFile(fname).entity
        self._entity_cache[fname] = entity
        return entity

    def node_uri(self, name):
        return self._nodes[name]

    def entities(self):
        entities = {}
        for k, v in self._nodes.iteritems():
            entity = self.read_entity(k)
            entities[k] = entity
        return entities

    def _register_files(self, dirpath, filenames):
        for f in filter(lambda f: f.endswith(FILE_EXTENSION), filenames):
            nodename = f[:-len(FILE_EXTENSION)]
            if self._use_namespaces:
                nodename = self.__namespace(dirpath, nodename)
            f = os.path.join(dirpath, f)
            vvv('REGISTER NODE {0} ({1})'.format(nodename, f))
            self._nodes[nodename] = f

    def _register_groups(self, dirpath, filenames):
        for f in filter(lambda f: f.endswith(HOSTS_FILE_EXTENSION), filenames):
            grp = f[:-len(HOSTS_FILE_EXTENSION)]
            vvv('REGISTER HOSTS {0}'.format(grp))
            ptr = os.path.join(dirpath, ''.join([grp, FILE_EXTENSION]))
            f = os.path.join(dirpath, f)
            self._groups[grp] = ptr
            if self._nodes.has_key(grp):
                del self._nodes[grp]
            ins = open( f, "r" )
            for line in ins:
                line = line.rstrip()
                if self._nodes.has_key(line):
                    # todo make it possible to merge multiple definitions
                    raise LookupError('Node %s already registered from %s' % (line, self._nodes[line]))
                vvv('REGISTER NODE {0}->{1}'.format(line, ptr))
                self._nodes[line] = ptr
            ins.close()

    def __namespace(self, dirpath, nodename):
        fullpath = os.path.abspath(os.path.join(dirpath, nodename))
        namespace = fullpath[len(self._path)+1:].replace(os.path.sep, '.')
        vvv('Got namespace {0}'.format(namespace))
        return namespace

    nodes = property(lambda self: self._nodes)

    def _walk(self):
        for dirpath, dirnames, filenames in os.walk(self._path,
                                                      topdown=True,
                                                      followlinks=True):
            vvv('RECURSE {0}, {1} files, {2} subdirectories'.format(
                dirpath.replace(os.getcwd(), '.'), len(filenames), len(dirnames)))
            for d in SKIPDIRS:
                if d in dirnames:
                    vvv('   SKIP subdirectory {0}'.format(d))
                    dirnames.remove(d)
            self._register_files(dirpath, filenames)
            if self._read_groups:
                self._register_groups(dirpath, filenames)

    def __repr__(self):
        return '<{0} {1}>'.format(self.__class__.__name__, self._path)

