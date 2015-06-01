from distutils.core import setup, Extension

module1 = Extension('testmodule', sources = ['testmodule.c', 'coordtrans.cpp'])

setup(name='PackageName',
      version = '1.0',
      description = 'this is a demo package',
      ext_modules = [module1])
