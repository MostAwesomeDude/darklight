Darklight Protocol v1

(c) Corbin Simpson, 2008-09

This document is available under the terms of the GPL v2; see the 
attached LICENSE file for details.

In this document, "Darklight" may be abbreviated "DL."

Feb 08, 2009: Major revision v1. Remove search functionality, divide
   remaining commands into server- and client-side groups, change hash
   definition.

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
distributable and hideable.

On-the-wire Commands
====================

<> are required parameters, [] are optional. All commands and parameters 
are space-delimited except where otherwise noted, and terminate with a 
carriage return and line feed (\r\n).

Client Commands
---------------

All of the following may only be issued by clients. Reply: fields denote
replies which the server should issue upon success.

CHECKAPI

 * This command allows a client to retrieve the version of the on-the-wire
   protocol that the server uses.
 * Reply: API

HAI [challenge]

 * This command authenticates a client with a server. [challenge] should be a
   hash of the client's password, decided as follows:
        Let W(plaintext, iterations) be the Whirlpool hash function. The 
        hash is defined as:
            hash = W(password, (day of the month UTC + 42))
   Servers may not require [challenge] but are allowed to deny
   authentication in that case. If an authentication is unsuccessful,
   the server's reply is undefined.
 * Reply: OHAI

KTHNXBAI

 * This command is sent by a client to notify the server that it intends to
   close the connection. Clients should wait for the server to respond, but
   they are allowed to terminate the connection after sending this.
 * Reply: BAI

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
