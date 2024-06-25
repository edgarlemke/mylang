struct MyStruct :=
	int size

fn main ()
	mut MyStruct mystruct := unset
	set_struct_member mystruct size 1
	get_struct_member mystruct size
