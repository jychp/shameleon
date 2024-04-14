package main

import (
	"net"
	"strings"
	"time"
	"errors"
	"io"
)

func HandleLforward(tunnel Tunnel) {
	data :=  <-tunnel.Input
	addr := strings.SplitN(string(data), "!", 2)
	dstAddr := addr[0]
	dstPort := addr[1]
	println("Lforward: New connection to", dstAddr, ":", dstPort)
	socket, err := net.Dial("tcp", dstAddr + ":" + dstPort)
	if err != nil {
		tunnel.Output <- []byte("KO")
	} else {
		tunnel.Output <- []byte("OK")
	}

	for {
		select {
		case data := <-tunnel.Input:
			_, err = socket.Write(data)
			if err != nil {
				println("Lforward: Error sending data")
				return
			}
		default:
		}
		buf := make([]byte, 1024)
		socket.SetReadDeadline(time.Now().Add(time.Second))
		mLen, err := socket.Read(buf)
		if err != nil {
			if errors.Is(err, io.EOF) {
				return
			}
		}
		if mLen > 0 {
			tunnel.Output <- buf[:mLen]
		}
	}
}
