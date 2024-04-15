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
				println("FORWARD: Error sending data")
				return
			}
		}
		for {
			buf := make([]byte, 10240)
			err := socket.SetReadDeadline(time.Now().Add(time.Second))
			if err != nil {
				break
			}
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
