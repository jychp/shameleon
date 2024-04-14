package main

import (
 	"time"
	"strings"
)

func main() {
	tunnels := make(map[string]Tunnel)
	buffers := make(map[string][]byte)
	buffers["system"] = []byte{}

	// Load config
	configData, err := loadConfig()
	if err != nil {
		println("ERROR: Failed to load config", err.Error())
		Fail(1)
	}

	// Create provider
	provider := NewProvider(configData)

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
			buffers[packet.TunnelID] = append(buffers[packet.TunnelID], packet.Content...)
			packetLength := len(packet.Content)
			if packetLength + len(packet.TunnelID) == configData.PacketSize && packet.Content[packetLength-1] == '!' {
				continue
			}
			if packet.TunnelID == "system" {
				newTunnelData := strings.SplitN(string(buffers[packet.TunnelID]), ":", 2)
				tunnelType := newTunnelData[0]
				tunnelID := newTunnelData[1]
				println("MAIN: Received new tunnel request with ID:", tunnelID)
				tunnels[tunnelID] = NewTunnel(tunnelType)
				go tunnels[tunnelID].Handle()
				outbound = append(outbound, BuildPacket("system", []byte("OK"), configData)...)
			} else {
				println("MAIN: Received data for tunnel", packet.TunnelID)
				if _, ok := tunnels[packet.TunnelID]; !ok {
					println("MAIN: Tunnel", packet.TunnelID, "does not exist")
				} else {
					if tunnel, ok := tunnels[packet.TunnelID]; ok {
						tunnel.Lastseen = time.Now().Unix()
						tunnel.Input <- buffers[packet.TunnelID]
						tunnels[packet.TunnelID] = tunnel
					}
				}
			}
			buffers[packet.TunnelID] = []byte{}
		}

		// Oubout
		for tunnelID, tunnel := range tunnels {
			// Check activity
			if time.Now().Unix() - tunnel.Lastseen > configData.Timeout {
				println("MAIN: Tunnel", tunnelID, "timed out")
				delete(tunnels, tunnelID)
				continue
			}
			// Check data
			select {
			case data := <-tunnel.Output:
				outbound = append(outbound, BuildPacket(tunnelID, data, configData)...)
			default:
				continue
			}
		}
		// TODO: Implement packet number limit
		if len(outbound) > 0 {
			err = provider.SendPackets(outbound)
			if err != nil {
				println("ERROR: Failed to send packets", err.Error())
				Fail(3)
			}
		}

		// TODO: Increase delay if both inbound and outbound are empty
		time.Sleep(time.Duration(configData.Delay) * time.Millisecond)
	}
}
