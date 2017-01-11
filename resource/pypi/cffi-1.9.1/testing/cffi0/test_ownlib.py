import py, sys
import subprocess, weakref
from cffi import FFI
from cffi.backend_ctypes import CTypesBackend


SOURCE = """\
#include <errno.h>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

EXPORT int test_getting_errno(void) {
    errno = 123;
    return -1;
}

EXPORT int test_setting_errno(void) {
    return errno;
};

typedef struct {
    long x;
    long y;
} POINT;

typedef struct {
    long left;
    long top;
    long right;
    long bottom;
} RECT;


EXPORT int PointInRect(RECT *prc, POINT pt)
{
    if (pt.x < prc->left)
        return 0;
    if (pt.x > prc->right)
        return 0;
    if (pt.y < prc->top)
        return 0;
    if (pt.y > prc->bottom)
        return 0;
    return 1;
};

EXPORT long left = 10;
EXPORT long top = 20;
EXPORT long right = 30;
EXPORT long bottom = 40;

EXPORT RECT ReturnRect(int i, RECT ar, RECT* br, POINT cp, RECT dr,
                        RECT *er, POINT fp, RECT gr)
{
    /*Check input */
    if (ar.left + br->left + dr.left + er->left + gr.left != left * 5)
    {
        ar.left = 100;
        return ar;
    }
    if (ar.right + br->right + dr.right + er->right + gr.right != right * 5)
    {
        ar.right = 100;
        return ar;
    }
    if (cp.x != fp.x)
    {
        ar.left = -100;
    }
    if (cp.y != fp.y)
    {
        ar.left = -200;
    }
    switch(i)
    {
    case 0:
        return ar;
        break;
    case 1:
        return dr;
        break;
    case 2:
        return gr;
        break;

    }
    return ar;
}

EXPORT int my_array[7] = {0, 1, 2, 3, 4, 5, 6};
"""

