#ifndef DRAL_REGISTER_MODEL_H
#define DRAL_REGISTER_MODEL_H

#include <cstdint>

namespace dral {

template <uint32_t address>
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


template <uint32_t address, uint32_t bankOffset>
class RegisterBankModel
{
public:
  static constexpr uint32_t Address = address;

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


template <uint32_t address, uint32_t position, uint32_t mask, uint32_t bankOffset = 0>
class FieldModel
{
public:
  static constexpr uint32_t Mask = mask;
  static constexpr uint32_t Position = position;

public:
  static void write(uint32_t bank, uint32_t value)
  {
    volatile uint32_t* reg = reinterpret_cast<volatile uint32_t*>(address + (bankOffset * bank));
    *reg = (*reg & ~(mask << position)) | ((value & mask) << position);
  }

  static uint32_t read(uint32_t bank)
  {
    volatile uint32_t* reg = reinterpret_cast<volatile uint32_t*>(address + (bankOffset * bank));
    return (*reg >> position) & mask;
  }

  static uint32_t set(uint32_t value)
  {
    return (value & mask) << position;
  }

  static void set(uint32_t& reg, uint32_t value)
  {
    reg |= (value & mask) << position;
  }

  static uint32_t clear()
  {
    return ~mask;
  }

  static void clear(uint32_t& reg)
  {
    reg &= ~mask;
  }

  static uint32_t getFromRegValue(uint32_t regValue)
  {
    return (regValue >> position) & mask;
  }
};


template <uint32_t address, uint32_t position, uint32_t mask>
class FieldModel<address, position, mask, 0>
{
public:
  static constexpr uint32_t Mask = mask;
  static constexpr uint32_t Position = position;

public:
  static void write(uint32_t value)
  {
    volatile uint32_t* reg = reinterpret_cast<volatile uint32_t*>(address);
    *reg = (*reg & ~(mask << position)) | ((value & mask) << position);
  }

  static uint32_t read()
  {
    volatile uint32_t* reg = reinterpret_cast<volatile uint32_t*>(address);
    return (*reg >> position) & mask;
  }

  static uint32_t set(uint32_t value)
  {
    return (value & mask) << position;
  }

  static void set(uint32_t& reg, uint32_t value)
  {
    reg |= (value & mask) << position;
  }

  static uint32_t clear()
  {
    return ~mask;
  }

  static void clear(uint32_t& reg)
  {
    reg &= ~mask;
  }

  static uint32_t getFromRegValue(uint32_t regValue)
  {
    return (regValue >> position) & mask;
  }
};

} // namespace

#endif /* DRAL_REGISTER_MODEL_H */
