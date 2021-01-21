#ifndef REGISTER_MODEL_H
#define REGISTER_MODEL_H

#include <cstdint>

// TODO Add support for byte access and halfword access
// TODO Add support for other register policy
namespace stm32::regs {

enum class RegisterPolicy {
  ReadOnly,
  WriteOnly,
  ReadWrite,
};


using FieldPolicy = RegisterPolicy;


template<RegisterPolicy regPolicy>
class RegisterPolicyExecutor
{
};


template<>
class RegisterPolicyExecutor<RegisterPolicy::WriteOnly>
{
public:
  static void write(volatile uint32_t* reg, uint32_t value)
  {
    *reg = value;
  }
};


template<>
class RegisterPolicyExecutor<RegisterPolicy::ReadOnly>
{
public:
  static uint32_t read(volatile uint32_t* reg)
  {
    return *reg;
  }
};


template<>
class RegisterPolicyExecutor<RegisterPolicy::ReadWrite>
{
public:
  static uint32_t read(volatile uint32_t* reg)
  {
    return *reg;
  }

  static void write(volatile uint32_t* reg, uint32_t value)
  {
    *reg = value;
  }
};


template<RegisterPolicy regPolicy, FieldPolicy fieldPolicy>
class FieldPolicyExecutor
{
};


template<>
class FieldPolicyExecutor<RegisterPolicy::ReadOnly, FieldPolicy::ReadOnly>
{
public:
  static uint32_t read(volatile uint32_t* reg, uint32_t offset, uint32_t mask)
  {
    return (*reg >> offset) & mask;
  }
};


template<>
class FieldPolicyExecutor<RegisterPolicy::WriteOnly, FieldPolicy::WriteOnly>
{
public:
  static void write(volatile uint32_t* reg, uint32_t offset, uint32_t mask, uint32_t value)
  {
    *reg = (value & mask) << offset;
  }
};


template<>
class FieldPolicyExecutor<RegisterPolicy::ReadWrite, FieldPolicy::ReadOnly>
{
public:
  static uint32_t read(volatile uint32_t* reg, uint32_t offset, uint32_t mask)
  {
    return (*reg >> offset) & mask;
  }
};


template<>
class FieldPolicyExecutor<RegisterPolicy::ReadWrite, FieldPolicy::WriteOnly>
{
public:
  static void write(volatile uint32_t* reg, uint32_t offset, uint32_t mask, uint32_t value)
  {
    *reg = (*reg & ~(mask << offset)) | ((value & mask) << offset);
  }
};


template<>
class FieldPolicyExecutor<RegisterPolicy::ReadWrite, FieldPolicy::ReadWrite>
{
public:
  static uint32_t read(volatile uint32_t* reg, uint32_t offset, uint32_t mask)
  {
    return (*reg >> offset) & mask;
  }

  static void write(volatile uint32_t* reg, uint32_t offset, uint32_t mask, uint32_t value)
  {
    *reg = (*reg & ~(mask << offset)) | ((value & mask) << offset);
  }
};


// TODO add register mask parameter to ommit reserved fields that must be kept at reset value
template <uint32_t address, RegisterPolicy policy>
class RegisterModel
{
public:
  static void write(uint32_t value)
  {
    RegisterPolicyExecutor<policy>::write(reinterpret_cast<volatile uint32_t*>(address), value);
  }

  static uint32_t read()
  {
    return RegisterPolicyExecutor<policy>::read(reinterpret_cast<volatile uint32_t*>(address));
  }

private:
  static constexpr RegisterPolicy m_policy = policy;
};


template <uint32_t address, uint32_t offset, uint32_t mask, RegisterPolicy regPolicy, FieldPolicy fieldPolicy>
class FieldModel
{
public:
  static void write(uint32_t value)
  {
    FieldPolicyExecutor<regPolicy, fieldPolicy>::write(reinterpret_cast<volatile uint32_t*>(address), offset, mask, value);
  }

  static uint32_t read()
  {
    return FieldPolicyExecutor<regPolicy, fieldPolicy>::read(reinterpret_cast<volatile uint32_t*>(address), offset, mask);
  }
};

} // namespace

#endif /* REGISTER_MODEL_H */
