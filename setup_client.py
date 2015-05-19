from distutils.core import setup, Extension

module1 = Extension('client',
                    sources = ['clientmodule.c','queque.c'])

setup (name = 'client',
       version = '1.0',
       description = 'This is a client package',
       ext_modules = [module1])