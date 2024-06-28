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

#ifndef DRAL_GROUP_ADDRESS_POLICY_H
#define DRAL_GROUP_ADDRESS_POLICY_H

#include <cstdint>
#include <tuple>

namespace dral {

/**
 * Indices Type Extractor
 */
template<typename T>
class DefaultTypeExtractor
{
public:
  using type = typename T::type;
};

template<typename T>
class OffsetPolicyTypeExtractor
{
public:
  using type = typename T::IndexType;
};

template<template<typename> class TypeExtractor, typename Tuple, typename Index>
struct ExtractedTypesTuple;

template<template<typename> class TypeExtractor, typename Tuple, std::size_t... Index>
struct ExtractedTypesTuple<TypeExtractor, Tuple, std::index_sequence<Index...>>
{
  using type = std::tuple<typename TypeExtractor<std::tuple_element_t<Index, Tuple>>::type...>;
};

template<typename Tuple, template<typename> class TypeExtractor = DefaultTypeExtractor>
using IndicesTypesTuple = typename ExtractedTypesTuple<TypeExtractor, Tuple, std::make_index_sequence<std::tuple_size_v<Tuple>>>::type;

/**
 * Group Address Policy
 */
template<std::uintptr_t Address, typename OffsetPolicy = void>
class GroupAddressPolicy;

template<std::uintptr_t Address, typename... OffsetPolicy>
class GroupAddressPolicy<Address, std::tuple<OffsetPolicy...>>
{
public:
  static constexpr std::size_t LayersCount{ sizeof...(OffsetPolicy) };
  using Layers = std::tuple<OffsetPolicy...>;
  using IndexType = IndicesTypesTuple<Layers, OffsetPolicyTypeExtractor>;

  template<std::size_t I>
  using LayerPolicy = std::tuple_element_t<I, Layers>;

public:
  static constexpr std::uintptr_t getBaseAddress()
  {
    return Address;
  }

  static std::uintptr_t getAddress(const IndexType& index)
  {
    return Address + getOffset<LayersCount - 1>(index);
  }

  template<typename... Index>
  static std::uintptr_t getAddress(Index&&... index)
  {
    static_assert(sizeof...(Index) == LayersCount, "The number of indices must match the number of layers.");
    const auto indexValue{ IndexType(std::forward<Index>(index)...) };
    return getAddress(indexValue);
  }

private:
  template<std::size_t Index>
  static constexpr std::uintptr_t getOffset(const IndexType& index)
  {
    const std::uintptr_t offset{ LayerPolicy<Index>::getOffset(std::get<Index>(index)) };
    if constexpr (Index > 0) {
      return offset + getOffset<Index - 1>(index);
    }
    return offset;
  }
};

template<std::uintptr_t Address, typename OffsetPolicy>
class GroupAddressPolicy<Address, std::tuple<OffsetPolicy>>
{
public:
  static constexpr std::size_t LayersCount = 1;
  using IndexType = typename OffsetPolicy::IndexType;
  using LayerPolicy = OffsetPolicy;

public:
  static constexpr std::uintptr_t getBaseAddress()
  {
    return Address;
  }

  static std::uintptr_t getAddress(const IndexType& index)
  {
    return Address + OffsetPolicy::getOffset(index);
  }
};

template<uintptr_t Address>
class GroupAddressPolicy<Address, void>
{
public:
  static constexpr std::size_t LayersCount = 0;

public:
  static constexpr std::uintptr_t getBaseAddress()
  {
    return Address;
  }

  static constexpr uintptr_t getAddress()
  {
    return Address;
  }
};

}

#endif /* DRAL_GROUP_ADDRESS_POLICY_H */
