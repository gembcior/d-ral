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

import pytest

from dral.utils.name import DralName, DralNameError, lower_camel_case, upper_camel_case


class TestUtils:
    @pytest.mark.parametrize(
        "word, expected",
        [
            ("test_word", "TestWord"),
            ("another_test", "AnotherTest"),
            ("example_name", "ExampleName"),
            ("simple", "Simple"),
            ("alreadyCamelCase", "AlreadyCamelCase"),
            ("AlreadyUpperCamelCase", "AlreadyUpperCamelCase"),
            ("123number", "123Number"),
            ("_leading_underscore", "LeadingUnderscore"),
            ("trailing_underscore_", "TrailingUnderscore"),
            ("_both_underscores_", "BothUnderscores"),
            ("with spaces", "WithSpaces"),
            ("with-special-characters!", "WithSpecialCharacters!"),
            ("", ""),
            ("-", ""),
            ("singleword", "Singleword"),
            ("123", "123"),
            ("_underscore", "Underscore"),
            ("__double_underscore__", "DoubleUnderscore"),
            ("mixed123case", "Mixed123Case"),
            ("UPPERCASE", "Uppercase"),
            ("HTTPServer", "Httpserver"),
        ],
    )
    def test_upper_camel_case(self, word: str, expected: str) -> None:
        result = upper_camel_case(word)
        assert result == expected, f"Expected '{expected}', but got '{result}' for input '{word}'"

    @pytest.mark.parametrize(
        "word, expected",
        [
            ("test_word", "testWord"),
            ("another_test", "anotherTest"),
            ("example_name", "exampleName"),
            ("simple", "simple"),
            ("alreadyCamelCase", "alreadyCamelCase"),
            ("AlreadyUpperCamelCase", "alreadyUpperCamelCase"),
            ("123number", "123Number"),
            ("_leading_underscore", "leadingUnderscore"),
            ("trailing_underscore_", "trailingUnderscore"),
            ("_both_underscores_", "bothUnderscores"),
            ("with spaces", "withSpaces"),
            ("with-special-characters!", "withSpecialCharacters!"),
            ("", ""),
            ("-", ""),
            ("singleword", "singleword"),
            ("123", "123"),
            ("_underscore", "underscore"),
            ("__double_underscore__", "doubleUnderscore"),
            ("mixed123case", "mixed123Case"),
            ("UPPERCASE", "uppercase"),
            ("HTTPServer", "httpserver"),
        ],
    )
    def test_lower_camel_case(self, word: str, expected: str) -> None:
        result = lower_camel_case(word)
        assert result == expected, f"Expected '{expected}', but got '{result}' for input '{word}'"

    @pytest.mark.parametrize(
        "name_a, name_b, expected",
        [
            ("test", "test", True),
            ("test1", "test2", True),
            ("test_case", "testCase", True),
            ("TestCase", "test_case", True),
            ("example_name", "exampleName", True),
            ("simple_test", "simpleTest", True),
            ("alreadyCamelCase", "AlreadyCamelCase", True),
            ("123number", "123Number", True),
            ("different_case", "DIFFERENT_CASE", True),
            ("mixed123case", "Mixed123Case", True),
            ("foo", "bar", False),
            ("gpioA", "spiB", False),
            ("gpioA", "gpioB", True),
            ("gpioA", "gpioA", True),
            ("gpioA1", "gpioA2", True),
            ("gpioA1", "gpioB1", True),
            ("GPIO_A1", "GPIO_A2", True),
            ("GPIO_A1", "GPIO_B1", True),
            ("Ctr01Enable", "Ctr01Disable", False),
            ("Ctr01Enable", "Ctr02Enable", True),
            ("IBout", "ICout", True),
        ],
    )
    def test_is_similar_name(self, name_a: str, name_b: str, expected: bool) -> None:
        result = DralName.is_similar_name(name_a, name_b)
        assert result == expected, f"Expected '{expected}', but got '{result}' for names '{name_a}' and '{name_b}'"

    @pytest.mark.parametrize(
        "namelist, expected",
        [
            (["test", "test1"], "test_x"),
            (["test1", "test2"], "test_x"),
            (["test", "test1", "test2"], "test_x"),
            (["gpioA", "gpioB"], "gpio_x"),
            (["gpioA1", "gpioA2"], "gpioA_x"),
            (["gpioA1", "gpioB1"], "gpio_x"),
            (["GPIO_A1", "GPIO_A2"], "GPIO_A_x"),
            (["GPIO_A1", "GPIO_B1"], "GPIO_x"),
            (["Ctr01Enable", "Ctr02Enable"], "Ctr_x_Enable"),
            (["IBout", "ICout"], "I_x_out"),
            (["i2cA", "i2cB", "i2cD"], "i2c_x"),
            (["spiA", "SPIB", "sPiC"], "SPI_x"),  # Sneaky example with mixed case. What to do with base name?
            (["TIMER0", "TIMER1", "TIMER2"], "TIMER_x"),
        ],
    )
    def test_get_common_name(self, namelist: list[str], expected: str) -> None:
        dral_name = DralName(namelist)
        result = dral_name.get_common_name()
        assert result == expected, f"Expected '{expected}', but got '{result}' for namelist {namelist}"

    @pytest.mark.parametrize(
        "namelist",
        [
            ["GpioC", "GpioC"],
            ["gpioA", "gpioA", "gpioC"],
            ["gpioA1", "gpioA1", "gpioC1"],
            ["GPIO_A1", "GPIO_A1", "GPIO_C1"],
            ["Ctr01Enable", "Ctr01Enable", "Ctr02Enable"],
            ["IBout", "ICout", "IBout"],
            ["I2C1", "SPI1", "UART1"],
        ],
    )
    def test_calculate_common_name_error(self, namelist: list[str]) -> None:
        with pytest.raises(DralNameError):
            DralName(namelist)

    @pytest.mark.parametrize(
        "namelist, expected",
        [
            (["test", "test1"], "test"),
            (["test1", "test2"], "test"),
            (["test", "test1", "test2"], "test"),
            (["gpioA", "gpioB"], "gpio"),
            (["gpioA1", "gpioA2"], "gpioA"),
            (["gpioA1", "gpioB1"], "gpio"),
            (["GPIO_A1", "GPIO_A2"], "GPIO_A"),
            (["GPIO_A1", "GPIO_B1"], "GPIO"),
            (["Ctr01Enable", "Ctr02Enable"], "Ctr_Enable"),
            (["IBout", "ICout"], "I_out"),
            (["i2cA", "i2cB", "i2cD"], "i2c"),
            (["spiA", "SPIB", "sPiC"], "SPI"),  # Sneaky example with mixed case. What to do with base name?
            (["TIMER0", "TIMER1", "TIMER2"], "TIMER"),
        ],
    )
    def test_get_register_name(self, namelist: list[str], expected: str) -> None:
        dral_name = DralName(namelist)
        result = dral_name.get_register_name()
        assert result == expected, f"Expected '{expected}', but got '{result}' for namelist {namelist}"

    @pytest.mark.parametrize(
        "namelist, instance, expected",
        [
            (["test", "test1"], "test1", "test_1"),
            (["test1", "test2"], "test2", "test_2"),
            (["test", "test1", "test2"], "test1", "test_1"),
            (["gpioA", "gpioB"], "gpioA", "gpio_A"),
            (["gpioA1", "gpioA2"], "gpioA1", "gpioA_1"),
            (["gpioA1", "gpioB1"], "gpioB1", "gpio_B1"),
            (["GPIO_A1", "GPIO_A2"], "GPIO_A1", "GPIO_A_1"),
            (["GPIO_A1", "GPIO_B1"], "GPIO_B1", "GPIO_B1"),
            (["Ctr01Enable", "Ctr02Enable"], "Ctr01Enable", "Ctr_01_Enable"),
            (["IBout", "ICout"], "ICout", "I_C_out"),
            (["i2cA", "i2cB", "i2cD"], "i2cD", "i2c_D"),
            (["spiA", "SPIB", "sPiC"], "sPiC", "sPi_C"),  # Sneaky example with mixed case. What to do with base name?
            (["TIMER0", "TIMER1", "TIMER2"], "TIMER0", "TIMER_0"),
        ],
    )
    def test_get_instance_name(self, namelist: list[str], instance: str, expected: str) -> None:
        dral_name = DralName(namelist)
        result = dral_name.get_instance_name(instance)
        assert result == expected, f"Expected '{expected}', but got '{result}' for instance '{instance}' in namelist {namelist}"
