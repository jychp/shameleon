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
	encrypted   bool
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
	packetLength := len(packetContent)
	var msg []byte
	if packetContent[packetLength-1] == '!' {
		msg = fernet.VerifyAndDecrypt([]byte(packetContent[:packetLength-1]), 60*time.Second, k)
		msg = append(msg, []byte("!")...)
	} else {
		msg = fernet.VerifyAndDecrypt([]byte(packetContent), 60*time.Second, k)
	}
	packet := Packet{tunnelID, msg, false}
    return packet, nil
}

func BuildPacket(tunnelID string, content []byte, config Config) []Packet {
	result := []Packet{}
	k := fernet.MustDecodeKeys(config.Secret)
	encrypted, err := fernet.EncryptAndSign(content, k[0])
	if err != nil {
		println("ERROR: Failed to encrypt packet", err.Error())
		Fail(5)
	}
	if config.PacketSize == 0 {
		result = append(result, Packet{tunnelID, encrypted, true})
		return result
	}
	for len(encrypted) > 0 {
		if len(encrypted) + len(tunnelID) + 2 <= config.PacketSize {
			result = append(result, Packet{tunnelID, encrypted, true})
			return result
		}
		chunk := append([]byte(nil), encrypted[:config.PacketSize - len(tunnelID)]...)
		encrypted = encrypted[len(chunk):]
		chunk = append(chunk, []byte("!")...)
		result = append(result, Packet{tunnelID, chunk, true})

	}
	return result
}

func (p Packet) Format() string {
	packetRaw := p.TunnelID + ":" + string(p.Content)
	return packetRaw
}
