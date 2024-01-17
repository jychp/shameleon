package main

import (
	"encoding/json"
	"encoding/base64"
)

var (
	rawConfig = `eyJkZWxheSI6MTAwMCwic2VjcmV0IjoiZmh1cHI1QUU5aHBDTUNsSzI2cWFLQ3ZtSUdLalU4aE16NlJUMDBZTXZqND0iLCJwYWNrZXRfc2l6ZSI6MTAwMDAsInBhY2tldF9udW1iZXIiOjAsInRpbWVvdXQiOjYwLCJjdXN0b20iOnsidXJsIjoiPENIQU5HRV9NRT4iLCJ1c2VyIjoiPENIQU5HRV9NRT4iLCJ0b2tlbiI6IjxDSEFOR0VfTUU+IiwibGFiZWwiOiJzZXZlcml0eSIsImxhYmVsX2luIjoibG93IiwibGFiZWxfb3V0IjoiaGlnaCJ9fQ==`
)

type Config struct {
	Delay 			int 				`json:"delay"`
	Secret 			string 				`json:"secret"`
	PacketSize 		int 				`json:"packet_size"`
	PacketNumber 	int 				`json:"packet_number"`
	Timeout     	int64   			`json:"timeout"`
	Custom          map[string]string	`json:"custom"`
}

func loadConfig() (Config, error) {
	var config Config
	decoded, err := base64.StdEncoding.DecodeString(rawConfig)
	if err != nil {
		return config, err
	}
	err = json.Unmarshal([]byte(decoded), &config)
	return config, err
}
