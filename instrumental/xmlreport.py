#
# Copyright (C) 2012  Matthew J Desmarais

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
import os
import sys
import time

from xml.etree import ElementTree

import instrumental
from instrumental.constructs import BooleanDecision

class CoverageObject(object):

    @property
    def line_rate(self):
        statements = self.statements
        if statements:
            total_statements = len(statements)
            hit_statements = len([statement for statement in statements
                                  if statement])
            return float(hit_statements) / total_statements
        else:
            return 1.0

    @property
    def branch_rate(self):
        decisions = self.decisions
        if decisions:
            total_conditions = 0
            for decision in self.decisions:
                total_conditions += decision.number_of_conditions(self.options.report_conditions_with_literals)
            if total_conditions:
                total_conditions_hit = 0
                for decision in self.decisions:
                    total_conditions_hit += decision.number_of_conditions_hit()
                return float(total_conditions_hit) / total_conditions
            else:
                return 1.0
        else:
            return 1.0

    @property
    def condition_rate(self):
        if self.conditions:
            total_conditions = sum(construct.number_of_conditions(self.options.report_conditions_with_literals)
                                   for construct in self.conditions)
            total_conditions_hit = sum(construct.number_of_conditions_hit()
                                       for construct in self.conditions)
            return float(total_conditions_hit) / total_conditions
        else:
            return 1.0

    @property
    def decisions(self):
        return [construct for construct in self.constructs
                if construct.is_decision()]

    @property
    def conditions(self):
        return [construct for construct in self.constructs
                if not construct.is_decision()]

    def to_element(self):
        element = ElementTree.Element(self.tag)
        if hasattr(self, 'name'):
            element.attrib['name']  = self.name
        element.attrib['complexity'] = '0.0'
        element.attrib['line-rate'] = "%f" % self.line_rate
        element.attrib['branch-rate'] = "%f" % self.branch_rate
        element.attrib['condition-rate'] = "%f" % self.condition_rate
        return element

class Coverage(CoverageObject):
    tag = 'coverage'

    def __init__(self, working_directory, metadata, options):
        self._working_directory = working_directory
        self._metadata = metadata
        self.options = options

    @property
    def statements(self):
        _statements = []
        for modulename in self._metadata:
            _statements += self._metadata[modulename].lines.values()
        return _statements

    @property
    def constructs(self):
        return [construct
                for modulename in self._metadata
                for construct in self._metadata[modulename].constructs.values()]

    def _package_for_module(self, modulename):
        # REMIND:
        # This funny business with 'os.path.sep.join'. Let me tell you: if you
        # replace it with the much more sensible 'os.path.join' form you get a
        # weird exception, "AttributeError: version". I have no idea what this
        # is all aboot, but it was blocking the 0.5.2 release (and python 3.3
        # compatibility) so I worked around it. Gotta figure this out later :)
        package_path = os.path.sep.join([modulename.replace('.', os.path.sep),
                                         '__init__.py'])
        if os.path.exists(package_path):
            return modulename
        else:
            return modulename.rsplit('.', 1)[0]

    def _path_for_module(self, modulename):
        package_path = os.path.join(modulename.replace('.', os.path.sep),
                                    '__init__.py')
        if os.path.exists(package_path):
            return package_path
        else:
            return modulename.replace('.', os.path.sep) + ".py"

    def to_element(self):
        coverage_element = super(Coverage, self).to_element()
        del coverage_element.attrib['complexity']
        coverage_element.attrib['timestamp'] = str(int(time.time()))
        coverage_element.version = instrumental.__version__

        comment = 'Generated by instrumental: http://bitbucket.org/desmaj/instrumental'
        coverage_element.append(ElementTree.Comment(comment))

        here = self._working_directory
        packages = {}
        for modulename in self._metadata:
            packagename = self._package_for_module(modulename)
            modules = packages.setdefault(packagename, [])
            modules.append((modulename, self._path_for_module(modulename)))

        packages_element = ElementTree.Element('packages')
        for packagename, modulenames in packages.items():
            package_coverage = PackageCoverage(packagename,
                                               packages[packagename],
                                               self._metadata,
                                               self.options)
            package_element = package_coverage.to_element()
            packages_element.append(package_element)

        coverage_element.append(packages_element)

        return coverage_element

class PackageCoverage(CoverageObject):
    tag = 'package'

    def __init__(self, name, modules, metadata, options):
        self.name = name
        self._modules = modules
        self._metadata = metadata
        self.options = options

    @property
    def statements(self):
        _statements = []
        for modulename, modulefile in self._modules:
            _statements += self._metadata[modulename].lines.values()
        return _statements

    @property
    def constructs(self):
        return [construct
                for modulename, modulefile in self._modules
                for construct in self._metadata[modulename].constructs.values()]

    def to_element(self):
        element = super(PackageCoverage, self).to_element()

        modules = ElementTree.Element('classes')
        element.append(modules)

        for modulename, modulefile in self._modules:
            module_constructs = (
                [construct for construct
                 in self._metadata[modulename].constructs.values()])
            module_coverage = ModuleCoverage(modulename,
                                             modulefile,
                                             self._metadata[modulename],
                                             self.options)
            modules.append(module_coverage.to_element())

        return element

class ModuleCoverage(CoverageObject):
    tag = 'class'

    def __init__(self, name, filename, metadata, options):
        self.name = name
        self.filename = filename
        self._metadata = metadata
        self.options = options

    @property
    def statements(self):
        return self._metadata.lines.values()

    @property
    def constructs(self):
        return self._metadata.constructs.values()

    def to_element(self):
        element = super(ModuleCoverage, self).to_element()
        element.attrib['filename'] = self.filename
        element.append(ElementTree.Element('methods'))

        lines_element = ElementTree.Element('lines')
        for lineno, hit in sorted(self._metadata.lines.items()):
            line_element = ElementTree.Element('line')
            line_element.attrib['line'] = str(lineno)
            line_element.attrib['hits'] = str(int(hit))
            lines_element.append(line_element)
        element.append(lines_element)

        return element

class XMLCoverageReport(object):

    def __init__(self, working_directory, metadata, options):
        self._working_directory = working_directory
        self._metadata = metadata
        self.options = options

    def write(self, filename):
        tree = str(self)
        document = '\n'.join([
                '<?xml version="1.0" ?>',
                '<!DOCTYPE coverage ',
                "  SYSTEM 'http://cobertura.sourceforge.net/xml/coverage-03.dtd'>",
                tree,
                ])
        with open(filename, 'w') as f:
            f.write(document)

    def __str__(self):
        return ElementTree.tostring(self.tree.getroot()).decode()

    @property
    def tree(self):
        coverage_element = Coverage(self._working_directory, self._metadata, self.options)
        coverage = coverage_element.to_element()

        _tree = ElementTree.ElementTree(coverage)
        return _tree
