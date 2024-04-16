# shameleon

Source code for blog posts on https://jychp.medium.com/

## Error codes
- 1: Failed to load config
- 2: Failed to get packets
- 3: Failed to send packets
- 4: Unknown tunnel type
- 5: Failed to encrypt data

## Testing
1. Launch Dummy API Server
```bash
uvicorn dummy_server:app --reload
```

2. Launch backdoor
```bash
cd backdoor_src/
go run .
```

3. Launch client
```bash
poetry run python3 client.py -p ./profiles dummy
```

## Building
1. Create profile
2. Launch builder.py
```
python3 builder.py -p ./profiles -o . dummy linux
```
