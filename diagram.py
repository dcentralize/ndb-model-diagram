#!/usr/bin/python

from __future__ import unicode_literals

import jinja2
import os
import re
import sys
from google.appengine.ext.ndb.model import KeyProperty


relations = []
help_message = """Generates a class diagram for Google Appengine models.


Example usage:
  %s module | dot -Tsvg -o x.svg

  note: module is the module name, not the python file.

"""


class Jin():
    """
    An empty class solely with the purpose of being an object which can
    be instantiated.

    """
    style = ''


def create_table(cls):
    """
    Generates a table for a class and puts its relations in the
    relations list.

    """
    global relations
    name = cls.__name__
    properties = []
    for p in cls._properties:
        if p == 'class':  # This is used for subclassing PolyModels
            continue
        j = Jin()
        j.name = p
        property = cls._properties[p]
        multi = property._repeated
        if issubclass(type(property), KeyProperty):
            j.type = property._kind
            j.style = 'color="red"'
            relations += [('%s -> %s [headlabel="1" taillabel="%s" ' +
                                    'arrowhead="none"];') % (property._kind,
                                    name, ('*' if multi else '1'))]
        else:
            j.type = unicode(property).split('Property')[0]
        if multi:
            j.type += '[]'
        properties += [j]
    # Create arrows for inherited classes
    for base in cls.__bases__:
        try:
            relations += ['%s -> %s [arrowhead="onormal"];\n' % (
                                                        name, base.__name__)]
        except:
            pass

    doc = cls.__doc__
    if doc:
        # Only use the text before the first empty line
        doc = re.sub('[ ]{2,}', '', doc).split('\n\n')[0].split('\n')
    return jinja.get_template("class.html").render({
        'properties': properties,
        'name': name,
        'doc': doc
    })


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(help_message % sys.argv[0])
        sys.exit(0)

    module = __import__(sys.argv[1])
    jinja = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(
                                                                    __file__)))
    ret = '\n'.join([
        'digraph test {',
        'rankdir=LR;',
        'size="8,5"',
        'node [shape = circle];'])

    for model in dir(module):
        try:
            ret += ('"%s" [style="filled, bold" penwidth=5 fillcolor="white"' +
                                ' shape="Mrecord" label =<%s>];\n') % (model,
                                create_table(eval("module.%s" % model)))
        except:
            pass

    print(ret + ''.join(relations) + '}')
