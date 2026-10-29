"""Small, read-only LLVM C API adapter; no textual IR parsing or extra wheel."""
from __future__ import annotations

import ctypes as C
from pathlib import Path


class LLVM:
    def __init__(self, library: Path):
        self.library = library.resolve()
        self.lib = C.CDLL(str(self.library))
        p, u, s = C.c_void_p, C.c_uint, C.c_size_t
        self.GetVersion = self.lib.LLVMGetVersion
        self.GetVersion.restype = None
        self.GetVersion.argtypes = [C.POINTER(u)] * 3
        if self.version.split(".")[0] != "22":
            raise ValueError("Flow extraction currently supports LLVM 22 only")
        signatures = {
            "ContextCreate": (p, []), "ContextDispose": (None, [p]),
            "DisposeModule": (None, [p]), "DisposeMessage": (None, [p]),
            "CreateMemoryBufferWithMemoryRangeCopy": (p, [C.c_char_p, s, C.c_char_p]),
            "ParseIRInContext": (C.c_int, [p, p, C.POINTER(p), C.POINTER(p)]),
            "VerifyModule": (C.c_int, [p, C.c_int, C.POINTER(p)]),
            "GetVersion": (None, [C.POINTER(u), C.POINTER(u), C.POINTER(u)]),
            "GetValueName2": (p, [p, C.POINTER(s)]),
            "PrintValueToString": (p, [p]),
            "GetInstructionOpcode": (u, [p]),
            "GetNumOperands": (C.c_int, [p]), "GetOperand": (p, [p, u]),
            "GetNumSuccessors": (u, [p]), "GetSuccessor": (p, [p, u]),
            "GetSwitchCaseValue": (p, [p, u]),
            "GetBasicBlockTerminator": (p, [p]),
            "BasicBlockAsValue": (p, [p]),
            "GetDebugLocLine": (u, [p]), "GetDebugLocColumn": (u, [p]),
            "GetDebugLocFilename": (p, [p, C.POINTER(u)]),
            "GetDebugLocDirectory": (p, [p, C.POINTER(u)]),
            "GetIncomingBlock": (p, [p, u]),
        }
        for kind in ("Function", "Param", "BasicBlock", "Instruction"):
            signatures["GetFirst" + kind] = (p, [p])
            signatures["GetNext" + kind] = (p, [p])
        for kind in ("BasicBlock", "ConstantExpr", "GlobalValue", "Function"):
            signatures["IsA" + kind] = (p, [p])
        for name, (result, args) in signatures.items():
            fn = getattr(self.lib, "LLVM" + name)
            fn.restype, fn.argtypes = result, args
            setattr(self, name, fn)

    @property
    def version(self):
        values = [C.c_uint() for _ in range(3)]
        self.GetVersion(*(C.byref(v) for v in values))
        return ".".join(str(v.value) for v in values)

    def name(self, value):
        length = C.c_size_t()
        ptr = self.GetValueName2(value, C.byref(length))
        return C.string_at(ptr, length.value).decode("utf-8", "replace") if ptr else ""

    def text(self, value):
        ptr = self.PrintValueToString(value)
        try:
            return C.string_at(ptr).decode("utf-8", "replace").strip()
        finally:
            self.DisposeMessage(ptr)

    def debug_string(self, value, field):
        length = C.c_uint()
        ptr = getattr(self, "GetDebugLoc" + field)(value, C.byref(length))
        return C.string_at(ptr, length.value).decode("utf-8", "replace") if ptr else ""

    def items(self, parent, kind):
        value = getattr(self, "GetFirst" + kind)(parent)
        while value:
            yield value
            value = getattr(self, "GetNext" + kind)(value)

    def parse(self, data: bytes):
        return Module(self, data)


class Module:
    def __init__(self, api: LLVM, data: bytes):
        self.api = api
        self.context = api.ContextCreate()
        self.module = C.c_void_p()
        error = C.c_void_p()
        buffer = api.CreateMemoryBufferWithMemoryRangeCopy(data, len(data), b"flow.ll")
        # ParseIRInContext takes ownership of the memory buffer.
        failed = api.ParseIRInContext(self.context, buffer, C.byref(self.module), C.byref(error))
        if failed:
            message = C.string_at(error).decode("utf-8", "replace")
            api.DisposeMessage(error)
            api.ContextDispose(self.context)
            raise ValueError(message)
        if api.VerifyModule(self.module, 2, C.byref(error)):
            message = C.string_at(error).decode("utf-8", "replace")
            api.DisposeMessage(error)
            self.__exit__(None, None, None)
            raise ValueError(message)
        if error:
            api.DisposeMessage(error)

    def __enter__(self):
        return self.module

    def __exit__(self, *_):
        self.api.DisposeModule(self.module)
        self.api.ContextDispose(self.context)
