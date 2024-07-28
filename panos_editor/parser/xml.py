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
        self.xpath = []

    @classmethod
    def from_xml(cls, xml: Element, current_xpath: list = None):
        this = cls()

        xpath = this.calc_xpath(xml)
        if not current_xpath:
            my_xpath = [xpath]
        else:
            my_xpath = current_xpath.copy()
            my_xpath.append(xpath)

        this.xpath = my_xpath

        for child in xml:
            if len(child) == 0 and child.text:
                add_to_dict(child.tag, this.elements, child.text)
            else:
                add_to_list(
                    child.tag, this.children, PanosObject.from_xml(child, my_xpath)
                )

        this.attrs = dict(xml.attrib)
        return this

    def calc_xpath(self, xml: Element):
        if xml.tag == "entry":
            name = xml.attrib.get("name")
            return f"entry[@name='{name}']"
        else:
            return xml.tag

    def to_dict(self):
        children_dicts = {}
        for k, v in self.children.items():
            children_dicts[k] = [x.to_dict() for x in v]

        return {
            "xpath": "/" + "/".join(self.xpath),
            "attrs": self.attrs,
            "text": self.text,
            "children": children_dicts,
            "elements": self.elements,
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
