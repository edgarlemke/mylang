struct MyStruct :=
	size int

struct MyStruct1 :=
	mystruct MyStruct

struct MyStruct2 :=
	mystruct MyStruct1

fn main () int
	MyStruct mystruct0 := (46)
	MyStruct1 mystruct1 := (mystruct0)
	MyStruct2 mystruct2 := (mystruct1)

	int result := mystruct1 . mystruct . size

	result
