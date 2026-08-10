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

from dral.utils.name import (
    DralName,
    DralNameError,
    decapitalize,
    lower_camel_case,
    to_snake_case,
    to_snake_case_advance,
    upper_camel_case,
)


class TestDecapitalize:
    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("TestName", "testName"),
            ("ALLCAPS", "aLLCAPS"),
            ("lowercase", "lowercase"),
            ("T", "t"),
            ("A", "a"),
            ("", ""),
            ("MixedCase", "mixedCase"),
            ("XMLParser", "xMLParser"),
        ],
    )
    def test_decapitalize(self, input_str: str, expected: str) -> None:
        assert decapitalize(input_str) == expected


class TestUpperCamelCase:
    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("test_name", "TestName"),
            ("test_name_123", "TestName123"),
            ("test_123_name", "Test123Name"),
            ("test_123_name_456", "Test123Name456"),
            ("simple", "Simple"),
            ("a", "A"),
            ("", ""),
            ("already_camel", "AlreadyCamel"),
            ("with_many_words", "WithManyWords"),
            ("number_42_test", "Number42Test"),
        ],
    )
    def test_upper_camel_case(self, input_str: str, expected: str) -> None:
        assert upper_camel_case(input_str) == expected


class TestLowerCamelCase:
    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("test_name", "testName"),
            ("test_name_123", "testName123"),
            ("test_123_name", "test123Name"),
            ("test_123_name_456", "test123Name456"),
            ("simple", "simple"),
            ("a", "a"),
            ("already_camel", "alreadyCamel"),
            ("with_many_words", "withManyWords"),
            ("number_42_test", "number42Test"),
        ],
    )
    def test_lower_camel_case(self, input_str: str, expected: str) -> None:
        assert lower_camel_case(input_str) == expected

    def test_lower_camel_case_empty_string(self) -> None:
        with pytest.raises(IndexError):
            lower_camel_case("")


class TestToSnakeCase:
    @pytest.mark.parametrize(
        "input_text,expected",
        [
            ("already_snake_case", "already_snake_case"),
            ("test_name", "test_name"),
            ("simple_test", "simple_test"),
            ("one", "one"),
            ("hello world", "hello_world"),
            ("test name conversion", "test_name_conversion"),
            ("multiple   spaces   between", "multiple_spaces_between"),
            ("  leading and trailing  ", "leading_and_trailing"),
            ("kebab-case-string", "kebab_case_string"),
            ("test-name", "test_name"),
            ("multi-word-test", "multi_word_test"),
            ("mixed.dot.separator", "mixed_dot_separator"),
            ("path/with/slashes", "path_with_slashes"),
            ("name@with#special$chars", "name_with_special_chars"),
            ("test-name_mixed.separators", "test_name_mixed_separators"),
            ("test 123", "test_123"),
            ("version-2-test", "version_2_test"),
            ("test_123_name", "test_123_name"),
            ("", ""),
            ("A", "a"),
            ("ALLUPPERCASE", "alluppercase"),
            ("lowercase", "lowercase"),
            ("___multiple___underscores___", "multiple_underscores"),
            ("hello!world", "hello_world"),
            ("test@email.com", "test_email_com"),
            ("price$100", "price_100"),
            ("50%discount", "50_discount"),
            ("GPIO Configuration", "gpio_configuration"),
            ("Test Register - Description", "test_register_description"),
            ("Register Name [0x1234]", "register_name_0x1234"),
            ("Bit Field (Read/Write)", "bit_field_read_write"),
        ],
    )
    def test_to_snake_case_basic_functionality(self, input_text: str, expected: str) -> None:
        assert to_snake_case(input_text) == expected

    @pytest.mark.parametrize(
        "input_text,expected",
        [
            ("MyClassName", "my_class_name"),
            ("camelCaseTest", "camel_case_test"),
            ("getHTTPResponse", "get_http_response"),
            ("IOError", "io_error"),
            ("XMLParser", "xml_parser"),
            ("HTMLElement", "html_element"),
            ("test123Name", "test123_name"),
            ("version2Test", "version2_test"),
            ("RGB2YUV", "rgb2yuv"),
            ("Test123Class", "test123_class"),
            ("V2Parser", "v2_parser"),
            ("getHTTP2Response", "get_http2_response"),
            ("HTTPSConnection", "https_connection"),
            ("parseXMLDocument", "parse_xml_document"),
            ("URLParser", "url_parser"),
            ("HTTPSProxy", "https_proxy"),
        ],
    )
    def test_to_snake_case_camelcase(self, input_text: str, expected: str) -> None:
        assert to_snake_case_advance(input_text) == expected

    @pytest.mark.parametrize(
        "input_text,expected",
        [
            ("MY CLASS NAME", "my_class_name"),
            ("TEST NAME", "test_name"),
            ("HELLO WORLD", "hello_world"),
            ("Test-Name", "test_name"),
            ("My.Class.Name", "my_class_name"),
            ("Some Name Here", "some_name_here"),
        ],
    )
    def test_to_snake_case_uppercase_with_separators(self, input_text: str, expected: str) -> None:
        assert to_snake_case(input_text) == expected

    @pytest.mark.parametrize(
        "input_text",
        [
            "test_name",
            "simple_snake_case",
            "with_numbers_123",
            "multiple_words_here",
        ],
    )
    def test_to_snake_case_idempotent(self, input_text: str) -> None:
        once = to_snake_case(input_text)
        twice = to_snake_case(once)
        assert once == twice


