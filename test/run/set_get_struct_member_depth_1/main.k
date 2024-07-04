struct MyStruct :=
	size int

struct MyStruct1 :=
	mystruct MyStruct

fn main () int
	MyStruct mystruct0 := (46)
	MyStruct1 mystruct1 := (mystruct0)

	int result := mystruct1 . mystruct . size

	result
