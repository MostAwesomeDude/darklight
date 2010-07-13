Configuration
=============

Darklight servers support a single configuration file with a simple,
straightforward syntax.

Required Settings
-----------------

Directories to index are specified with the FOLDER command.

Syntax: FOLDER <directory>

The path to the file database is specified with the DB command.

Syntax: DB <file>

Optional Settings
-----------------

The CACHE command may be used to force the server to only store a certain
amount of pieces.

Syntax: CACHE <size>

To force immediate hashing instead of lazy hashing, the HASHSTYLE command may
be used.

Syntax: HASHSTYLE imm

Comments
--------

Lines starting with an octothorpe (#) are ignored and may be used for
comments.
