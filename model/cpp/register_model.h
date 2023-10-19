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

namespace dral {

template<uint32_t address>
class RegisterModel
{
public:
  static constexpr uint32_t Address = address;

public:
  static uint32_t read()
  {
    volatile uint32_t* reg = reinterpret_cast<volatile uint32_t*>(address);
    return *reg;
  }

  static void write(uint32_t value)
  {
    volatile uint32_t* reg = reinterpret_cast<volatile uint32_t*>(address);
    *reg = value;
  }
};

template<uint32_t address, uint32_t bankOffset>
class RegisterBankModel
{
public:
  static constexpr uint32_t Address = address;
  static constexpr uint32_t BankOffset = bankOffset;

public:
  static uint32_t read(uint32_t bank)
  {
    volatile uint32_t* reg = reinterpret_cast<volatile uint32_t*>(address + (bankOffset * bank));
    return *reg;
  }

  static void write(uint32_t bank, uint32_t value)
  {
    volatile uint32_t* reg = reinterpret_cast<volatile uint32_t*>(address + (bankOffset * bank));
    *reg = value;
  }
};

template<uint32_t address, uint32_t position, uint32_t width, uint32_t bankOffset = 0>
class FieldModel
{
public:
  static constexpr uint32_t Width = width;
  static constexpr uint32_t Mask = (1U << width) - 1U;
  static constexpr uint32_t Position = position;

public:
  static void write(uint32_t bank, uint32_t value)
  {
    volatile uint32_t* reg = reinterpret_cast<volatile uint32_t*>(address + (bankOffset * bank));
    *reg = (*reg & ~(Mask << position)) | ((value & Mask) << position);
  }

  static uint32_t read(uint32_t bank)
  {
    volatile uint32_t* reg = reinterpret_cast<volatile uint32_t*>(address + (bankOffset * bank));
    return (*reg >> position) & Mask;
  }

  static_assert(position >= 0 && position <= 31, "Field position must be between 0 and 31");
  static_assert(width >= 1 && width <= 32, "Field width must be between 1 and 32");
};

template<uint32_t address, uint32_t position, uint32_t width>
class FieldModel<address, position, width, 0>
{
public:
  static constexpr uint32_t Width = width;
  static constexpr uint32_t Mask = (1U << width) - 1U;
  static constexpr uint32_t Position = position;

public:
  static void write(uint32_t value)
  {
    volatile uint32_t* reg = reinterpret_cast<volatile uint32_t*>(address);
    *reg = (*reg & ~(Mask << position)) | ((value & Mask) << position);
  }

  static uint32_t read()
  {
    volatile uint32_t* reg = reinterpret_cast<volatile uint32_t*>(address);
    return (*reg >> position) & Mask;
  }

  static_assert(position >= 0 && position <= 31, "Field position must be between 0 and 31");
  static_assert(width >= 1 && width <= 32, "Field width must be between 1 and 32");
};

template<uint32_t position, uint32_t width = 1>
class BitFieldModel
{
public:
  static constexpr uint32_t Width = width;
  static constexpr uint32_t Mask = (1U << width) - 1U;
  static constexpr uint32_t Position = position;

public:
  template<typename T>
  BitFieldModel& operator=(T value)
  {
    m_value = (m_value & ~(Mask << position)) | ((value & Mask) << position);
    return *this;
  }

  operator uint32_t() const
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

  uint32_t operator++(int)
  {
    const uint32_t result = *this;
    ++*this;
    return result;
  }

  BitFieldModel& operator--()
  {
    return *this = *this - 1U;
  }

  uint32_t operator--(int)
  {
    const uint32_t result = *this;
    --*this;
    return result;
  }

private:
  uint32_t m_value;

  static_assert(position >= 0 && position <= 31, "BitFiled position must be between 0 and 31");
  static_assert(width >= 1 && width <= 32, "BitFiled width must be between 1 and 32");
};

template<uint32_t position>
class BitFieldModel<position, 1U>
{
public:
  static constexpr uint32_t Width = 1U;
  static constexpr uint32_t Mask = (1U << Width) - 1U;
  static constexpr uint32_t Position = position;

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
  uint32_t m_value;

  static_assert(position >= 0 && position <= 31, "BitFiled position must be between 0 and 31");
};

}  // namespace

#endif /* DRAL_REGISTER_MODEL_H */
