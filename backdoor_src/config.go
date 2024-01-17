package main

import (
	"encoding/json"
)

var (
	rawConfig = `{"delay":1000,"secret":"fhupr5AE9hpCMClK26qaKCvmIGKjU8hMz6RT00YMvj4=","packet_size":10000,"packet_number":0,"timeout":60,"custom":{"url":"https://logs-prod-012.grafana.net","user":"<CHANGEME>","token":"<CHANGEME>","label":"severity","label_in":"low","label_out":"high"}}`
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
	err := json.Unmarshal([]byte(rawConfig), &config)
	return config, err
}
