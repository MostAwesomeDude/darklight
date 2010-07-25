Configuration
=============

The DarkLight reference server uses classic INI-style configuration files.

Paths in configuration files should be absolute; relative paths work but may
not do what they appear to do.

Cache
-----

The cache section controls the behavior of the builtin piece and hash cache.

size
    The number of bytes that the cache will store. Only pieces count towards
    cache size; hashes are cached as needed and do not contribute
    significantly towards cache usage.
hash-style
    This option controls when the server will examine unhashed files. By
    default, DarkLight enumerates all files in its folders, but waits until
    after the server starts up to hash files, and tries to not block the
    networking machinery. Setting this option to "immediate" forces DL to
    update all hashes before starting network connections.

Database
--------

The database section controls the database that DarkLight uses to remember
files it has seen.

path
    Location of the database file. Must be writeable.

SSL
---

SSL has its own configuration section.

enabled
    Enable SSL tunnelling. If not set, the server will run in pure TCP mode,
    unencrypted.
key
    Path to the SSL server key.
certificate
    Path to the SSL server certificate.
