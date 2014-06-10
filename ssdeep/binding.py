import binascii

from cffi import FFI

from ssdeep.__about__ import __version__

cdef = """
    static const long FUZZY_FLAG_ELIMSEQ;
    static const long FUZZY_FLAG_NOTRUNC;
    static const long FUZZY_MAX_RESULT;

    struct fuzzy_state;
    struct fuzzy_state *fuzzy_new(void);
    int fuzzy_update(
        struct fuzzy_state *,
        const unsigned char *,
        size_t
    );

    int fuzzy_digest(
        const struct fuzzy_state *,
        char *,
        unsigned int
    );
    void fuzzy_free(struct fuzzy_state *);

    int fuzzy_hash_buf(
        const unsigned char *,
        uint32_t,
        char *
    );

    int fuzzy_hash_file(
        FILE *,
        char *
    );

    int fuzzy_hash_stream(
        FILE *,
        char *
    );

    int fuzzy_hash_filename(
        const char *,
        char *
    );

    int fuzzy_compare(
        const char *,
        const char *
    );
"""

source = """
    #include "fuzzy.h"
"""


class Binding(object):
    def __init__(self, extra_objects=None, include_dirs=None, libraries=None):
        self.ffi = FFI()
        self.ffi.cdef(cdef)
        self._lib = None
        if extra_objects is None:
            extra_objects = []
        self._extra_objects = extra_objects
        if include_dirs is None:
            include_dirs = []
        self._include_dirs = include_dirs
        if libraries is None:
            libraries = ["fuzzy"]
        self._libraries = libraries

    def verify(self):
        self._lib = self.ffi.verify(
            source,
            ext_package="ssdeep",
            extra_objects=self._extra_objects,
            include_dirs=self._include_dirs,
            modulename=_create_modulename(cdef, source, __version__),
            libraries=self._libraries,
        )

    @property
    def lib(self):
        if self._lib is None:
            self.verify()
        return self._lib


def _create_modulename(cdef, source, sys_version):
    key = "\x00".join([sys_version[:3], source, cdef])
    key = key.encode("utf-8")
    k1 = hex(binascii.crc32(key[0::2]) & 0xffffffff)
    k1 = k1.lstrip("0x").rstrip("L")
    k2 = hex(binascii.crc32(key[1::2]) & 0xffffffff)
    k2 = k2.lstrip("0").rstrip("L")
    return "_ssdeep_cffi_{0}{1}".format(k1, k2)
