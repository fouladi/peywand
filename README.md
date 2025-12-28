# peywand

A terminal tool (command line) for managing bookmarks

# Background

I use many different laptops and PCs for work and private. So in the
past I saved my bookmarks in different places. At some point I came up
with the idea that I could save all links to a file in my Git repo.
After that I only have to maintain this file.

To simplify the maintenance of this file I began to implement this tool.
And this is so `peywand` was born and it started growing. Now I store my
bookmarks not in a file but in a `sqlite` DB.

# Requirements

- python (3.7+)
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

After that you may add, delete and update your bookmarks. For examples
and more information see:

```bash
./peywand.py -h
```

## Meaning

`peywand` is a Persian noun and means: `link`
