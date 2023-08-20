fn bin (i int  base uint) Str
        # initialized arrays
        #(Array byte) buffer = (1 2 3)
        #(Array byte) buffer = (20 ** 0x00)

        # arrays with Opt with default value
        #(Array (Opt byte)) buffer = (20 ** 0)

        # arrays with Opt without default value
        #(Array (Opt byte)) buffer = (20 ** ?)

        # uninitialized arrays
        (Array byte) buffer = (64 ** ?)

        int buffer_index = (end buffer)

	fn loop ()
		mut byte current_bit = (or i 1)

		(buffer (buffer_index)) = current_bit + 0x30

		i >> 1
		buffer_index -= 1

		if buffer_index >= 0
			loop ()
	loop ()

	ret Str buffer


fn octal (i int) Str
	#

fn decimal (i int) Str
	#

fn hex (i int) Str
	#

fn main ()
	#
