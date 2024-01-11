package main

import (
	"encoding/json"
)

var (
	rawConfig = `{"delay":1000,"secret":"fhupr5AE9hpCMClK26qaKCvmIGKjU8hMz6RT00YMvj4=","packet_size":1024}`
)

type Config struct {
	Delay 		int 	`json:"delay"`
	Secret 		string 	`json:"secret"`
	PacketSize 	int 	`json:"packet_size"`
}

func loadConfig() (Config, error) {
	var config Config
	err := json.Unmarshal([]byte(rawConfig), &config)
	return config, err
}
