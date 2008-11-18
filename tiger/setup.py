#!/usr/bin/env python

from distutils.core import setup, Extension

tigersources = ['sboxes.c', 'tiger.c', 'tigermodule.c']

tiger = Extension("tiger", sources = tigersources, extra_compile_args=['-O3'])

setup(name = "tiger", version = "0.2", description = "Tiger hash module",
	ext_modules = [tiger])
