package main

import (
 	"time"
	"strings"
	"os"
)

func Fail(errorcode int) {
	println("error", errorcode)
	os.Exit(1)
}

func main() {
	tunnels := make(map[string]Tunnel)

	// Load config
	configData, err := loadConfig()
	if err != nil {
		println("ERROR: Failed to load config", err.Error())
		Fail(1)
	}

	// Create provider
	provider := Provider{configData}

	// Main loop
	for {
		var inbound []Packet
		var outbound []Packet

		// Inbound
		inbound, err := provider.GetPackets()
		if err != nil {
			println("ERROR: Failed to get packets", err.Error())
			Fail(2)
		}
		for _, packet := range inbound {
			if packet.TunnelID == "system" {
				newTunnelData := strings.SplitN(string(packet.Content), ":", 2)
				tunnelType := newTunnelData[0]
				tunnelID := newTunnelData[1]
				println("MAIN: Received new tunnel request with ID:", tunnelID)
				tunnels[tunnelID] = Tunnel{make(chan []byte), make(chan []byte), tunnelType}
				go tunnels[tunnelID].Handle()
				outbound = append(outbound, Packet{"system", []byte("OK")})
			} else {
				println("MAIN: Received data for tunnel", packet.TunnelID)
				tunnels[packet.TunnelID].Input <- packet.Content
			}
		}

		// Oubout
		for tunnelID, tunnel := range tunnels {
			select {
			case data := <-tunnel.Output:
				outbound = append(outbound, Packet{tunnelID, data})
			default:
				continue
			}
		}
		err = provider.SendPackets(outbound)
		if err != nil {
			println("ERROR: Failed to send packets", err.Error())
			Fail(3)
		}


		// TODO: Increase delay if both inbound and outbound are empty
		time.Sleep(time.Duration(configData.Delay) * time.Millisecond)
	}
}
