import llvmlite.ir as ir
import llvmlite.binding as llvm

# TEST_FILE değişkenini tanımlıyoruz, test/test.yo dosyasının yolu olarak belirliyoruz.
TEST_FILE = "test/test.yo"

# LLVM modülü oluşturma
module = ir.Module(name="yazdir_module")

def create_yazdir_function():
    # yazdir fonksiyonu tanımlama, hem string hem de int alabilen
    yazdir_func_type = ir.FunctionType(ir.VoidType(), [ir.PointerType(ir.IntType(8))])
    yazdir_func = ir.Function(module, yazdir_func_type, name="yazdir")
    block = yazdir_func.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)

    # yazdir fonksiyonu içinde yazdırma işlemini tanımlama
    printf_func = ir.Function(module, ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=True), name="printf")
    builder.call(printf_func, [yazdir_func.args[0]])
    builder.ret_void()

def parse_and_compile(filename):
    with open(filename, "r") as file:
        for line in file:
            if line.startswith("yazdir"):
                # yazdir komutunu ayrıştırma
                content = line.strip().split("(", 1)[1].rsplit(")", 1)[0].strip()
                if content.startswith("\"") and content.endswith("\""):
                    # String ise
                    content = content[1:-1]  # Tırnakları çıkar
                    string_constant = ir.Constant(ir.ArrayType(ir.IntType(8), len(content) + 1), bytearray(content.encode('utf8')) + b'\00')
                    global_string = ir.GlobalVariable(module, string_constant.type, name="global_string")
                    global_string.initializer = string_constant
                    global_string.global_constant = True
                    global_string.linkage = 'internal'
                    create_yazdir_function()
                    return global_string
                else:
                    # Sayı ise
                    number = int(content)
                    fmt_arg = f"{number}\n\0"
                    fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt_arg)), bytearray(fmt_arg.encode('utf8')))
                    global_fmt = ir.GlobalVariable(module, fmt.type, name="global_fmt")
                    global_fmt.initializer = fmt
                    global_fmt.global_constant = True
                    global_fmt.linkage = 'internal'
                    create_yazdir_function()
                    return global_fmt
    return None

def main():
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    global_var = parse_and_compile(TEST_FILE)
    if global_var is None:
        print("Dosya içeriği geçersiz.")
        return

    # LLVM IR kodunu yazdırma
    print(str(module))

    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine()

    backing_mod = llvm.parse_assembly(str(module))
    backing_mod.verify()

    with llvm.create_mcjit_compiler(backing_mod, target_machine) as ee:
        ee.finalize_object()
        ee.run_static_constructors()
        
        yazdir = ee.get_function_address("yazdir")
        
        # CFFI ile JIT derlenmiş fonksiyonu çağırma
        import ctypes
        yazdir_func = ctypes.CFUNCTYPE(None, ctypes.c_char_p)(yazdir)

        # Global değişkenin bellek adresini almak
        global_var_addr = ee.get_global_value_address(global_var.name)
        yazdir_func(ctypes.c_char_p(global_var_addr))

if __name__ == "__main__":
    main()
