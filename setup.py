# -*- coding: utf-8 -*-
#$HeadURL$
#$LastChangedDate$
#$LastChangedRevision$

import os
import time
from setuptools import setup, find_packages, Command
from setuptools.command.install import install

version = '0.1'

class InstallCommand(install):
    """Customized setuptools install command - prints a friendly greeting."""
    def run(self):
        print "Hello, openfoamer, how are you? :)"
        time.sleep(2)	
        #os.system("./install_foam_utilities.sh") #Lo saco de acá porque necesito sudo para correr el install, y wmake no corre como sudo. (No pasa en los virtualenv porque /usr/local/lib no es de root)
        os.system("./compileUI.sh")
	install.run(self)

class CleanCommand(Command):
    description = "custom clean command \
    that forcefully removes dist/build directories"
    user_options = []

    def initialize_options(self):
        self.cwd = None

    def finalize_options(self):
        self.cwd = os.getcwd()

    def run(self):
        assert os.getcwd() == self.cwd, 'Must be in root: %s' % self.cwd
	print "Burning everything"
	time.sleep(1)
        os.system('./Allwclean')

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    '\n' +
    read('LICENSE.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('README.md')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('Contributors.txt')
    )

install_requires = [
        'setuptools',
        'matplotlib',
        'PyFoam==0.6.4'
        ]

#try:
#    import json
#except ImportError:
#    install_requires.append('simplejson')

#tests_require = ['pyPdf']
#sphinx_require = ['sphinx']
#hyphenation_require = ['wordaxe>=1.0']
#images_require = ['PIL']
#pdfimages_require = ['pyPdf','PythonMagick']
#pdfimages2_require = ['pyPdf','SWFTools']
#svgsupport_require = ['svg2rlg']
#aafiguresupport_require = ['aafigure>=0.4']
#mathsupport_require = ['matplotlib']
#rawhtmlsupport_require = ['xhtml2pdf']

setup(
    name="petroSym",
    version=version,
    packages=find_packages(exclude=[]),
    package_data=dict(petroSym=['images/fromHelyx/*.png',
	'images/*.png',
	'caseDicts/*',
	'pvsms/*',
      'matplotlibrc'
	]),
    include_package_data=True,
    dependency_links=[],
    install_requires=install_requires,
    #tests_require=tests_require,
    #extras_require=dict(
    #    tests=tests_require,
    #    sphinx=sphinx_require,
    #    hyphenation=hyphenation_require,
    #    images=images_require,
    #    pdfimages=pdfimages_require,
    #    pdfimages2=pdfimages2_require,
    #    svgsupport=svgsupport_require,
    #    aafiguresupport=aafiguresupport_require,
    #    mathsupport=mathsupport_require,
    #    rawhtmlsupport=rawhtmlsupport_require,
    #),
    classifiers=[
        'Development Status :: 1 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: GNU General Public License :: GPL-2',
        'Operating System :: OS Independent',
        'Operating System :: Linux :: Ubuntu',
        'Programming Language :: Python',
        'Topic :: Communications :: Email',
        'Topic :: Documentation',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    author="Juan Marcelo Gimenez",
    author_email="jmarcelogimenez at gmail dot com",
    description="GUI for OpenFOAM",
    long_description=long_description,
    license="GNU GPL-2",
    keywords="openfoam GUI",
    url="https://github.com/jmarcelogimenez/petroSym",
    download_url="https://github.com/jmarcelogimenez/petroSym",
    entry_points={'console_scripts': ['petroSym = petroSym.__main__:main']},
    cmdclass = {
        'clean': CleanCommand,
        'install': InstallCommand
    }
)
