.. include:: <isonum.txt>

Darklight Protocol v1

|copy| Corbin Simpson, 2008-10

:Author: Corbin Simpson
:Version: v0

This document is in the public domain, to the extent that it is legally
permitted.

In this document, "Darklight" may be abbreviated "DL."

Changelog
=========

Feb 08, 2009: Major revision v1.

 * Remove search functionality
 * Divide commands into server- and client-side groups
 * Change hash definition.

Jul 10, 2010: Major revision v0.

 * Rewind version number to prerelease, indicating unstable API.

Introduction
============

Darklight is a layer seven protocol, although it is intended to subsume layers
seven through five cleanly and seamlessly. Its design is modeled loosely on
some of the modern-day brightnet tools used for communication, most notably
HTTP/SSL, Direct Connect, and Bittorrent, although out of all of those, only
HTTP bears any resemblance to the actual wire protocol of Darklight.

Darklight's purpose is to provide a cryptographically impenetrable system for
transferring files of indeterminate size and contents. To this end, the
protocol has been designed to be secure while also being somewhat
distributable and invisible.

Abbreviations
=============

DL
    Darklight.

On-the-wire Commands
====================

<> are required parameters, [] are optional. All commands and parameters
are space-delimited except where otherwise noted, and terminate with a
carriage return and line feed (\\r\\n).

Client Commands
---------------

All of the following may only be issued by clients. Reply: fields denote
replies which the server should issue upon success.

CHECKAPI

 * This command allows a client to retrieve the version of the on-the-wire
   protocol that the server uses.
 * Reply: API

HAI [challenge]

 * This command authenticates a client with a server, using the challenge hash
   described in `Hashes`.
 * Servers may not require [challenge] but are allowed to deny
   authentication in that case.
 * If an authentication is unsuccessful, the server's reply is undefined.
   Servers are encouraged to remain completely silent and remain in
   passthrough mode if possible.
 * Reply: OHAI

KTHNXBAI

 * This command is sent by a client to notify the server that it intends to
   close the connection. Clients should wait for the server to respond, but
   they are allowed to terminate the connection after sending this.
 * Reply: BAI

SENDTTH <hash>

 * This command requests the immediate children of the <hash>. The server will
   reply with 0, 1, or 2 children, space-separated.
 * Reply: K

SENDPEZE <hash> <size> <piece>

 * This command requests the <piece> from the file identified by <hash> and
   <size>.
 * Reply: K

VERSION

 * This command prompts the server to respond with an unformatted reply.  The
   server should reply with a single line describing its version and vendor,
   although there are no requirements for the reply.

Server Replies
--------------

API <protocol version>

 * This reply contains the protocol version to which the server should
   conform.

BAI

 * This reply indicates that the connection is safe to close, and that the
   server will no longer listen on this connection.

FAIL

 * This reply indicates an internal server error while handling the client's
   request. The server is permitted to terminate the connection with no
   further warning.

K <count>

 * This reply indicates that the server is about to respond with <count>
   bytes of data, terminated with a full newline. The data sent depends on
   the previous request.

LOLWUT

 * This response indicates that the server does not understand the previous
   command. The server may close the connection.

OHAI

 * This reply is sent by the server to notify the client that authentication
   was successful.

Hashes
======

On the wire, hashes should generally be either unencoded, or base32-encoded.
The only encodings servers are required to support are raw (unencoded),
base32-encoded, and base16-encoded (ASCII hexadecimal).

Challenges
----------

The challenge hash is used by clients to authenticate with servers. The
challenge should be a hash of the client's password. The hash is defined as
the Whirlpool HMAC with the password as the pre-shared key and the ASCII
representation of the UTC day of the month plus 42, as the password. More
tersely, with W as the Whirlpool HMAC, the challenge is W(password, (day of
the month UTC + 42)).

TTH
---

For file hashes, the Tiger Tree Hash is used. THEX-style TTHs are currently
used, although other block sizes might be added later.
