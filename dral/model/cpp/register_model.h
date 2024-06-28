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

#ifndef DRAL_REGISTER_MODEL_H
#define DRAL_REGISTER_MODEL_H

#include <cstdint>
#include <limits>
#include <utility>

namespace dral {

/**
 * Static Register Model Template
 */
template<typename RegType, typename AddressPolicy>
class StaticRegisterModel
{
private:
  using SizeType = decltype(RegType::value);

public:
  template<typename... Index>
  static RegType read(Index&&... index)
  {
    volatile const SizeType* const regptr = reinterpret_cast<volatile const SizeType*>(AddressPolicy::getAddress(index...));
    return RegType{ *regptr };
  }

  template<typename... Index>
  static void write(const RegType& reg, Index&&... index)
  {
    volatile SizeType* const regptr = reinterpret_cast<volatile SizeType*>(AddressPolicy::getAddress(index...));
    *regptr = reg.value;
  }

  template<typename... Index>
  static void write(SizeType value, Index&&... index)
  {
    volatile SizeType* const regptr = reinterpret_cast<volatile SizeType*>(AddressPolicy::getAddress(index...));
    *regptr = value;
  }

public:
  template<typename... Index>
  static constexpr std::uintptr_t getAddress(Index&&... index)
  {
    return AddressPolicy::getAddress(index...);
  }
};

/**
 * Base Register Model Template
 */
template<typename RegType>
class BaseRegisterModel
{
private:
  using SizeType = decltype(RegType::value);

public:
  constexpr explicit BaseRegisterModel(std::uintptr_t address)
    : m_address(address)
  {
  }

public:
  RegType read() const
  {
    volatile const SizeType* const regptr = reinterpret_cast<volatile const SizeType*>(getAddress());
    return RegType{ *regptr };
  }

  void write(const RegType& reg) const
  {
    volatile SizeType* const regptr = reinterpret_cast<volatile SizeType*>(getAddress());
    *regptr = reg.value;
  }

  void write(SizeType value) const
  {
    volatile SizeType* const regptr = reinterpret_cast<volatile SizeType*>(getAddress());
    *regptr = value;
  }

public:
  constexpr std::uintptr_t getAddress() const
  {
    return m_address;
  }

private:
  const std::uintptr_t m_address;
};

/**
 * Register Model Template
 */
template<typename RegType, typename AddressPolicy>
class RegisterModel : public StaticRegisterModel<RegType, AddressPolicy>
{
public:
  template<typename... Index>
  constexpr auto operator()(Index&&... index) const
  {
    return BaseRegisterModel<RegType>{ AddressPolicy::getAddress(std::forward<Index>(index)...) };
  }
};

/**
 * Core Field Model Template
 */
template<typename RegType, std::size_t Position, std::size_t Width>
class CoreFieldModel
{
private:
  using SizeType = decltype(RegType::value);

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
    constexpr auto maxBits = sizeof(SizeType) * 8U;
    constexpr auto width = getWidth();

    if constexpr (width >= maxBits) {
      return std::numeric_limits<SizeType>::max();
    } else {
      return (1U << width) - 1U;
    }
  }

  static_assert(Position >= 0 && Position <= (sizeof(SizeType) * 8 - 1), "The position of the field can't exceed the register size or be less than 0.");
  static_assert(Width >= 1 && Width <= ((sizeof(SizeType) * 8) - Position),
                "The width of the field starting from the position can't exceed the register size or be less than 1.");
};

/**
 * Static Field Model Template
 */
template<typename RegType, typename AddressPolicy, std::size_t Position, std::size_t Width>
class StaticFieldModel : public CoreFieldModel<RegType, Position, Width>
{
private:
  using BaseModel = CoreFieldModel<RegType, Position, Width>;
  using SizeType = decltype(RegType::value);

public:
  template<typename... Index>
  static SizeType read(Index&&... index)
  {
    volatile const SizeType* const regptr = reinterpret_cast<volatile const SizeType*>(AddressPolicy::getAddress(index...));
    return (*regptr >> Position) & BaseModel::getMask();
  }

  template<typename... Index>
  static void write(SizeType value, Index&&... index)
  {
    volatile SizeType* const regptr = reinterpret_cast<volatile SizeType*>(AddressPolicy::getAddress(index...));
    *regptr = (*regptr & ~(BaseModel::getMask() << Position)) | ((value & BaseModel::getMask()) << Position);
  }
};

/**
 * Base Field Model Template
 */
template<typename RegType, std::size_t Position, std::size_t Width>
class BaseFieldModel : public CoreFieldModel<RegType, Position, Width>
{
private:
  using BaseModel = CoreFieldModel<RegType, Position, Width>;
  using SizeType = decltype(RegType::value);

public:
  constexpr explicit BaseFieldModel(std::uintptr_t address)
    : m_reg(address)
  {
  }

public:
  SizeType read() const
  {
    return (m_reg.read().value >> BaseModel::getPosition()) & BaseModel::getMask();
  }

  void write(SizeType value) const
  {
    m_reg.write((m_reg.read().value & ~(BaseModel::getMask() << BaseModel::getPosition())) | ((value & BaseModel::getMask()) << BaseModel::getPosition()));
  }

private:
  const BaseRegisterModel<RegType> m_reg;
};

/**
 * Field Model Template
 */
template<typename RegType, typename AddressPolicy, std::size_t Position, std::size_t Width>
class FieldModel : public StaticFieldModel<RegType, AddressPolicy, Position, Width>
{
public:
  template<typename... Index>
  constexpr auto operator()(Index&&... index) const
  {
    return BaseFieldModel<RegType, Position, Width>{ AddressPolicy::getAddress(std::forward<Index>(index)...) };
  }
};

}

#endif /* DRAL_REGISTER_MODEL_H */
