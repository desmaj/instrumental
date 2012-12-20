import gc
import os
import sys
from xml.etree import ElementTree

ZERO = '0.000000'
ONE = '1.000000'

class TestXMLReport(object):
    
    def _run_test(self, *args, **kwargs):
        from instrumental import api
        from instrumental.recorder import ExecutionRecorder
        ExecutionRecorder.reset()
        c = api.Coverage()
        modname = 'instrumental.test.samples.robust'
        c.start([modname], [])
        if modname in sys.modules:
            robust = sys.modules[modname]
            reload(robust)
        else:
            from instrumental.test.samples import robust
        robust.test_func(*args, **kwargs)
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
    
    def test_full_coverage_report(self):
        from instrumental.reporting import ExecutionReport
        
        recorder = self._run_test(True, True, False, True, False)
        
        report = ExecutionReport(os.getcwd(), recorder.metadata)
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
                      'branch-rate': '0.600000',
                      'line-rate': ONE,
                      'children': [{'tag': 'methods'}, lines_spec],
                      }
        root_children_spec = (
            {'tag': 'packages',
             'children': [{'tag': 'package',
                           'name': 'instrumental.test.samples',
                           'branch-rate': '0.600000',
                           'line-rate': ONE,
                           'children': [{'tag': 'classes',
                                         'children': [class_spec],
                                         }]
                           }]
             })
        spec = {'tag': 'coverage',
                'branch-rate': '0.600000',
                'line-rate': ONE,
                'children': [root_children_spec]
                }
                
        self._verify_element(root, spec)
        os.remove(xml_filename)
    
    def test_partial_coverage_report(self):
        from instrumental.reporting import ExecutionReport
        
        recorder = self._run_test(True, False, False, True, False, 0)
        
        report = ExecutionReport(os.getcwd(), recorder.metadata)
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
                      'branch-rate': '0.500000',
                      'line-rate': '0.700000',
                      'children': [{'tag': 'methods'}, lines_spec],
                      }
        root_children_spec = (
            {'tag': 'packages',
             'children': [{'tag': 'package',
                           'name': 'instrumental.test.samples',
                           'branch-rate': '0.500000',
                           'line-rate': '0.700000',
                           'children': [{'tag': 'classes',
                                         'children': [class_spec],
                                         }]
                           }]
             })
        spec = {'tag': 'coverage',
                'branch-rate': '0.500000',
                'line-rate': '0.700000',
                'children': [root_children_spec]
                }
                
        self._verify_element(root, spec)
        os.remove(xml_filename)
