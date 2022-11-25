# Boolfuck Verilog

An awesome boolfuck machine implemented in verilog.

## Compile and Run Testbench File

```
verilator --cc --exe --build -Wall boolfuck.cpp boolfuck.v -LDFLAGS -static
obj_dir/Vboolfuck.exe
```

*Notice: You need to install verilator in msys2 to compile it.*

## Usage

| Key | Uasage |
| --- | --- |
| `s` | move left |
| `d` | move right |
| `<space>` | start/stop the program |
