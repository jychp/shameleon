package main

import (
	"time"
)

type Provider struct {
	Config		Config
	LastPacket	int64
}

func NewProvider(config Config) Provider {
	return Provider{config, time.Now().UnixNano() - 1000000000}
}

func (p *Provider) GetPackets() ([]Packet, error) {
	packets, err := CustomGetPackets(p)
	return packets, err
}

func (p *Provider) SendPackets(packets []Packet) error {
	err := CustomSendPackets(p, packets)
	return err
}
