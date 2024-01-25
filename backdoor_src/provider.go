package main

type Provider struct {
	Config		Config
}

func (p Provider) GetPackets() ([]Packet, error) {
	packets, err := CustomGetPackets(p)
	return packets, err
}

func (p Provider) SendPackets(packets []Packet) error {
	err := CustomSendPackets(p, packets)
	return err
}
