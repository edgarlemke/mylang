fn loop (i int, buffer mut (Array byte), index int)
	mut byte value := 0x30
	byte one := 1

	if (and i 1) == 1
		value = value + one

	set_array_member buffer (index) value

	if index > 0
		loop (shr (or i 0) 1) buffer (sub index 1)


fn bin (i int) (Array byte)
	int buffer_size := 64
	mut (Array byte 64) buffer := unset
	int buffer_index := buffer_size - 1

	loop i buffer buffer_index

	buffer


fn main ()
	print (bin 1234567890)

