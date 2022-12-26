import json, argparse
import pandas as pd

from substrateinterface import SubstrateInterface, Keypair
from substrateinterface.exceptions import SubstrateRequestException


def check_balance(current, need, minimal_balance):
    return True if current > (need + minimal_balance) else False


def main(config_path=None, targets_path=None, only_kaa=False):
    # Read main config 
    config_file = open(config_path)
    config = json.load(config_file)
    config_file.close()

    # Read targets csv
    targets = pd.read_csv(targets_path)
    targets = targets.dropna()
    targets['amount'] = (targets['Количество (KAA)']*100).astype(int)
    print(targets)

    substrate = SubstrateInterface(
        url=config['endpoint']
    )
    keypair = Keypair.create_from_mnemonic(config['seed'], ss58_format=2)
    print(keypair.ss58_address)

    if not only_kaa:
        # Send existential KSM deposit to the targets
        transfer_ksm_batch = [
            {
                'call_module': 'Balances', 
                'call_function': 'transfer',
                'call_args':  {
                    'dest': row['Адрес кошелька'],
                    'value': config['ksm_existential_deposit']
                }
            } for index, row in targets.iterrows()
        ]

        transfer_ksm_batch_call = substrate.compose_call(
            call_module='Utility', 
            call_function='batch', 
            call_params={
                'calls': transfer_ksm_batch
            }
        )
        print(transfer_ksm_batch_call)

        transfer_ksm_batch_extrinsic = substrate.create_signed_extrinsic(call=transfer_ksm_batch_call, keypair=keypair)

        try:
            print("\nSend KSM existential deposit to targets: ")
            receipt = substrate.submit_extrinsic(transfer_ksm_batch_extrinsic, wait_for_inclusion=True)
            print("Extrinsic '{}' sent and included in block '{}'. Weight: '{}', total fee: '{}'.".format(receipt.extrinsic_hash, receipt.block_hash, receipt.weight, receipt.total_fee_amount))

        except SubstrateRequestException as e:
            print("Failed to send: {}".format(e))

    
    # Send assets to the targets
    transfer_assets_batch = [
        {
            'call_module': 'Assets', 
            'call_function': 'transfer', 
            'call_args': {
                'id': config['asset_id'],
                'target': row['Адрес кошелька'],
                'amount': row['amount']
            } 
        } for index, row in targets.iterrows()
    ]

    transfer_assets_batch_call = substrate.compose_call(
        call_module='Utility', 
        call_function='batch', 
        call_params={
            'calls': transfer_assets_batch
        }
    )
    print(transfer_assets_batch_call)

    transfer_assets_batch_extrinsic = substrate.create_signed_extrinsic(call=transfer_assets_batch_call, keypair=keypair)

    try:
        print("\nSend KAA asset to targets: ")
        receipt = substrate.submit_extrinsic(transfer_assets_batch_extrinsic, wait_for_inclusion=True)
        print("Extrinsic '{}' sent and included in block '{}'. Weight: '{}', total fee: '{}'.".format(receipt.extrinsic_hash, receipt.block_hash, receipt.weight, receipt.total_fee_amount))

    except SubstrateRequestException as e:
        print("Failed to send: {}".format(e))

    return None


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('--config_path', '-C', required=True, help='Path to JSON config file')
    parser.add_argument('--targets_path', '-T', required=True, help='Path to CSV targets file')
    parser.add_argument('--only_kaa', action=argparse.BooleanOptionalAction, default=False)

    args=parser.parse_args()

    main(config_path=args.config_path, targets_path=args.targets_path, only_kaa=args.only_kaa)