from distutils.core import setup, Extension

module1 = Extension('server',
                    sources = ['servermodule.c','queque.c'])

setup (name = 'server',
       version = '1.0',
       description = 'This is a server package',
       ext_modules = [module1])