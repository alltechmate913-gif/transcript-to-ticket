"""Common extraction/redaction patterns for the supported identifier formats.

These recognize syntax, not whether a mailbox, phone or ticket actually exists.
"""

import re


TICKET = re.compile(r"(?<![\w.-])T[0-9]{8}\.[0-9]{4}(?!\w|\.[0-9])", re.IGNORECASE)

# ASCII dot-atom mailboxes and DNS domains, including hyphenated subdomains.
# Boundaries prevent extracting a plausible suffix of a malformed address.
_ATOM = r"[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+"
_LABEL = r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
EMAIL = re.compile(
    rf"(?<![\w.!#$%&'*+/=?^`{{|}}~@-]){_ATOM}(?:\.{_ATOM})*"
    rf"@(?:{_LABEL}\.)+[a-zA-Z]{{2,63}}(?![\w@-]|\.[\w.-])"
)

# North American numbers; parentheses must balance. Retain the original format,
# including the country code and optional extension, for display/redaction.
PHONE = re.compile(
    r"(?<![\w+(.-])(?:\+?1[ .-]?)?"
    r"(?:\([0-9]{3}\)[ .-]?|[0-9]{3}[ .-]?)"
    r"[0-9]{3}[ .-]?[0-9]{4}"
    r"(?:[ \t]*(?:ext\.?|x|extension)[ \t]*[0-9]+)?"
    r"(?![\w)]|[.-][0-9])",
    re.IGNORECASE,
)
