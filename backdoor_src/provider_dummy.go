package main

import (
	"net/http"
	"io/ioutil"
	"encoding/json"
	"strings"
	"bytes"
)

type GetEndpointFormat struct {
	Packets []string `json:"elements"`
}

func (e GetEndpointFormat) ExtractPackets() ([]Packet, error) {
	var packets []Packet
	for _, rawPacket := range e.Packets {
		packet, err := ParsePacket(rawPacket)
		if err != nil {
			return []Packet{}, err
		}
		packets = append(packets, packet)
	}
	return packets, nil
}

func CustomGetPackets(p Provider) ([]Packet, error) {
	// Get data	from server
	resp, err := http.Get("http://127.0.0.1:8000/in")
	if err != nil {
		println("ERROR: Failed to connect to server", err.Error())
		return []Packet{}, err
	}
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		println("ERROR: Failed to read server response", err.Error())
		return []Packet{}, err
	}
	var rawData GetEndpointFormat
	err = json.Unmarshal([]byte(body), &rawData)
	if err != nil {
		println("ERROR: Failed to parse server response", err.Error())
		return []Packet{}, err
	}
	packets, err := rawData.ExtractPackets()
	if err != nil {
		println("ERROR: Failed to extract packets", err.Error())
		return []Packet{}, err
	}
	return packets, nil
}

func CustomSendPackets(p Provider, packets []Packet) error {
	results := []string{}
	for _, packet := range packets {
		results = append(results, string(packet.Encode()))
	}
	payload := "{\"elements\": [\"" + strings.Join(results, ",") + "\"]}"
	if len(packets) == 0 {
		return nil
	}
	_, err := http.Post("http://127.0.0.1:8000/out", "application/json", bytes.NewBuffer([]byte(payload)))
	if err != nil {
		return err
	}
	return nil
}
