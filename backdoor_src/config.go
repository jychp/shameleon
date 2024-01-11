package main

import (
	"encoding/json"
)

var (
	rawConfig = `{"delay":1000,"secret":"fhupr5AE9hpCMClK26qaKCvmIGKjU8hMz6RT00YMvj4=","packet_size":1024,"timeout":60}`
)

type Config struct {
	Delay 		int 	`json:"delay"`
	Secret 		string 	`json:"secret"`
	PacketSize 	int 	`json:"packet_size"`
	Timeout     int64   `json:"timeout"`
}

func loadConfig() (Config, error) {
	var config Config
	err := json.Unmarshal([]byte(rawConfig), &config)
	return config, err
}
