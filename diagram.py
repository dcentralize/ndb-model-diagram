#!/usr/bin/python

import google
import jinja2
import os
import sys

class Jin():
    pass

def create_class(cls):
    global relations
    name = cls.__name__
    properties = []
    for p in cls._properties:
        if p != "class":
            j = Jin()
            j.name = p
            property = cls._properties[p]
            multiple = property._repeated
            if property.__class__ == google.appengine.ext.ndb.model.KeyProperty:
                j.type = str(property._kind)
                relations += ['%s -> %s [headlabel="1" taillabel="%s" arrowhead="none"];\n' % (str(property._kind), cls.__name__, ("*" if multiple else "1"))]
            else:
                j.type = str(property).split("Property")[0]
            if multiple:
                j.type += "[]"
            properties += [j]
    
    try:
        relations += ['%s -> %s [arrowhead="onormal"];\n' % (name, cls.__bases__[0].__name__)]
    except:
        pass
    template = jinja.get_template("class.html")
    template_values = {
        "properties": properties,
        "name": name
    }
    return template.render(template_values).replace("\n", "").replace("    ", "")

if __name__ == "__main__" and len(sys.argv) > 1:
    module = __import__(sys.argv[1])
    jinja = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
    relations = []
    ret = 'digraph test {\n' +\
        'rankdir=LR;\n' +\
        'size="8,5"\n' +\
        'node [shape = circle];\n'
    
    for model in dir(module):
        try:
            ret += '"%s" [style="filled, bold" penwidth=5 fillcolor="white" shape="Mrecord" label =<%s>];\n' % (model, create_class(eval("module.%s" % model)))
        except:
            pass
    
    for rel in relations:
        ret += rel
    
    ret += '}'
    print(ret)
else:
    print("Usage:\n  %s my_models_package | dot -Tsvg -o x.svg" % sys.argv[0])

