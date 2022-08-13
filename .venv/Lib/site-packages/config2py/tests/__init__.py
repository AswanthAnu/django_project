import sys

try:
    from importlib.resources import files  # ... and any other things you want to get
except ImportError:
    from importlib_resources import files  # pip install importlib_resources

module_path = files(sys.modules[__name__])
ppath = module_path.joinpath



