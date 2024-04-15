package main

import (
	"time"
)

type Tunnel struct {
	Input    chan []byte
	Output   chan []byte
	Kind     string
	Lastseen int64
}

func NewTunnel(kind string) Tunnel {
	return Tunnel{make(chan []byte, 100), make(chan []byte, 100), kind, time.Now().Unix()}
}

func (t *Tunnel) Handle() {
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

func (t *Tunnel) PutIn(data []byte) {
	t.Lastseen = time.Now().Unix()
	println("TUNNEL: Start PUTIN ...")
	t.Input <- data
	println("TUNNEL: Data PUTIN")
}

func (t *Tunnel) PutOut(data []byte) {
	t.Lastseen = time.Now().Unix()
	println("TUNNEL: Start PUTOUT ...")
	t.Output <- data
	println("TUNNEL: Data PUTOUT")
}

func (t *Tunnel) GetIn(blocking bool) []byte {
	for {
		select {
		case data := <-t.Input:
			return data
		default:
			if !blocking {
				return nil
			}
		}
	}
}

func (t *Tunnel) GetOut(blocking bool) []byte {
	for {
		select {
		case data := <-t.Output:
			return data
		default:
			if !blocking {
				return nil
			}
		}
	}
}
