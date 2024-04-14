package main

import (
	"net"
	"strings"
	"time"
	"fmt"
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
			println("Lforward: Sending data")
			_, err = socket.Write(data)
			if err != nil {
				fmt.Println("Lforward: Error sending data")
				return
			}
		default:
		}
		println("Keep going")
		buf := make([]byte, 1024)
		socket.SetReadDeadline(time.Now().Add(time.Second))
		mLen, err := socket.Read(buf)
		if err != nil {
			if errors.Is(err, io.EOF) {
				return
			}
		}
		if mLen > 0 {
			println("Lforward: Receiving data")
			println("Lforward: Received", mLen, "bytes")
			println(string(buf[:mLen]))
			tunnel.Output <- buf[:mLen]
		}
	}
}