class TestOwnLib(object):
    Backend = CTypesBackend

    def setup_class(cls):
        cls.module = None
        from testing.udir import udir
        udir.join('testownlib.c').write(SOURCE)
        if sys.platform == 'win32':
            import os
            # did we already build it?
            if os.path.exists(str(udir.join('testownlib.dll'))):
                cls.module = str(udir.join('testownlib.dll'))
                return
            # try (not too hard) to find the version used to compile this python
            # no mingw
            from distutils.msvc9compiler import get_build_version
            version = get_build_version()
            toolskey = "VS%0.f0COMNTOOLS" % version
            toolsdir = os.environ.get(toolskey, None)
            if toolsdir is None:
                return
            productdir = os.path.join(toolsdir, os.pardir, os.pardir, "VC")
            productdir = os.path.abspath(productdir)
            vcvarsall = os.path.join(productdir, "vcvarsall.bat")
            # 64?
            arch = 'x86'
            if sys.maxsize > 2**32:
                arch = 'amd64'
            if os.path.isfile(vcvarsall):
                cmd = '"%s" %s' % (vcvarsall, arch) + ' & cl.exe testownlib.c ' \
                        ' /LD /Fetestownlib.dll'
                subprocess.check_call(cmd, cwd = str(udir), shell=True)    
                cls.module = str(udir.join('testownlib.dll'))
        else:
            subprocess.check_call(
                'cc testownlib.c -shared -fPIC -o testownlib.so',
                cwd=str(udir), shell=True)
            cls.module = str(udir.join('testownlib.so'))

    def test_getting_errno(self):
        if self.module is None:
            py.test.skip("fix the auto-generation of the tiny test lib")
        if sys.platform == 'win32':
            py.test.skip("fails, errno at multiple addresses")
        ffi = FFI(backend=self.Backend())
        ffi.cdef("""
            int test_getting_errno(void);
        """)
        ownlib = ffi.dlopen(self.module)
        res = ownlib.test_getting_errno()
        assert res == -1
        assert ffi.errno == 123

    def test_setting_errno(self):
        if self.module is None:
            py.test.skip("fix the auto-generation of the tiny test lib")
        if sys.platform == 'win32':
            py.test.skip("fails, errno at multiple addresses")
        if self.Backend is CTypesBackend and '__pypy__' in sys.modules:
            py.test.skip("XXX errno issue with ctypes on pypy?")
        ffi = FFI(backend=self.Backend())
        ffi.cdef("""
            int test_setting_errno(void);
        """)
        ownlib = ffi.dlopen(self.module)
        ffi.errno = 42
        res = ownlib.test_setting_errno()
        assert res == 42
        assert ffi.errno == 42

    def test_my_array_7(self):
        if self.module is None:
            py.test.skip("fix the auto-generation of the tiny test lib")
        ffi = FFI(backend=self.Backend())
        ffi.cdef("""
            int my_array[7];
        """)
        ownlib = ffi.dlopen(self.module)
        for i in range(7):
            assert ownlib.my_array[i] == i
        assert len(ownlib.my_array) == 7
        if self.Backend is CTypesBackend:
            py.test.skip("not supported by the ctypes backend")
        ownlib.my_array = list(range(10, 17))
        for i in range(7):
            assert ownlib.my_array[i] == 10 + i
        ownlib.my_array = list(range(7))
        for i in range(7):
            assert ownlib.my_array[i] == i

    def test_my_array_no_length(self):
        if self.module is None:
            py.test.skip("fix the auto-generation of the tiny test lib")
        if self.Backend is CTypesBackend:
            py.test.skip("not supported by the ctypes backend")
        ffi = FFI(backend=self.Backend())
        ffi.cdef("""
            int my_array[];
        """)
        ownlib = ffi.dlopen(self.module)
        for i in range(7):
            assert ownlib.my_array[i] == i
        py.test.raises(TypeError, len, ownlib.my_array)
        ownlib.my_array = list(range(10, 17))
        for i in range(7):
            assert ownlib.my_array[i] == 10 + i
        ownlib.my_array = list(range(7))
        for i in range(7):
            assert ownlib.my_array[i] == i

    def test_keepalive_lib(self):
        if self.module is None:
            py.test.skip("fix the auto-generation of the tiny test lib")
        ffi = FFI(backend=self.Backend())
        ffi.cdef("""
            int test_getting_errno(void);
        """)
        ownlib = ffi.dlopen(self.module)
        ffi_r = weakref.ref(ffi)
        ownlib_r = weakref.ref(ownlib)
        func = ownlib.test_getting_errno
        del ffi
        import gc; gc.collect()       # ownlib stays alive
        assert ownlib_r() is not None
        assert ffi_r() is not None    # kept alive by ownlib
        res = func()
        assert res == -1

    def test_keepalive_ffi(self):
        if self.module is None:
            py.test.skip("fix the auto-generation of the tiny test lib")
        ffi = FFI(backend=self.Backend())
        ffi.cdef("""
            int test_getting_errno(void);
        """)
        ownlib = ffi.dlopen(self.module)
        ffi_r = weakref.ref(ffi)
        ownlib_r = weakref.ref(ownlib)
        func = ownlib.test_getting_errno
        del ownlib
        import gc; gc.collect()       # ffi stays alive
        assert ffi_r() is not None
        assert ownlib_r() is not None # kept alive by ffi
        res = func()
        assert res == -1
        if sys.platform != 'win32':  # else, errno at multiple addresses
            assert ffi.errno == 123

    def test_struct_by_value(self):
        if self.module is None:
            py.test.skip("fix the auto-generation of the tiny test lib")
        ffi = FFI(backend=self.Backend())
        ffi.cdef("""
            typedef struct {
                long x;
                long y;
            } POINT;

            typedef struct {
                long left;
                long top;
                long right;
                long bottom;
            } RECT;
            
            long left, top, right, bottom;

            RECT ReturnRect(int i, RECT ar, RECT* br, POINT cp, RECT dr,
                        RECT *er, POINT fp, RECT gr);
        """)
        ownlib = ffi.dlopen(self.module)

        rect = ffi.new('RECT[1]')
        pt = ffi.new('POINT[1]')
        pt[0].x = 15
        pt[0].y = 25
        rect[0].left = ownlib.left
        rect[0].right = ownlib.right
        rect[0].top = ownlib.top
        rect[0].bottom = ownlib.bottom
        
        for i in range(4):
            ret = ownlib.ReturnRect(i, rect[0], rect, pt[0], rect[0],
                                    rect, pt[0], rect[0])
            assert ret.left == ownlib.left
            assert ret.right == ownlib.right
            assert ret.top == ownlib.top
            assert ret.bottom == ownlib.bottom