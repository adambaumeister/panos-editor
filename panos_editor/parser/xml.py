from typing import Optional, Union

from pydantic import BaseModel, Field
from lxml.etree import Element


def add_to_dict(key: str, d: dict, item):
    if key in d:
        if isinstance(d.get(key), list):
            d[key].append(item)
        else:
            d[key] = [d[key], item]
    else:
        d[key] = item


def add_to_list(key: str, d: dict, item):
    if key in d:
        d[key].append(item)
    else:
        d[key] = [item]


class PanosObject:
    def __init__(self):
        self.children: dict[str, list[PanosObject]] = {}
        self.elements: dict[str, Union[str, list]] = {}
        self.attrs: dict = {}
        self.text = ""

    @classmethod
    def from_xml(cls, xml: Element):
        this = cls()
        for child in xml:
            if len(child) == 0 and child.text:
                add_to_dict(child.tag, this.elements, child.text)
            else:
                add_to_list(child.tag, this.children, PanosObject.from_xml(child))

        this.attrs = dict(xml.attrib)
        return this

    def to_dict(self):
        children_dicts = {}
        for k, v in self.children.items():
            children_dicts[k] = [x.to_dict() for x in v]

        return {
            "attrs": self.attrs,
            "text": self.text,
            "children": children_dicts,
            "elements": self.elements
        }


class PanosObjectCollection:
    def __init__(self, objects: list[PanosObject]):
        self.objects = objects

    def __iter__(self):
        return iter(self.objects)

    def __repr__(self):
        rstr = super().__repr__()
        return f"{rstr} <{len(self.objects)} members>"

    def __len__(self):
        return len(self.objects)