"""Create only a new disposable wallet using the bundled wallet implementation."""
import argparse,os,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--state',type=Path,required=True);a=p.parse_args();a.state.mkdir(parents=True,exist_ok=False)
old=os.path.expanduser;os.path.expanduser=lambda s:str(a.state/'legacy-home')+s[len('~/.electrum-sv'):] if isinstance(s,str) and s.startswith('~/.electrum-sv') else old(s)
sys.path.insert(0,str(a.source))
from electrumsv.simple_config import SimpleConfig
from electrumsv.app_state import AppStateProxy,DefaultApp
from electrumsv.storage import WalletStorage
from electrumsv.wallet import Wallet
from electrumsv import keystore
from electrumsv.mnemonic import generate_bip39_seed
from electrumsv.keystore import bip44_derivation_cointype
from electrumsv.networks import Net
app=AppStateProxy(SimpleConfig(dict(electrum_sv_path=str(a.state/'config'))),'cmdline');app.set_app(DefaultApp())
with app.async_:
    password='disposable-packaged-wallet'
    storage=WalletStorage.create(str(a.state/'test-wallet'),password);wallet=Wallet(storage)
    ks=keystore.from_bip39_seed(generate_bip39_seed(12),'',bip44_derivation_cointype(Net.BIP44_COIN_TYPE,0));ks.update_password(password)
    account=wallet.create_account_from_keystore(ks);account.synchronize();wallet.start(None);wallet.stop()
print('Created new disposable unfunded wallet; no recovery material exported.')
