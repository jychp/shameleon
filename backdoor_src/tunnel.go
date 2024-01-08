package main

type Tunnel struct {
	Input	chan []byte
	Output	chan []byte
	Kind    string
	// TODO: Implement lastseen + garbage collection
}

func (t Tunnel) Handle() {
	switch t.Kind {
	case "sh":
		HandleShell(t)
	case "sx":
		println("ERROR: Not yet implemented ;)")
		Fail(9999)
	case "fd":
		println("ERROR: Not yet implemented ;)")
		Fail(9999)
	case "pf":
		println("ERROR: Not yet implemented ;)")
		Fail(9999)
	default:
		println("ERROR: Unknown tunnel type", t.Kind)
		Fail(4)
	}
}
