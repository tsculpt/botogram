"""
    botogram.utils
    Utilities used by the rest of the code

    Copyright (c) 2015 Pietro Albini <pietro@pietroalbini.io>
    Released under the MIT license
"""

import re
import os
import sys
import gettext

import pkg_resources
import logbook
import functools

_username_re = re.compile(r"\@([a-zA-Z0-9_]{5}[a-zA-Z0-9_]*)")
_command_re = re.compile(r"^\/[a-zA-Z0-9_]+(\@[a-zA-Z0-9_]{5}[a-zA-Z0-9_]*)?$")
_email_re = re.compile(r"[a-zA-Z0-9_\.\+\-]+\@[a-zA-Z0-9_\.\-]+\.[a-zA-Z]+")

_markdown_re = re.compile(r"(\*(.*)\*|_(.*)_|\[(.*)\]\((.*)\)|`(.*)`|"
                          r"```(.*)```)")

# This small piece of global state will track if logbook was configured
_logger_configured = False


def wraps(func):
    """Update a wrapper function to looks like the wrapped one"""
    # Custom implementation of functools.wraps
    # Needed because copying __dict__ causes some trouble with the pass_*
    # decorators. Except for this it's the same
    return functools.partial(functools.update_wrapper, wrapped=func,
                             assigned=functools.WRAPPER_ASSIGNMENTS,
                             updated=tuple())  # DON'T COPY __dict__


def format_docstr(docstring):
    """Prepare a docstring for /help"""
    result = []
    for line in docstring.split("\n"):
        stripped = line.strip()

        # Allow only a blank line
        if stripped == "" and len(result) and result[-1] == "":
            continue

        result.append(line.strip())

    # Remove empty lines at the end or at the start of the docstring
    for pos in 0, -1:
        if result[pos] == "":
            result.pop(pos)

    return "\n".join(result)


def docstring_of(func, bot=None):
    """Get the docstring of a function"""
    # Custom docstring
    if hasattr(func, "botogram") and func.botogram.help_message:
        if bot is not None:
            docstring = bot._call(func.botogram.help_message)
        else:
            docstring = func.botogram.help_message()
    # Standard default docstring
    elif func.__doc__:
        docstring = func.__doc__
    # Put a default message
    else:
        if bot is not None:
            docstring = bot._("No description available.")
        else:
            docstring = "No description available."

    return format_docstr(docstring)


def usernames_in(message):
    """Return all the matched usernames in the message"""
    # Don't parse usernames in the commands
    if _command_re.match(message.split(" ", 1)[0]):
        message = message.split(" ", 1)[1]

    # Strip email addresses from the message, in order to avoid matching the
    # user's domain. This also happens to match username/passwords in URLs
    message = _email_re.sub("", message)

    results = []
    for result in _username_re.finditer(message):
        if result.group(1):
            results.append(result.group(1))

    return results


def is_markdown(string):
    """Check if a string is actually markdown"""
    return bool(_markdown_re.match(string))


def get_language(lang):
    """Get the GNUTranslations instance of a specific language"""
    path = pkg_resources.resource_filename("botogram", "i18n/%s.mo" % lang)
    if not os.path.exists(path):
        raise ValueError('Language "%s" is not supported by botogram' % lang)

    with open(path, "rb") as f:
        gt = gettext.GNUTranslations(f)

    return gt


def configure_logger():
    """Configure a logger object"""
    global _logger_configured

    # Don't configure the logger multiple times
    if _logger_configured:
        return

    # The StreamHandler will log everything to stdout
    min_level = 'DEBUG' if 'BOTOGRAM_DEBUG' in os.environ else 'INFO'
    handler = logbook.StreamHandler(sys.stdout, level=min_level)
    handler.format_string = '{record.time.hour:0>2}:{record.time.minute:0>2}' \
                            '.{record.time.second:0>2} - ' \
                            '{record.level_name:^9} - {record.message}'
    handler.push_application()

    # Don't reconfigure the logger, thanks
    _logger_configured = True


class HookDetails:
    """Container for some details of user-provided hooks"""

    def __init__(self, func):
        self._func = func
        self.name = ""
        self.component = None
        self.pass_args = {}
        self.help_message = None

    def _default_help_message(self):
        return format_docstr(self._func.__doc__)
