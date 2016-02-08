import gc
import os
import sys
from xml.etree import ElementTree

ZERO = '0.000000'
ONE = '1.000000'

if sys.version_info.major == 3:
    from imp import reload

class DummyConfig(object):
    instrument_assertions = True
    instrument_comparisons = True
    use_metadata_cache = False
    report_conditions_with_literals = False

class TestXMLReport(object):

    def setUp(self):
        self.config = DummyConfig()

    def _run_test(self, *args, **kwargs):
        from instrumental import api
        from instrumental.recorder import ExecutionRecorder
        ExecutionRecorder.reset()
        c = api.Coverage(self.config, '.')
        modname = kwargs.pop('modname',
                             'instrumental.test.samples.robust')
        c.start([modname], [])
        if modname in sys.modules:
            testmod = sys.modules[modname]
            reload(testmod)
        else:
            testmod = __import__(modname, fromlist=modname.split('.')[:-1])
        testmod.test_func(*args, **kwargs)
        c.stop()
        return c.recorder

    def _verify_element(self, element, spec):
        assert element.tag == spec.pop('tag')
        child_specs = spec.pop('children', [])
        for attr, expected in spec.items():
            assert element.attrib[attr] == expected,(
                (attr, element.attrib[attr], expected))
        children = list(element)
        assert len(children) == len(child_specs)
        for child, child_spec in zip(children, child_specs):
            self._verify_element(child, child_spec)

    def test_full_coverage_constructs(self):
        from instrumental import constructs
        from instrumental.reporting import ExecutionReport

        recorder = self._run_test(True, True, False, True, False)
        metadata = recorder.metadata['instrumental.test.samples.robust']

        assert 10 == len(metadata.constructs), metadata.constructs.keys()

        decision = metadata.constructs['5.1']
        assert isinstance(decision, constructs.BooleanDecision)
        assert 2 == decision.number_of_conditions(False)
        assert 1 == decision.conditions_missed(False)

        boolop = metadata.constructs['5.2']
        assert isinstance(boolop, constructs.LogicalAnd)
        assert 3 == boolop.number_of_conditions(False)
        assert 2 == len(boolop.conditions_missed(False))

        decision = metadata.constructs['8.1']
        assert isinstance(decision, constructs.BooleanDecision)
        assert 2 == decision.number_of_conditions(False)
        assert 1 == decision.conditions_missed(False)

        boolop = metadata.constructs['8.2']
        assert isinstance(boolop, constructs.LogicalOr)
        assert 3 == boolop.number_of_conditions(False)
        assert 2 == len(boolop.conditions_missed(False))

        decision = metadata.constructs['11.1']
        assert isinstance(decision, constructs.BooleanDecision)
        assert 2 == decision.number_of_conditions(False)
        assert 0 == decision.conditions_missed(False)

        compare = metadata.constructs['11.2']
        assert isinstance(compare, constructs.Comparison)
        assert 2 == compare.number_of_conditions(False)
        assert 0 == compare.conditions_missed(False)

        decision = metadata.constructs['14.1']
        assert isinstance(decision, constructs.BooleanDecision)
        assert 2 == decision.number_of_conditions(False)
        assert 1 == decision.conditions_missed(False)

        decision = metadata.constructs['16.1']
        assert isinstance(decision, constructs.BooleanDecision)
        assert 1 == decision.number_of_conditions(False)
        assert 0 == decision.conditions_missed(False)

        boolop = metadata.constructs['16.2']
        assert isinstance(boolop, constructs.LogicalOr)
        assert 2 == boolop.number_of_conditions(False)
        assert 1 == len(boolop.conditions_missed(False))

        boolop = metadata.constructs['16.3']
        assert isinstance(boolop, constructs.LogicalAnd)
        assert 2 == boolop.number_of_conditions(False)
        assert 1 == len(boolop.conditions_missed(False))

    def test_full_coverage_report(self):
        from instrumental.reporting import ExecutionReport

        recorder = self._run_test(True, True, False, True, False)
        report = ExecutionReport(os.getcwd(), recorder.metadata, self.config)
        xml_filename = 'test-xml-report.xml'
        report.write_xml_coverage_report(xml_filename)

        tree = ElementTree.parse(xml_filename)
        root = tree.getroot()

        lines_spec = {'tag': 'lines',
                      'children': [{'tag': 'line',
                                    'hits': '1',
                                    'line': '1',
                                    },
                                   {'tag': 'line',
                                    'hits': '1',
                                    'line': '3',
                                    },
                                   {'tag': 'line',
                                    'hits': '1',
                                    'line': '5',
                                    },
                                   {'tag': 'line',
                                    'hits': '1',
                                    'line': '6',
                                    },
                                   {'tag': 'line',
                                    'hits': '1',
                                    'line': '8',
                                    },
                                   {'tag': 'line',
                                    'hits': '1',
                                    'line': '9',
                                    },
                                   {'tag': 'line',
                                    'hits': '1',
                                    'line': '11',
                                    },
                                   {'tag': 'line',
                                    'hits': '1',
                                    'line': '12',
                                    },
                                   {'tag': 'line',
                                    'hits': '1',
                                    'line': '14',
                                    },
                                   {'tag': 'line',
                                    'hits': '1',
                                    'line': '16',
                                    },
                                   ]}
        class_spec = {'tag': 'class',
                      'name': 'instrumental.test.samples.robust',
                      'filename': 'instrumental/test/samples/robust.py',
                      'condition-rate': '0.500000',
                      'branch-rate': '0.666667',
                      'line-rate': ONE,
                      'children': [{'tag': 'methods'}, lines_spec],
                      }
        root_children_spec = (
            {'tag': 'packages',
             'children': [{'tag': 'package',
                           'name': 'instrumental.test.samples',
                           'condition-rate': '0.500000',
                           'branch-rate': '0.666667',
                           'line-rate': ONE,
                           'children': [{'tag': 'classes',
                                         'children': [class_spec],
                                         }]
                           }]
             })
        spec = {'tag': 'coverage',
                'condition-rate': '0.500000',
                'branch-rate': '0.666667',
                'line-rate': ONE,
                'children': [root_children_spec]
                }
        self._verify_element(root, spec)
        os.remove(xml_filename)

    def test_partial_coverage_constructs(self):
        from instrumental import constructs
        from instrumental.reporting import ExecutionReport

        recorder = self._run_test(True, False, False, True, False, 0)
        metadata = recorder.metadata['instrumental.test.samples.robust']

        assert 10 == len(metadata.constructs), metadata.constructs.keys()

        decision = metadata.constructs['5.1']
        assert isinstance(decision, constructs.BooleanDecision)
        assert 2 == decision.number_of_conditions(False)
        assert 1 == decision.conditions_missed(False)

        boolop = metadata.constructs['5.2']
        assert isinstance(boolop, constructs.LogicalAnd)
        assert 3 == boolop.number_of_conditions(False)
        assert 2 == len(boolop.conditions_missed(False))

        decision = metadata.constructs['8.1']
        assert isinstance(decision, constructs.BooleanDecision)
        assert 2 == decision.number_of_conditions(False)
        assert 1 == decision.conditions_missed(False)

        boolop = metadata.constructs['8.2']
        assert isinstance(boolop, constructs.LogicalOr)
        assert 3 == boolop.number_of_conditions(False)
        assert 2 == len(boolop.conditions_missed(False))

        decision = metadata.constructs['11.1']
        assert isinstance(decision, constructs.BooleanDecision)
        assert 2 == decision.number_of_conditions(False)
        assert 1 == decision.conditions_missed(False)

        compare = metadata.constructs['11.2']
        assert isinstance(compare, constructs.Comparison)
        assert 2 == compare.number_of_conditions(False)
        assert 1 == compare.conditions_missed(False)

        decision = metadata.constructs['14.1']
        assert isinstance(decision, constructs.BooleanDecision)
        assert 2 == decision.number_of_conditions(False)
        assert 1 == decision.conditions_missed(False)

        decision = metadata.constructs['16.1']
        assert isinstance(decision, constructs.BooleanDecision)
        assert 1 == decision.number_of_conditions(False)
        assert 0 == decision.conditions_missed(False)

        boolop = metadata.constructs['16.2']
        assert isinstance(boolop, constructs.LogicalOr)
        assert 2 == boolop.number_of_conditions(False)
        assert 1 == len(boolop.conditions_missed(False))

        boolop = metadata.constructs['16.3']
        assert isinstance(boolop, constructs.LogicalAnd)
        assert 2 == boolop.number_of_conditions(False)
        assert 1 == len(boolop.conditions_missed(False))

    def test_partial_coverage_report(self):
        from instrumental.reporting import ExecutionReport

        recorder = self._run_test(True, False, False, True, False, 0)

        report = ExecutionReport(os.getcwd(), recorder.metadata, self.config)
        xml_filename = 'test-xml-report.xml'
        report.write_xml_coverage_report(xml_filename)

        tree = ElementTree.parse(xml_filename)
        root = tree.getroot()

        lines_spec = {'tag': 'lines',
                      'children': [{'tag': 'line',
                                    'hits': '1',
                                    'line': '1',
                                    },
                                   {'tag': 'line',
                                    'hits': '1',
                                    'line': '3',
                                    },
                                   {'tag': 'line',
                                    'hits': '1',
                                    'line': '5',
                                    },
                                   {'tag': 'line',
                                    'hits': '0',
                                    'line': '6',
                                    },
                                   {'tag': 'line',
                                    'hits': '1',
                                    'line': '8',
                                    },
                                   {'tag': 'line',
                                    'hits': '0',
                                    'line': '9',
                                    },
                                   {'tag': 'line',
                                    'hits': '1',
                                    'line': '11',
                                    },
                                   {'tag': 'line',
                                    'hits': '0',
                                    'line': '12',
                                    },
                                   {'tag': 'line',
                                    'hits': '1',
                                    'line': '14',
                                    },
                                   {'tag': 'line',
                                    'hits': '1',
                                    'line': '16',
                                    },
                                   ]}
        class_spec = {'tag': 'class',
                      'name': 'instrumental.test.samples.robust',
                      'filename': 'instrumental/test/samples/robust.py',
                      'condition-rate': '0.416667',
                      'branch-rate': '0.555556',
                      'line-rate': '0.700000',
                      'children': [{'tag': 'methods'}, lines_spec],
                      }
        root_children_spec = (
            {'tag': 'packages',
             'children': [{'tag': 'package',
                           'name': 'instrumental.test.samples',
                           'condition-rate': '0.416667',
                           'branch-rate': '0.555556',
                           'line-rate': '0.700000',
                           'children': [{'tag': 'classes',
                                         'children': [class_spec],
                                         }]
                           }]
             })
        spec = {'tag': 'coverage',
                'condition-rate': '0.416667',
                'branch-rate': '0.555556',
                'line-rate': '0.700000',
                'children': [root_children_spec]
                }

        self._verify_element(root, spec)
        os.remove(xml_filename)

    def test_zero_conditions(self):
        from instrumental import constructs
        from instrumental.reporting import ExecutionReport

        modname = 'instrumental.test.samples.zeroconditions'
        recorder = self._run_test(modname=modname)
        report = ExecutionReport(os.getcwd(), recorder.metadata, self.config)
        xml_filename = 'test-xml-report.xml'
        report.write_xml_coverage_report(xml_filename)

        tree = ElementTree.parse(xml_filename)
        root = tree.getroot()

        lines_spec = {'tag': 'lines',
                      'children': [{'tag': 'line',
                                    'hits': '1',
                                    'line': '1',
                                    },
                                   {'tag': 'line',
                                    'hits': '1',
                                    'line': '3',
                                    },
                                   {'tag': 'line',
                                    'hits': '1',
                                    'line': '5',
                                    },
                                   {'tag': 'line',
                                    'hits': '1',
                                    'line': '6',
                                    },
                                   ]}
        class_spec = {'tag': 'class',
                      'name': 'instrumental.test.samples.zeroconditions',
                      'filename': 'instrumental/test/samples/zeroconditions.py',
                      'condition-rate': '1.000000',
                      'branch-rate': '1.000000',
                      'line-rate': '1.000000',
                      'children': [{'tag': 'methods'}, lines_spec],
                      }
        root_children_spec = (
            {'tag': 'packages',
             'children': [{'tag': 'package',
                           'name': 'instrumental.test.samples',
                           'condition-rate': '1.000000',
                           'branch-rate': '1.000000',
                           'line-rate': '1.000000',
                           'children': [{'tag': 'classes',
                                         'children': [class_spec],
                                         }]
                           }]
             })
        spec = {'tag': 'coverage',
                'condition-rate': '1.000000',
                'branch-rate': '1.000000',
                'line-rate': '1.000000',
                'children': [root_children_spec]
                }

        self._verify_element(root, spec)
        os.remove(xml_filename)
