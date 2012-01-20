import os
import shutil

from mako.exceptions import text_error_template
from mako.lookup import TemplateLookup

class HTMLCoverageReport(object):
    
    def __init__(self, summary, sources):
        self.summary = summary
        self.sources = sources
    
    def write(self, directory):
        print "writing html coverage report to", directory
        if os.path.isdir(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)
        
        resource_directory = os.path.join(os.path.dirname(__file__), 
                                          'resources')
        shutil.copy(os.path.join(resource_directory, 'jquery-1.7.1.min.js'), directory)
        shutil.copy(os.path.join(resource_directory, 'styles.css'), directory)
        
        template_directory = os.path.join(os.path.dirname(__file__), 
                                          'templates')
        template_lookup = TemplateLookup(directories=[template_directory],
                                         output_encoding='utf-8')
        
        packages_template = template_lookup.get_template('/html/packages.html')
        packages_html = packages_template.render(summary=self.summary)
        packages_path = os.path.join(directory, 'packages.html')
        with file(packages_path, 'w') as f:
            f.write(packages_html)
        
        for package, package_summary in self.summary.packages.items():
            for module, module_summary in package_summary.modules.items():
                module_template = template_lookup.get_template('/html/module.html')
                try:
                    module_html = module_template.render(module=module_summary,
                                                         source=self.sources[module].decode('utf-8'))
                except:
                    print text_error_template().render()
                    raise
                module_path = os.path.join(directory, module + '.html')
                with file(module_path, 'w') as f:
                    f.write(module_html)
