from Constant import TEMPLATES_PATH
import os
import re

class DeviceItem:
    def __init__(self):
        self._template = None
        self._dral_prefix = "\[dral\]"
        self._dral_sufix = "\[#dral\]"
        self._dral_pattern = re.compile(self._dral_prefix + "(.*?)" + self._dral_sufix, flags=(re.MULTILINE | re.DOTALL))

    def _get_policy(self, pattern):
        policy = "POLICY_NOT_SUPPORTED"
        if pattern.lower() == "r":
            policy = "ReadOnly"
        elif pattern.lower() == "w":
            policy = "WriteOnly"
        elif pattern.lower() == "rw":
            policy = "ReadWrite"
        elif pattern.lower() == "rc_w1":
            policy = "ReadWrite"
        elif pattern.lower() == "rc_w0":
            policy = "ReadWrite"
        elif pattern.lower() == "rs":
            policy = "ReadWrite"
        elif pattern.lower() == "rt_w":
            policy = "ReadWrite"
        elif pattern.lower() == "t":
            policy = "WriteOnly"
        return policy

    def _apply_modifier(self, string, modifier):
        if modifier == "uppercase":
            string = string.upper()
        elif modifier == "lowercase":
            string = string.lower()
        elif modifier == "capitalize":
            string == string.capitalize()
        return string

    def _get_substitution(self, pattern):
        return None

    def _get_pattern_substitution(self, pattern):
        modifier = pattern.split("%")
        pattern = modifier[0].split(".")
        if len(modifier) > 1:
            modifier = modifier[1]
        else:
            modifier = None
        substitution = self._get_substitution(pattern)
        if modifier is not None and substitution is not None:
            substitution = self._apply_modifier(substitution, modifier)
        return substitution

    def _generate_from_string(self, string):
        content = []
        for line in string.splitlines(True):
            for pattern in re.findall(self._dral_pattern, line):
                substitution = self._get_pattern_substitution(pattern)
                if substitution is not None:
                    pattern = "%s%s%s" % (self._dral_prefix, pattern ,self._dral_sufix)
                    line = re.sub(pattern, substitution, line, flags=(re.MULTILINE | re.DOTALL))
            content.append(line)
        return "".join(content)

    def _generate_from_template(self, template):
        content = []
        template_file = os.path.join(TEMPLATES_PATH, template)
        with open(template_file,"r") as template:
            for line in template.readlines():
                for pattern in re.findall(self._dral_pattern, line):
                    substitution = self._get_pattern_substitution(pattern)
                    if substitution is not None:
                        pattern = "%s%s%s" % (self._dral_prefix, pattern ,self._dral_sufix)
                        line = re.sub(pattern, substitution, line, flags=(re.MULTILINE | re.DOTALL))
                content.append(line)
        return "".join(content)

    def get_string(self):
        content = self._generate_from_template(self._template)
        content = self._generate_from_string(content)
        return content

