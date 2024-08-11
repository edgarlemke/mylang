TUnion Result :=
	bool
	int
	float


fn main () int
	Result result := 46
	mut int x := 0

	handle result
		bool
			x = -1
		int
			x = result
		float
			x = -2

	x
