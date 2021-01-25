class Object:
    def __init__(self):
        pass

    def _get_policy(self, pattern):
        policy = "ERROR"
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
        return "ERROR"

    def generate(self):
        return "ERROR"
