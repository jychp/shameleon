package main

import (
	"errors"
	"io"
	"net"
	"strings"
	"time"
)

func HandleForward(tunnel *Tunnel) {
	data := tunnel.GetIn(true)
	addr := strings.SplitN(string(data), "!", 2)
	dstAddr := addr[0]
	dstPort := addr[1]
	println("FORWARD: New connection to", dstAddr, ":", dstPort)
	socket, err := net.Dial("tcp", dstAddr+":"+dstPort)
	if err != nil {
		tunnel.PutOut([]byte("KO"))
	} else {
		tunnel.PutOut([]byte("OK"))
	}

	for {
		data = tunnel.GetIn(false)
		if data != nil {
			_, err = socket.Write(data)
			if err != nil {
				println("Error sending data")
				return
			}
		}
		for {
			buf := make([]byte, 10240)
			socket.SetReadDeadline(time.Now().Add(time.Second))
			mLen, err := socket.Read(buf)
			if err != nil {
				if errors.Is(err, io.EOF) {
					return
				}
				break
			}
			if mLen > 0 {
				println("FORWARD: Received", mLen, "bytes")
				tunnel.PutOut(buf[:mLen])
			}
		}
	}
}