class TestDralNameIsSimilar:
    @pytest.mark.parametrize(
        "name_a,name_b,expected",
        [
            ("test_name", "test_name", True),
            ("test_name", "test_name_123", True),
            ("test_name", "test_name_123_name", False),
            ("Tx0", "Tx2", True),
            ("Tx0", "Tx1", True),
            ("Tx9", "Tx10", True),
            ("GpioA", "GpioB", True),
            ("GpioA", "GpioZ", True),
            ("cat", "dog", False),
            ("test", "test", True),
            ("Gpio_0", "Gpio_1", True),
            ("Gpio_0", "Gpio_2", True),
            ("Gpio_10", "Gpio_20", True),
            ("testA", "testB", True),
            ("test1", "test2", True),
            ("Uart0Tx", "Uart1Tx", True),
            ("", "", True),
        ],
    )
    def test_is_similar_name(self, name_a: str, name_b: str, expected: bool) -> None:
        assert DralName.is_similar_name(name_a, name_b) == expected


class TestDralNameInit:
    def test_init_with_valid_similar_names(self) -> None:
        dral_name = DralName(["Tx0", "Tx1", "Tx2"])
        assert dral_name._namelist == ["Tx0", "Tx1", "Tx2"]

    def test_init_with_unsorted_names(self) -> None:
        dral_name = DralName(["Tx2", "Tx0", "Tx1"])
        assert dral_name._namelist == ["Tx0", "Tx1", "Tx2"]

    def test_init_with_validation_disabled_still_needs_similar_names(self) -> None:
        with pytest.raises(DralNameError):
            DralName(["cat", "dog", "mouse"], validate=False)

    def test_init_with_dissimilar_names_raises_error(self) -> None:
        with pytest.raises(DralNameError):
            DralName(["cat", "dog", "mouse"])

    def test_init_with_single_name(self) -> None:
        with pytest.raises(IndexError):
            DralName(["Tx0"])


class TestDralNameGetCommonName:
    @pytest.mark.parametrize(
        "namelist,expected",
        [
            (["Tx0", "Tx1", "Tx2"], "Tx_x"),
            (["GpioA", "GpioB", "GpioC"], "Gpio_x"),
            (["Uart0", "Uart1"], "Uart_x"),
            (["Gpio_0", "Gpio_1", "Gpio_2"], "Gpio_x"),
            (["TestReg0", "TestReg1"], "TestReg_x"),
            (["Port_A", "Port_B"], "Port_x"),
            (["Tx0", "Tx1", "Tx2", "Tx3", "Tx4"], "Tx_x"),
        ],
    )
    def test_get_common_name(self, namelist: list[str], expected: str) -> None:
        dral_name = DralName(namelist)
        assert dral_name.get_common_name() == expected

    def test_get_common_name_with_dissimilar_names_raises_error(self) -> None:
        with pytest.raises(DralNameError):
            dral_name = DralName(["cat", "dog", "mouse"])
            dral_name.get_common_name()


