package main

import (
	"encoding/json"
)

var (
	rawConfig = `{"delay":1000}`
)

type Config struct {
	Delay int `json:"delay"`
}

func loadConfig() (Config, error) {
	var config Config
	err := json.Unmarshal([]byte(rawConfig), &config)
	return config, err
}
