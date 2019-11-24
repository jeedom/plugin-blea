import pkgutil
import logging
__path__ = pkgutil.extend_path(__path__, __name__)
for importer, modname, ispkg in pkgutil.walk_packages(path=__path__, prefix=__name__+'.'):
	logging.info("LOADER------Import de la configuration " + modname)
	try:
		__import__(modname)
	except Exception as e:
		logging.debug('Impossible d\'importer ' + modname + ' : ' + str(e))
