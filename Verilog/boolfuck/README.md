# Boolfuck Verilog

An awesome boolfuck machine implemented in verilog.

## Compile and Run Testbench File

```
verilator --cc --exe --build -Wall boolfuck.cpp boolfuck.v -LDFLAGS -lncurses
obj_dir/Vboolfuck
```

*Notice: You need to install verilator and libncurses first.*

## Usage

| Key | Uasage |
| --- | --- |
| `s` | move left |
| `d` | move right |
| `<space>` | start/stop the program |
