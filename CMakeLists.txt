cmake_minimum_required(VERSION 3.16)

if (NOT DRAL_BRAND)
  message(FATAL_ERROR "No DRAL_BRAND variable specify!")
endif()

if (NOT DRAL_FAMILY)
  message(FATAL_ERROR "No DRAL_FAMILY variable specify!")
endif()

if (NOT DRAL_CHIP)
  message(FATAL_ERROR "No DRAL_CHIP variable specify!")
endif()

if (NOT DRAL_PYTHON)
  set(DRAL_PYTHON python3)
endif()

if (NOT DRAL_GENERATOR)
  set(DRAL_GENERATOR ${CMAKE_CURRENT_SOURCE_DIR}/generator/Generator.py)
endif()

add_library(dral INTERFACE)

target_include_directories(dral
  INTERFACE
    ${CMAKE_CURRENT_SOURCE_DIR}/dral
)

add_custom_command(dral
  PRE_BUILD
  COMMAND ${DRAL_PYTHON} ${DRAL_GENERATOR} -b ${DRAL_BRAND} -f ${DRAL_FAMILY} -c ${DRAL_CHIP}
  COMMENT "Generating DRAL - Device Register Access Layer files"
)
