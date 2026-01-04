# Peywand

A terminal tool (command line) for managing bookmarks.

**Peywand** is a command-line application for managing bookmarks stored
in a local `SQLite` database. It supports adding, listing, updating,
deleting, importing, and exporting bookmarks in multiple formats via a
**plugin-based I/O architecture**.

# Background

I use many different laptops and PCs for work and personal use. In the
past, I saved my bookmarks in different places. At some point, I had the
idea to save all my links to a file in my Git repository. After that, I
would only have to maintain this file.

To simplify maintenance of the file, I began implementing this tool.
That's how `paywand` was born, and it started growing. Now, I store my
bookmarks in an `SQLite` database, not a file.

# Requirements

- python (3.10+)
- pip

# Installation

You can install *peywand* by using `pip`. Change to the directory
*peywand* and after installation of `virtualenv` run:

```bash
pip install -r requirements.txt
```

# Usage

First of all you have to initialize your database:

```bash
./peywand.py init
```

After that you may add, delete and update your bookmarks.

For examples to see all links with word *wind* in them:

![alt text](doc/images/peywand_list.gif)

For more information see:

```bash
./peywand.py -h
```

## Meaning

`peywand` is a Persian noun and means: `link`
