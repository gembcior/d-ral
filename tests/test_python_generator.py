# =================================================================================
#
# MIT License
#
# Copyright (c) 2026 Gembcior
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# =================================================================================

from __future__ import annotations

from dral.core.generator import MultiOutputGenerator
from dral.core.objects import DralAccessType, DralDevice, DralGroup, DralGroupInstance, DralRegister
from dral.utils.utils import Utils

RW = DralAccessType.ReadWrite
UINT32 = "uint32_t"


def _non_uniform_offset_device() -> DralDevice:
    """A device with a group whose instances have non-uniform address strides.

    Regression fixture for the python codegen crash: "0x{:08X}".format(list)
    raised when a group's offset is a list[int] instead of an int.
    """
    group = DralGroup(
        name="Irregular",
        address=0x1000,
        offset=[0, 0x200, 0x700],
        instances=[
            DralGroupInstance(name="Irregular_0", address=0x1000),
            DralGroupInstance(name="Irregular_1", address=0x1200),
            DralGroupInstance(name="Irregular_2", address=0x1700),
        ],
        groups=[],
        registers=[DralRegister(name="Ctrl", address=0, size=32, access=RW, value_type=UINT32, fields=[])],
    )
    return DralDevice(name="Dev", groups=[group])


def test_python_main_template_renders_non_uniform_offset_group() -> None:
    device = _non_uniform_offset_device()
    generator = MultiOutputGenerator(template_dir=[Utils.get_template_dir("python")])

    output = generator.generate("main.jinja", device)

    assert len(output) == 1
    content = output[0].content
    assert "dral.group(" in content
    # non-uniform offset must render as a list literal, not crash the format spec
    assert "[0x00000000, 0x00000200, 0x00000700]" in content
