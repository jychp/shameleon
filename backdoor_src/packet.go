package main

import (
	"strings"
	"errors"
	"time"
	"github.com/fernet/fernet-go"
)

type Packet struct {
	TunnelID	string
	Content		[]byte
}

func ParsePacket(rawPacket string, config Config) (Packet, error) {
	// Parse raw
	packetArray := strings.SplitN(rawPacket, ":", 2)
	if len(packetArray) != 2 {
		return Packet{}, errors.New("Invalid packet")
	}
	tunnelID := packetArray[0]
	packetContent := packetArray[1]
	k := fernet.MustDecodeKeys(config.Secret)
	msg := fernet.VerifyAndDecrypt([]byte(packetContent), 60*time.Second, k)
	packet := Packet{tunnelID, msg}
    return packet, nil
}

func (p Packet) Encode(config Config) ([]byte, error) {
	k := fernet.MustDecodeKeys(config.Secret)
	packetContent, err := fernet.EncryptAndSign(p.Content, k[0])
	if err != nil {
		return []byte{}, err
	}
	packetRaw := p.TunnelID + ":" + string(packetContent)
	return []byte(packetRaw), nil
}
