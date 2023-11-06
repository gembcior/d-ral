/*
 * D-RAL - Device Register Access Layer
 * https://github.com/gembcior/d-ral
 *
 * MIT License
 *
 * Copyright (c) 2023 Gembcior
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 * This is an auto generated file. Do not modify!
 */

#ifndef DRAL_REGISTER_MODEL_H
#define DRAL_REGISTER_MODEL_H

#include <cstdint>
#include <type_traits>

namespace dral {

template<typename SizeType, SizeType address>
class RegisterModel
{
public:
  static constexpr SizeType Address = address;

public:
  static SizeType read()
  {
    volatile SizeType* reg = reinterpret_cast<volatile SizeType*>(address);
    return *reg;
  }

  static void write(SizeType value)
  {
    volatile SizeType* reg = reinterpret_cast<volatile SizeType*>(address);
    *reg = value;
  }
};

template<typename SizeType, SizeType address, SizeType bankOffset>
class RegisterBankModel
{
public:
  static constexpr SizeType Address = address;
  static constexpr SizeType BankOffset = bankOffset;

public:
  static SizeType read(SizeType bank)
  {
    volatile SizeType* reg = reinterpret_cast<volatile SizeType*>(address + (bankOffset * bank));
    return *reg;
  }

  static void write(SizeType bank, SizeType value)
  {
    volatile SizeType* reg = reinterpret_cast<volatile SizeType*>(address + (bankOffset * bank));
    *reg = value;
  }
};

template<typename SizeType, SizeType address, SizeType position, SizeType width, SizeType bankOffset = 0, typename = void>
class FieldModel
{
public:
  static constexpr SizeType Width = width;
  static constexpr SizeType Mask = (1U << width) - 1U;
  static constexpr SizeType Position = position;

public:
  static void write(SizeType bank, SizeType value)
  {
    volatile SizeType* reg = reinterpret_cast<volatile SizeType*>(address + (bankOffset * bank));
    *reg = (*reg & ~(Mask << position)) | ((value & Mask) << position);
  }

  static SizeType read(SizeType bank)
  {
    volatile SizeType* reg = reinterpret_cast<volatile SizeType*>(address + (bankOffset * bank));
    return (*reg >> position) & Mask;
  }

  static_assert(position >= 0 && position <= (sizeof(SizeType) * 8 - 1), "The position of the field can't exceed the register size or be less than 0.");
  static_assert(width >= 1 && width <= ((sizeof(SizeType) * 8) - position), "The width of the field starting from the position can't exceed the register size or be less than 1.");
};

template<typename SizeType, SizeType address, SizeType position, SizeType width, SizeType bankOffset>
class FieldModel<SizeType, address, position, width, bankOffset, std::enable_if_t<bankOffset == 0>>
{
public:
  static constexpr SizeType Width = width;
  static constexpr SizeType Mask = (1U << width) - 1U;
  static constexpr SizeType Position = position;

public:
  static void write(SizeType value)
  {
    volatile SizeType* reg = reinterpret_cast<volatile SizeType*>(address);
    *reg = (*reg & ~(Mask << position)) | ((value & Mask) << position);
  }

  static SizeType read()
  {
    volatile SizeType* reg = reinterpret_cast<volatile SizeType*>(address);
    return (*reg >> position) & Mask;
  }

  static_assert(position >= 0 && position <= (sizeof(SizeType) * 8 - 1), "The position of the field can't exceed the register size or be less than 0.");
  static_assert(width >= 1 && width <= ((sizeof(SizeType) * 8) - position), "The width of the field starting from the position can't exceed the register size or be less than 1.");
};

template<typename SizeType, SizeType position, SizeType width = 1, typename = void>
class BitFieldModel
{
public:
  static constexpr SizeType Width = width;
  static constexpr SizeType Mask = (1U << width) - 1U;
  static constexpr SizeType Position = position;

public:
  template<typename T>
  BitFieldModel& operator=(T value)
  {
    m_value = (m_value & ~(Mask << position)) | ((value & Mask) << position);
    return *this;
  }

  operator SizeType() const
  {
    return (m_value >> position) & Mask;
  }

  explicit operator bool() const
  {
    return m_value & (Mask << position);
  }

  BitFieldModel& operator++()
  {
    return *this = *this + 1U;
  }

  SizeType operator++(int)
  {
    const SizeType result = *this;
    ++*this;
    return result;
  }

  BitFieldModel& operator--()
  {
    return *this = *this - 1U;
  }

  SizeType operator--(int)
  {
    const SizeType result = *this;
    --*this;
    return result;
  }

private:
  SizeType m_value;

  static_assert(position >= 0 && position <= (sizeof(SizeType) * 8 - 1), "The position of the field can't exceed the register size or be less than 0.");
  static_assert(width >= 1 && width <= ((sizeof(SizeType) * 8) - position), "The width of the field starting from the position can't exceed the register size or be less than 1.");
};

template<typename SizeType, SizeType position, SizeType width>
class BitFieldModel<SizeType, position, width, std::enable_if_t<width == 1>>
{
public:
  static constexpr SizeType Width = 1U;
  static constexpr SizeType Mask = (1U << Width) - 1U;
  static constexpr SizeType Position = position;

public:
  BitFieldModel& operator=(bool value)
  {
    m_value = (m_value & ~(Mask << position)) | (value << position);
    return *this;
  }

  explicit operator bool() const
  {
    return m_value & (Mask << position);
  }

private:
  SizeType m_value;

  static_assert(position >= 0 && position <= (sizeof(SizeType) * 8 - 1), "The position of the field can't exceed the register size or be less than 0.");
  static_assert(width >= 1 && width <= ((sizeof(SizeType) * 8) - position), "The width of the field starting from the position can't exceed the register size or be less than 1.");
};

}  // namespace

#endif /* DRAL_REGISTER_MODEL_H */
