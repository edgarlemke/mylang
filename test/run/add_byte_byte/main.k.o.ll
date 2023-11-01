define i64 @linux_write (i64 %fildes, i8* %buf, i64 %nbyte) {
start:
%retv = call i64 asm sideeffect "syscall",
        "={rax},{rax},{rdi},{rsi},{rdx}"
        (i64 1, i64 %fildes, i8* %buf, i64 %nbyte)
ret i64 %retv
}

%struct.Str = type {i8*, i64}

%Array_byte = type {i8*, i64}
@stdin = constant i64 0
@stdout = constant i64 1
@stderr = constant i64 2
define void @print__Str(%struct.Str* %text) {
	start:

		%str_addr_ptr = getelementptr i8*, %struct.Str* %text, i64 0
		%str_size_ptr = getelementptr i64, %struct.Str* %text, i64 1

		%fd = load i64, i64* @stdout
		%addr = load i8*, i8** %str_addr_ptr
		%size = load i64, i64* %str_size_ptr

		call void @linux_write(i64 %fd, i8* %addr, i64 %size)

		ret void ; bug
}
define void @print__Array_byte(i8* %text) {
	start:

		%str_addr_ptr = getelementptr i8*, %struct.Str* %text, i64 0
		%str_size_ptr = getelementptr i64, %struct.Str* %text, i64 1

		%fd = load i64, i64* @stdout
		%addr = load i8*, i8** %str_addr_ptr
		%size = load i64, i64* %str_size_ptr

		call void @linux_write(i64 %fd, i8* %addr, i64 %size)

		ret void ; bug
}
define i64 @add__int_int(i64 %x, i64 %y) {
	start:
%result = add i64 %x, %y
ret i64 %result
}
define i64 @sub__int_int(i64 %x, i64 %y) {
	start:
%result = sub i64 %x, %y
ret i64 %result
}
define i64 @mul__int_int(i64 %x, i64 %y) {
	start:
%result = mul i64 %x, %y
ret i64 %result
}
define float @div__int_int(i64 %x, i64 %y) {
	start:

%x_float = sitofp i64 %x to float
%y_float = sitofp i64 %y to float

%result = fdiv float %x_float, %y_float

ret float %result
}
define i64 @and__int_int(i64 %x, i64 %y) {
	start:
%result = and i64 %x, %y
ret i64 %result
}
define i64 @or__int_int(i64 %x, i64 %y) {
	start:
%result = or i64 %x, %y
ret i64 %result
}
define i64 @xor__int_int(i64 %x, i64 %y) {
	start:
%result = xor i64 %x, %y
ret i64 %result
}
define i64 @not__int(i64 %x) {
	start:
%result = xor i64 %x, -1
ret i64 %result
}
define i1 @eq__int_int(i64 %x, i64 %y) {
	start:
%result = icmp eq i64 %x, %y
ret i1 %result
}
define i1 @gt__int_int(i64 %x, i64 %y) {
	start:
%result = icmp sgt i64 %x, %y
ret i1 %result
}
define i1 @ge__int_int(i64 %x, i64 %y) {
	start:
%result = icmp sge i64 %x, %y
ret i1 %result
}
define i1 @lt__int_int(i64 %x, i64 %y) {
	start:
%result = icmp slt i64 %x, %y
ret i1 %result
}
define i1 @le__int_int(i64 %x, i64 %y) {
	start:
%result = icmp sle i64 %x, %y
ret i1 %result
}
define i64 @shl__int_int(i64 %x, i64 %y) {
	start:
%result = shl i64 %x, %y
ret i64 %result
}
define i64 @shr__int_int(i64 %x, i64 %y) {
	start:
%result = lshr i64 %x, %y
ret i64 %result
}
define i64 @add__uint_uint(i64 %x, i64 %y) {
	start:
%result = add i64 %x, %y
ret i64 %result
}
define i64 @sub__uint_uint(i64 %x, i64 %y) {
	start:
%result = sub i64 %x, %y
ret i64 %result
}
define i64 @mul__uint_uint(i64 %x, i64 %y) {
	start:
%result = mul i64 %x, %y
ret i64 %result
}
define float @div__uint_uint(i64 %x, i64 %y) {
	start:

%x_float = sitofp i64 %x to float
%y_float = sitofp i64 %y to float

%result = fdiv float %x_float, %y_float

ret float %result
}
define i64 @and__uint_uint(i64 %x, i64 %y) {
	start:
%result = and i64 %x, %y
ret i64 %result
}
define i64 @or__uint_uint(i64 %x, i64 %y) {
	start:
%result = or i64 %x, %y
ret i64 %result
}
define i64 @xor__uint_uint(i64 %x, i64 %y) {
	start:
%result = xor i64 %x, %y
ret i64 %result
}
define i64 @not__uint(i64 %x) {
	start:
%result = xor i64 %x, -1
ret i64 %result
}
define i1 @eq__uint_uint(i64 %x, i64 %y) {
	start:
%result = icmp eq i64 %x, %y
ret i1 %result
}
define i1 @gt__uint_uint(i64 %x, i64 %y) {
	start:
%result = icmp ugt i64 %x, %y
ret i1 %result
}
define i1 @ge__uint_uint(i64 %x, i64 %y) {
	start:
%result = icmp uge i64 %x, %y
ret i1 %result
}
define i1 @lt__uint_uint(i64 %x, i64 %y) {
	start:
%result = icmp ult i64 %x, %y
ret i1 %result
}
define i1 @le__uint_uint(i64 %x, i64 %y) {
	start:
%result = icmp ule i64 %x, %y
ret i1 %result
}
define i64 @shl__uint_int(i64 %x, i64 %y) {
	start:
%result = shl i64 %x, %y
ret i64 %result
}
define i64 @shr__uint_int(i64 %x, i64 %y) {
	start:
%result = lshr i64 %x, %y
ret i64 %result
}
define i8 @add__byte_byte(i8 %x, i8 %y) {
	start:
%result = add i8 %x, %y
ret i8 %result
}
define float @add__float_float(float %x, float %y) {
	start:
%result = fadd float %x, %y
ret float %result
}
define float @sub__float_float(float %x, float %y) {
	start:
%result = fsub float %x, %y
ret float %result
}
define float @mul__float_float(float %x, float %y) {
	start:
%result = fmul float %x, %y
ret float %result
}
define float @div__float_float(float %x, float %y) {
	start:
%result = fdiv float %x, %y
ret float %result
}
define i1 @eq__float_float(float %x, float %y) {
	start:
%result = fcmp oeq float %x, %y
ret i1 %result
}
define i1 @gt__float_float(float %x, float %y) {
	start:
%result = fcmp ogt float %x, %y
ret i1 %result
}
define i1 @ge__float_float(float %x, float %y) {
	start:
%result = fcmp oge float %x, %y
ret i1 %result
}
define i1 @lt__float_float(float %x, float %y) {
	start:
%result = fcmp olt float %x, %y
ret i1 %result
}
define i1 @le__float_float(float %x, float %y) {
	start:
%result = fcmp ole float %x, %y
ret i1 %result
}
define i1 @eq__bool_bool(i1 %x, i1 %y) {
	start:
%result = icmp eq i1 %x, %y
ret i1 %result
}
define i1 @and__bool_bool(i1 %x, i1 %y) {
	start:
%result = and i1 %x, %y
ret i1 %result
}
define i1 @or__bool_bool(i1 %x, i1 %y) {
	start:
%result = or i1 %x, %y
ret i1 %result
}
define i1 @xor__bool_bool(i1 %x, i1 %y) {
	start:
%result = xor i1 %x, %y
ret i1 %result
}
define i1 @not__bool(i1 %x) {
	start:
%result = xor i1 %x, -1
ret i1 %result
}
@main_onetwo = constant i8 12
@main_threefour = constant i8 34
define i8 @main() {
	start:
		; load value of constant "onetwo"
		%onetwo = load i8, i8* @main_onetwo

		; load value of constant "threefour"
		%threefour = load i8, i8* @main_threefour

		%result = call i8 @add__byte_byte(i8 %onetwo, i8 %threefour)
	ret i64 %result
}