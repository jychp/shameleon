package main

import (
	"net"
	"strings"
	"time"
	"errors"
	"io"
)

func HandleForward(tunnel Tunnel) {
	data :=  <-tunnel.Input
	addr := strings.SplitN(string(data), "!", 2)
	dstAddr := addr[0]
	dstPort := addr[1]
	println("FORWARD: New connection to", dstAddr, ":", dstPort)
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
				println("Error sending data")
				return
			}
		default:
		}
		outputBuffer := []byte{}
		for {
			buf := make([]byte, 1024)
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
				println(buf[:mLen])
				outputBuffer = append(outputBuffer, buf[:mLen]...)
			}
			if mLen < 1024 {
				println("FORWARD: Sending", len(outputBuffer), "bytes")
				println(outputBuffer)
				tunnel.Output <- outputBuffer
				break
			} else {
				println("FORWARD: Sending", len(outputBuffer), "bytes")
				println(outputBuffer)
				tunnel.Output <- outputBuffer
				break
			}
		}
	}
}
