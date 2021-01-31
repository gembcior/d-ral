from Constant import TEMPLATES_PATH
import os
import re

class Object:
    def __init__(self):
        self._template = None

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
        return string

    def _get_pattern_substitution(self, pattern):
        return None

    def _generate(self, template):
        content = []
        template_file = os.path.join(TEMPLATES_PATH, template)
        dral_pattern = re.compile('\[dral\](.*?)\[#dral\]', flags=(re.MULTILINE | re.DOTALL))
        with open(template_file,"r") as template:
            for line in template.readlines():
                for pattern in re.findall(dral_pattern, line):
                    substitution = self._get_pattern_substitution(pattern)
                    if substitution is not None:
                        line = re.sub("\[dral\]%s\[#dral\]" % pattern, substitution, line, flags=(re.MULTILINE | re.DOTALL))
                content.append(line)
        return "".join(content)

    def get_string(self):
        content = self._generate(self._template)
        return content

