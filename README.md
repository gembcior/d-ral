![Logo](https://raw.githubusercontent.com/gembcior/d-ral/main/doc/logo.svg)

<h1 align="center">D-RAL - Device Register Access Layer</h1>

[![PyPI](https://img.shields.io/pypi/v/dral?label=dral)](https://pypi.org/project/dral/)
[![PyPI - License](https://img.shields.io/pypi/l/dral)](https://pypi.org/project/dral/)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/dral)](https://pypi.org/project/dral/)
[![PyPI - Format](https://img.shields.io/pypi/format/dral)](https://pypi.org/project/dral/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/dral)](https://pypi.org/project/dral/)

---

## What is it?
D-RAL is a register access code generator for any device, chip or embedded system. The goal is to provide a simple and consistent way to access the internal registers of the device.
Every embedded project requires the programmer to manipulate registers. D-RAL is trying to address this and provide an easy way to access registers.
The main motivation for creating this project was to design a register access layer for modern C++ programming language.

## Main functionality
Main functionality is to generate a register access layer based on the device register description input for the C++ programming language.
Currently, D-RAL only supports the SVD format as an input file with a description of the registers.
[SVD](https://arm-software.github.io/CMSIS_5/SVD/html/index.html) is an ARM-created format that formalizes the description of the system inside microcontrollers based on Arm Cortex-M processors, specifically the memory mapped registers of peripherals.
It is a widely used format by many companies.
It is also possible to use your own register description format in D-RAL by writing an adapter that translates it to know for the D-RAL form. More about this on the wiki page.
D-RAL generates a set of header files that you can simply copy and paste into your existing project.

### Example
Let's take the STM32F411 microcontroller and its general-purpose timers as an example. We want to configure the TIM2 timer as a countdown timer. To do this, we need to set the direction bit in one of the timer's control registers.
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/gembcior/d-ral/main/doc/stm32f411_tim2_control_register_dark.svg">
    <img alt="STM32F411 Tim2 Control Register" src="https://raw.githubusercontent.com/gembcior/d-ral/main/doc/stm32f411_tim2_control_register.svg">
  </picture>
</p>

We can accomplish this in C++ by utilizing raw pointers:
```c++
constexpr uint32_t Tim2Cr1Address = 0x4000'0000;
constexpr uint32_t Tim2Cr1DirPos = 4;
constexpr uint32_t Tim2Cr1DirMask = 0x1;

volatile uint32_t* Tim2Cr1Reg = reinterpret_cast<volatile uint32_t*>(Tim2Cr1Address);
*Tim2Cr1Reg = (*Tim2Cr1Reg & ~(Tim2Cr1DirMask << Tim2Cr1DirPos)) | ((1 & Tim2Cr1DirMask) << Tim2Cr1DirPos);
```

Or we can use D-RAL:
```c++
using namespace dral::stm32f411;

Tim2Group::Cr1Register::dirField::write(1);
```
This is a brief example to demonstrate D-RAL's purpose. More information can be found on the Wiki page.

### Main benefits of using D-RAL:
- Simple and clean syntax,
- Less code,
- No need to warry about bit shifting and masking,
- No run-time overhead

## Installing
The easiest way to install D-RAL is with [pipx](https://pypa.github.io/pipx/).

```
pipx install dral
```
You can also install D-RAL with `pip`:
```
pip install dral
```
Whichever method you use, you should have a `dral` command on your path.

## Usage
```
Usage: dral [OPTIONS] INPUT_FILE

  D-RAL - Device Register Access Layer

  Generate D-RAL files from INPUT-FILE.

  INPUT-FILE  - path to device description file.

Options:
  -O, --output-path PATH          Output directory. Path where files will be
                                  generated. Default is current directory.
  -l, --language [cpp|html]       Specify the programming language for which
                                  you want to generate files.  [default: cpp]
  -t, --access-type [direct|indirect]
                                  Specify the access template. Applys only for
                                  C++ model.  [default: direct]
  -T, --template-path PATH        Specify path to template files used to
                                  generate files.
  -s, --skip-groups-detection     Skip automatic registers groups detection.
  -f, --skip-output-formatting    Skip output formatting with auto format
                                  tools.
  -w, --white-list PATH           Paripherals and Registers white list.
  -b, --black-list PATH           Peripherals and Registers black list.
  --version                       Show the version and exit.
  --help                          Show this message and exit.
```

## Other Programming Languages
The D-RAL generator is flexible enough to be easily adapted to generate register access layers for other programming languages or for other use cases.
More about it on the Wiki page.
