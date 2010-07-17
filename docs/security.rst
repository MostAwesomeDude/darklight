Security
========

DarkLight is meant to be secure and invisible above all other concerns. Are
those goals actually achieved?

Hashes
------

Hashing needs to be computationally expensive to the point where a brute-force
attack is infeasible. Simple tests confirm that the CPython implementations of
Whirlpool can run approximately 56000 hashes/second on commodity hardware, and
the Whirlpool HMAC can be calculated approximately 8000 times/second if
continuously rekeyed. While the hardware in question is quite poor, this is
definitely slow enough that even if sped up by several factors, it would not
yield any useful attacks.

Further complicating the brute-force problem is network latency. Confirmation
of the HMAC is very quick, but DarkLight servers are permitted to do anything
they like in the case of an incorrect HMAC. For example, servers may
intentionally delay any response to a failed challenge by around, but not
exactly, half a second. This small delay, while invisible to the user, would
completely frustrate an attacker working on a LAN next to the targeted
server.

However, HMACs are vulnerable to a variety of replay attacks. Passthrough mode
is the primary way of addressing this problem, although the server's forced
daily rekeying helps as well.

Passthrough
-----------

Passthrough mode is the main technique DarkLight uses to become invisible to
packet sniffers. It is based on a few simple observations about encrypted web
traffic.

As a simple thought experiment, consider an HTTPS connection. It starts with
an SSL handshake, creating an impenetrable tunnel that cannot be sniffed
without a man-in-the-middle. Then, regular HTTP commands are sent through the
tunnel. How does one know that the content of the tunnel is HTTP? Well, the
connection was established on the standard HTTPS port 443, so it must be HTTP.
But what if it isn't?

DarkLight's passthrough mode is simple. DarkLight itself binds to a
secure-tunnel-based port, such as 443 for HTTPS, and provides the
cryptographic tools necessary for starting the connection. However, it does
not actually provide the inner protocol necessary for the connection; instead,
DarkLight passes through all input and output to a local program running on a
different port, or perhaps on a socket. For HTTPS, it might pass through to an
HTTP server running on port 80. This simple trick provides the illusion that
the HTTP server on port 80 is also in control of port 443.

DarkLight servers choose to exit passthrough mode when they receive a valid
challenge, properly formatted, as part of their input. Up until that point,
DarkLight passes through all of its input and output, so invalid challenges
will provoke predictable and uninteresting output from the HTTP server without
DarkLight revealing its presence.

Known Problems
--------------

DarkLight does have some issues. The largest issue evident to the author is
the obvious replay attack possible when a man-in-the-middle attack is
performed on the initial encrypted tunnel. The MITM has the ability to record
correct challenges and save them for reuse later in the same keying period.
The author's solution is to require encryption certificate fingerprints, or
entire certificates, to be verified and protected by clients just like the
pre-shared keys used to generate the challenge. This would prevent
man-in-the-middle attacks by forbidding connections to unknown servers.
