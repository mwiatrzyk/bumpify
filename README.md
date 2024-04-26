![PyPI - Version](https://img.shields.io/pypi/v/bumpify)
![PyPI - Downloads](https://img.shields.io/pypi/dm/bumpify)
![PyPI - License](https://img.shields.io/pypi/l/bumpify)

# Bumpify

Semantic versioning automation tool for software projects.

## About

Bumpify is a CLI tool that analyzes VCS changelog of your project and generates
next semantic version of it. Despite the fact that the tool is written in
Python, it can be used to automate versioning of any project, written in any
language, and any technology.

Bumpify works with conventional commits, as defined here:

https://www.conventionalcommits.org/en/v1.0.0/

And follows semantic versioning rules that can be found here:

https://semver.org/

## Installation

### Using ``pip``

This is recommended option if you want to use this tool only inside your
virtual Python environment as a development dependency of the project you work
on:

```
$ pip install bumpify
```

### Using ``pipx``

This is recommended option if you want this tool to be available system wide:

```
$ pipx install bumpify
```

## Usage

### Creating initial configuration

Bumpify reads its configuration from a configuration file, that by default will
be created inside project's root directory and named ``.bumpify.toml``.

To create initial configuration for your project, proceed to the root directory
of your project and type:

```
$ bumpify init
```

That command will interactively guide you through the process of creating
initial configuration file.

Alternatively, you can also take a look at config file that Bumpify itself is
using:

https://github.com/mwiatrzyk/bumpify/blob/main/.bumpify.toml

Yes, Bumpify is also versioned with Bumpify :-)

### Create a new version

Once the project is configured, you can start using the tool. To bump the
version and create new release just run following command:

```
$ bumpify bump
```

The ``bump`` command will, among other things, do following:

1. Check if version tags are present.
2. Create initial version in no version tags are found.
3. Create next version if version tags are found. The new version is calculated
   by analyzing VCS changelog between last version and VCS repository HEAD.
   Only **conventional commits** are currently taken into account, all other
   formats are ignored.
4. Write new version to all configured **version files**.
5. Create or update all configured **changelog files**.
6. Create so called **bump commit** and add all modified files to it.
7. Tag the bump commit with a **version tag**.

Bumpify will not push the commit and the tag to the upstream; you will have to
do it on your own, as this is out of scope of Bumpify.

I strongly recommend calling ``bumpify bump`` from one of the final CI steps of
your project.

## Glossary

### Conventional commit

A normalized format of a commit message that can be later parsed by tools like
Bumpify and interpreted accordingly.

Here's an example:

    feat: add support for Markdown changelog

Thanks to conventional commits Bumpify knows what changes are breaking changes,
what are new features, and what are bug fixes. Based on that the tool can
calculate next version and generate changelog.

Check here for more details:

https://www.conventionalcommits.org/en/v1.0.0/

### Version file

Project's file containing project's version string. Version files are used to
store project's version value, which must be adjusted on each version bump.
There can be several such files inside a project and all should be known to
Bumpify to avoid version integrity problems.

### Changelog file

The file with release history of the project.

It is automatically created or updated on each version bump. Bumpify can create
several changelog files, with different formats.

Currently supported changelog file formats are Markdown and JSON.

### Bump commit

A commit created once version was bumped with message containing information
about previous and new version. For example:

```
bump: 0.1.0 -> 0.2.0
```

The format of a bump commit can be changed in the config file.

### Version tag

Each bump commit is tagged with a version tag. For example:

```
v1.2.3
```

The format of this tag can be changed in the config file.

## License

The project is licensed under the terms of the MIT license.

## Author

Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
