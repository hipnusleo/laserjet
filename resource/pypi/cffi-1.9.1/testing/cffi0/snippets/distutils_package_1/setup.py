
from distutils.core import setup
import snip_basic_verify1

setup(
    packages=['snip_basic_verify1'],
    ext_modules=[snip_basic_verify1.ffi.verifier.get_extension()])
