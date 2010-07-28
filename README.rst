DarkLight
=========

DarkLight is a simple, straightforward, line-based protocol for transferring
files. It is distinguished by a novel implementation that is effectively
invisible to IP-based filters, rendering it unfilterable and unblockable by
normal means.

Usage
-----

Bug Corbin about making a proper setup.py and filling in this section.

Bugs
----

The implementation is not yet robust enough to identify individual bugs.
Assume everything is broken. This is only a proof-of-concept tree.

Additionally, as covered in the documentation, there may be bugs in the
underlying protocol.

To Do
-----

This list is largely just for Corbin, because the license isn't clear yet!

Fix the license. For good. Either MIT/X11 or GPL3. The former might be better
since it'd be nice to be in Twisted someday.

The GUI needs to be finished.

Search needs to be added back to the protocol. This depends on privs.

We need privs for users. At least search needs to be a special priv beyond
basic login rights.
