# Installing Redlands Bindings on macOS

The [Redland bindings](http://librdf.org/bindings/) can be harder to install than most Python packages.
Specifically, you won't find pre-built wheels on [PyPi](https://pypi.org/), you have to install it from source, and you may run into linker issues.

The [installation instruction](http://librdf.org/bindings/INSTALL.html) work fine under various Linux distros and only need minimal tweaking on macOS w/ Homebrew's `python@3.x` formulae but won't work out of the box with [pyenv](https://github.com/pyenv/pyenv) Pythons.

Here's how to make that work:

## Dependencies

You at least need `autoconf` and `automake`, XCode CLT, etc.

## autogen.sh

`autogen.sh` has an issue detecting the version of `libtoolize` so, first, edit line 84 in `autogen.sh` to remove the constraint:

```
libtoolize_min_vers=000000
```

Then help `autogen.sh` find `libtoolize` by providing the absolute path in an environment variable. Note: Homebrew `libtoolize` is at `glibtoolize`:

```
LIBTOOLIZE=/usr/local/bin/glibtoolize ./autogen.sh
```

## ./configure

When running `./configure`, I found I needed to specify my Python binary directly and not by letting it guess or through a pyenv symlink:

```
./configure --with-python=/Users/me/.pyenv/versions/3.9.2/bin/python3
```

This will run but `make` will fail during linking complaining about undefined symnbols. See the next section.

If it succeeds, you should see python listed under "Language APIs built":

```
Redland build summary:
  Redland:              1.0.17
  Language APIs built:    python
```

## pyenv doesn't install Python.framework

It turns out that pyenv doesn't install a `Python.framework` folder like Homebrew does and you have to have this.

First, uninstall the version of Python you want to use and re-install with:

```
PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install -v 3.9.2
```

Then, tweak the linker flags in the Python-specific Makefile (`python/Makefile`).
Change the value from:

```
PYTHON_LDFLAGS = -Wl,-F. -Wl,-F. -bundle
```

to

```
PYTHON_LDFLAGS = -Wl,-F. -Wl,-F. -bundle -F/Users/me/.pyenv/versions/3.9.2 -framework Python
```

You might have to clean up first, I'm not sure:

```
make clean
rm -f config.cache
```

Then run:

```
make # should run
make install
```
