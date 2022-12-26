# statemine_assets_sender

## Prepare
1) clone repo: ```git clone https://github.com/dergudzon/statemine_assets_sender && cd ./statemine_assets_sender```
2) install requirements: ```pip3 install -r ./requirements.txt```
3) rename `config_example.json` to `config.json` and write your mnemonic instead `%MNEMONIC_HERE%`

## Using

```python3 send_statemine_assets.py -C config.json -T test_targets2.csv```

`-C` is path to the config.json, **required**
`-T` is path to the CSV file imported from Google Sheets, **required**
`--only_kaa` is the parameter for only asset transfer, excluding KSM existential deposit sending, **optional**


