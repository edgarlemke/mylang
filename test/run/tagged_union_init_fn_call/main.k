TUnion Result :=
	bool
	int

fn somefn () Result
	Result result := 1
	result

fn main () int
	Result result := (somefn)
	mut int x := 0

	handle result
		bool
			x = -1
		int
			x = 46

	x