class TestDralNameGetRegisterName:
    @pytest.mark.parametrize(
        "namelist,expected",
        [
            (["Tx0", "Tx1", "Tx2"], "Tx"),
            (["GpioA", "GpioB", "GpioC"], "Gpio"),
            (["Uart0", "Uart1"], "Uart"),
            (["Gpio_0", "Gpio_1", "Gpio_2"], "Gpio"),
            (["TestReg0", "TestReg1"], "TestReg"),
            (["Port_A", "Port_B"], "Port"),
        ],
    )
    def test_get_register_name(self, namelist: list[str], expected: str) -> None:
        dral_name = DralName(namelist)
        assert dral_name.get_register_name() == expected


class TestDralNameGetInstanceName:
    def test_get_instance_name_valid(self) -> None:
        dral_name = DralName(["Tx0", "Tx1", "Tx2"])
        assert dral_name.get_instance_name("Tx0") == "Tx_0"
        assert dral_name.get_instance_name("Tx1") == "Tx_1"
        assert dral_name.get_instance_name("Tx2") == "Tx_2"

    def test_get_instance_name_with_alpha(self) -> None:
        dral_name = DralName(["GpioA", "GpioB", "GpioC"])
        assert dral_name.get_instance_name("GpioA") == "Gpio_A"
        assert dral_name.get_instance_name("GpioB") == "Gpio_B"

    def test_get_instance_name_invalid_raises_error(self) -> None:
        dral_name = DralName(["Tx0", "Tx1", "Tx2"])
        with pytest.raises(DralNameError):
            dral_name.get_instance_name("Tx99")

    def test_get_instance_name_with_underscores(self) -> None:
        dral_name = DralName(["Port_A", "Port_B"])
        assert dral_name.get_instance_name("Port_A") == "Port_A"
        assert dral_name.get_instance_name("Port_B") == "Port_B"


class TestDralNameGetDuplicatedGroupName:
    def test_get_duplicated_group_name(self) -> None:
        dral_name = DralName(["Tx0", "Tx1", "Tx2"])
        assert dral_name.get_duplicated_group_name("TestGroup") == "Te_0_1_2_stGroup"

    def test_get_duplicated_group_name_with_alpha(self) -> None:
        dral_name = DralName(["GpioA", "GpioB", "GpioC"])
        assert dral_name.get_duplicated_group_name("Config") == "Conf_A_B_C_ig"

    def test_get_duplicated_group_name_with_two_items(self) -> None:
        dral_name = DralName(["Uart0", "Uart1"])
        assert dral_name.get_duplicated_group_name("Register") == "Regi_0_1_ster"

    def test_get_duplicated_group_name_matching_prefix(self) -> None:
        dral_name = DralName(["Tx0", "Tx1", "Tx2"])
        assert dral_name.get_duplicated_group_name("Tx") == "Tx_0_1_2"


class TestDralNameEdgeCases:
    def test_names_with_leading_numbers(self) -> None:
        dral_name = DralName(["Tx0", "Tx1", "Tx2"])
        assert dral_name.get_common_name() == "Tx_x"

    def test_names_with_multiple_digit_differences(self) -> None:
        dral_name = DralName(["Tx0", "Tx1", "Tx10"])
        assert dral_name.get_common_name() == "Tx_x"

    def test_names_natural_sort_order(self) -> None:
        dral_name = DralName(["Tx10", "Tx2", "Tx1"])
        assert dral_name._namelist == ["Tx1", "Tx2", "Tx10"]

    def test_names_with_different_length_numbers(self) -> None:
        dral_name = DralName(["Port1", "Port2"])
        assert DralName.is_similar_name("Port1", "Port2") is True
        assert dral_name.get_common_name() == "Port_x"
