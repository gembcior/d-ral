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

execute_process(
  COMMAND ${DRAL_PYTHON} ${DRAL_GENERATOR} -b ${DRAL_BRAND} -f ${DRAL_FAMILY} -c ${DRAL_CHIP}
)

set(DRAL_LIB_NAME dral_${DRAL_BRAND}_${DRAL_FAMILY}_${DRAL_CHIP}

add_library(${DRAL_LIB_NAME} INTERFACE)

target_include_directories(${DRAL_LIB_NAME}
  INTERFACE
    ${CMAKE_CURRENT_SOURCE_DIR}/${DRAL_LIB_NAME}
)
