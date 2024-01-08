package main

import (
	"strings"
	"errors"
	"encoding/base64"
)

type Packet struct {
	TunnelID	string
	Content		[]byte
}

func ParsePacket(rawPacket string) (Packet, error) {
	packetArray := strings.SplitN(rawPacket, ":", 2)
	if len(packetArray) != 2 {
		return Packet{}, errors.New("Invalid packet")
	}
	tunnelID := packetArray[0]
	packetContent := packetArray[1]
	decodedPacket, err := base64.StdEncoding.DecodeString(packetContent)
	packet := Packet{tunnelID, decodedPacket}
    return packet, err
}

func (p Packet) Encode() []byte {
	packetContent := base64.StdEncoding.EncodeToString(p.Content)
	packetRaw := p.TunnelID + ":" + packetContent
	return []byte(packetRaw)
}
