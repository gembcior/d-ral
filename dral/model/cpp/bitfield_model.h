// =================================================================================
//
// MIT License
//
// Copyright (c) 2024 Gembcior
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
//
// ==================================================================================

#ifndef DRAL_BITFIELD_MODEL_H
#define DRAL_BITFIELD_MODEL_H

#include <cstdint>
#include <limits>

namespace dral {

/**
 * Bit Field Mode Template
 */
template<typename SizeType, std::size_t Position, std::size_t Width = 1>
class BitFieldModel
{
public:
  static constexpr std::size_t getWidth()
  {
    return Width;
  }

  static constexpr std::size_t getPosition()
  {
    return Position;
  }

  static constexpr std::size_t getMask()
  {
    constexpr std::size_t maxBits = sizeof(SizeType) * 8U;
    constexpr std::size_t width = getWidth();

    if constexpr (width >= maxBits) {
      return std::numeric_limits<SizeType>::max();
    } else {
      return (1U << width) - 1U;
    }
  }

  template<typename T>
  BitFieldModel& operator=(T value)
  {
    m_value = (m_value & ~(getMask() << Position)) | ((value & getMask()) << Position);
    return *this;
  }

  operator SizeType() const
  {
    return (m_value >> Position) & getMask();
  }

  explicit operator bool() const
  {
    return m_value & (getMask() << Position);
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

  static_assert(Position >= 0 && Position <= (sizeof(SizeType) * 8 - 1), "The position of the field can't exceed the register size or be less than 0.");
  static_assert(Width >= 1 && Width <= ((sizeof(SizeType) * 8) - Position),
                "The width of the field starting from the position can't exceed the register size or be less than 1.");
};

/**
 * Bit Field Mode Template specialization for 1 bit field
 */
template<typename SizeType, std::size_t Position>
class BitFieldModel<SizeType, Position>
{
public:
  static constexpr std::size_t getWidth()
  {
    return 1U;
  }

  static constexpr std::size_t getPosition()
  {
    return Position;
  }

  static constexpr std::size_t getMask()
  {
    return 1U;
  }

  BitFieldModel& operator=(bool value)
  {
    const SizeType bit = value ? 1U : 0U;
    m_value = (m_value & ~(getMask() << Position)) | (bit << Position);
    return *this;
  }

  explicit operator bool() const
  {
    return m_value & (getMask() << Position);
  }

private:
  SizeType m_value;

  static_assert(Position >= 0 && Position <= (sizeof(SizeType) * 8 - 1), "The position of the field can't exceed the register size or be less than 0.");
};

}

#endif /* DRAL_BITFIELD_MODEL_H */
