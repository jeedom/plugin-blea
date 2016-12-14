import pkgutil 
import logging
__path__ = pkgutil.extend_path(__path__, __name__)
for importer, modname, ispkg in pkgutil.walk_packages(path=__path__, prefix=__name__+'.'):
	logging.info("Import de la configuration " + modname)
	__import__(modname)