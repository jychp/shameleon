package main

import (
	"time"
)

type Tunnel struct {
	Input		chan []byte
	Output		chan []byte
	Kind    	string
	Lastseen 	int64
}

func NewTunnel(kind string) Tunnel {
	return Tunnel{make(chan []byte), make(chan []byte), kind, time.Now().Unix()}
}

func (t Tunnel) Handle() {
	switch t.Kind {
	case "sh":
		HandleShell(t)
	case "sx":
		HandleForward(t)
	case "lf":
		HandleForward(t)
	default:
		println("ERROR: Unknown tunnel type", t.Kind)
		Fail(4)
	}
}
