package main

import (
	"strings"
	"time"
)

func main() {
	tunnels := make(map[string]*Tunnel)
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
			if packetLength+len(packet.TunnelID) == configData.PacketSize && packet.Content[packetLength-1] == '!' {
				continue
			}
			if packet.TunnelID == "system" {
				newTunnelData := strings.SplitN(string(buffers[packet.TunnelID]), ":", 2)
				tunnelType := newTunnelData[0]
				tunnelID := newTunnelData[1]
				println("MAIN: Received new tunnel request with ID:", tunnelID)
				tunnel := NewTunnel(tunnelType)
				tunnels[tunnelID] = &tunnel
				go tunnels[tunnelID].Handle()
				outbound = append(outbound, BuildPacket("system", []byte("OK"), configData)...)
			} else {
				println("MAIN: Received data for tunnel", packet.TunnelID)
				if _, ok := tunnels[packet.TunnelID]; !ok {
					println("MAIN: Tunnel", packet.TunnelID, "does not exist")
				} else {
					tunnels[packet.TunnelID].PutIn(buffers[packet.TunnelID])
				}
			}
			buffers[packet.TunnelID] = []byte{}
		}

		// Oubout
		for tunnelID, tunnel := range tunnels {
			// Check activity
			if time.Now().Unix()-tunnel.Lastseen > configData.Timeout {
				println("MAIN: Tunnel", tunnelID, "timed out")
				delete(tunnels, tunnelID)
				continue
			}
			// Check data
			data := tunnel.GetOut(false)
			if data == nil {
				continue
			}
			outbound = append(outbound, BuildPacket(tunnelID, data, configData)...)
		}
		// TODO: Implement packet number limit
		if len(outbound) > 0 {
			err = provider.SendPackets(outbound)
			if err != nil {
				println("ERROR: Failed to send packets", err.Error())
				Fail(3)
			}
		}

		println("MAIN: Delay set to", configData.CurrentDelay, "ms")
		time.Sleep(time.Duration(configData.CurrentDelay) * time.Millisecond)
		if len(inbound) == 0 && len(outbound) == 0 {
			configData.CurrentDelay = int(float64(configData.CurrentDelay) * (1 + configData.FactorDelay))
			if configData.CurrentDelay > configData.MaxDelay {
				configData.CurrentDelay = configData.MaxDelay
			}
		} else {
			configData.CurrentDelay = configData.MinDelay
		}
	}
}
