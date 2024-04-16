package main

import (
	"encoding/base64"
	"encoding/json"
)

var (
	rawConfig = `eyJkZWxheSI6MTAwMCwic2VjcmV0IjoiZmh1cHI1QUU5aHBDTUNsSzI2cWFLQ3ZtSUdLalU4aE16NlJUMDBZTXZqND0iLCJwYWNrZXRfc2l6ZSI6MTAwMDAsInBhY2tldF9udW1iZXIiOjAsInRpbWVvdXQiOjYwLCJjdXN0b20iOnsidXJsIjoiPENIQU5HRV9NRT4iLCJ1c2VyIjoiPENIQU5HRV9NRT4iLCJ0b2tlbiI6IjxDSEFOR0VfTUU+IiwibGFiZWwiOiJzZXZlcml0eSIsImxhYmVsX2luIjoibG93IiwibGFiZWxfb3V0IjoiaGlnaCJ9fQ==`
)

type Config struct {
	Secret       string            `json:"secret"`
	PacketSize   int               `json:"packet_size"`
	PacketNumber int               `json:"packet_number"`
	Timeout      int64             `json:"timeout"`
	Custom       map[string]string `json:"custom"`
	MinDelay     int               `json:"min_delay"`
	FactorDelay  float64           `json:"factor_delay"`
	MaxDelay     int               `json:"max_delay"`
	CurrentDelay int               `json:"current_delay"`
}

func loadConfig() (Config, error) {
	var config Config
	decoded, err := base64.StdEncoding.DecodeString(rawConfig)
	if err != nil {
		return config, err
	}
	err = json.Unmarshal([]byte(decoded), &config)
	config.CurrentDelay = config.MinDelay
	return config, err
}
