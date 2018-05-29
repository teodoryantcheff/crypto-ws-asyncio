import asyncio

from base import CryptoExchange


class Binance(CryptoExchange):
    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md

    url = 'wss://stream.binance.com:9443'

    all_markets = ['eth_btc', 'ltc_btc', 'bnb_btc', 'neo_btc', 'qtum_eth', 'eos_eth', 'snt_eth', 'bnt_eth', 'bch_btc',
                   'gas_btc', 'bnb_eth', 'btc_usdt', 'eth_usdt', 'hsr_btc', 'oax_eth', 'dnt_eth', 'mco_eth', 'icn_eth',
                   'mco_btc', 'wtc_btc', 'wtc_eth', 'lrc_btc', 'lrc_eth', 'qtum_btc', 'yoyow_btc', 'omg_btc', 'omg_eth',
                   'zrx_btc', 'zrx_eth', 'strat_btc', 'strat_eth', 'sngls_btc', 'sngls_eth', 'bqx_btc', 'bqx_eth',
                   'knc_btc', 'knc_eth', 'fun_btc', 'fun_eth', 'snm_btc', 'snm_eth', 'neo_eth', 'iota_btc', 'iota_eth',
                   'link_btc', 'link_eth', 'xvg_btc', 'xvg_eth', 'salt_btc', 'salt_eth', 'mda_btc', 'mda_eth',
                   'mtl_btc', 'mtl_eth', 'sub_btc', 'sub_eth', 'eos_btc', 'snt_btc', 'etc_eth', 'etc_btc', 'mth_btc',
                   'mth_eth', 'eng_btc', 'eng_eth', 'dnt_btc', 'zec_btc', 'zec_eth', 'bnt_btc', 'ast_btc', 'ast_eth',
                   'dash_btc', 'dash_eth', 'oax_btc', 'icn_btc', 'btg_btc', 'btg_eth', 'evx_btc', 'evx_eth', 'req_btc',
                   'req_eth', 'vib_btc', 'vib_eth', 'hsr_eth', 'trx_btc', 'trx_eth', 'powr_btc', 'powr_eth', 'ark_btc',
                   'ark_eth', 'yoyow_eth', 'xrp_btc', 'xrp_eth', 'mod_btc', 'mod_eth', 'enj_btc', 'enj_eth',
                   'storj_btc', 'storj_eth', 'bnb_usdt', 'ven_bnb', 'yoyow_bnb', 'powr_bnb', 'ven_btc', 'ven_eth',
                   'kmd_btc', 'kmd_eth', 'nuls_bnb', 'rcn_btc', 'rcn_eth', 'rcn_bnb', 'nuls_btc', 'nuls_eth', 'rdn_btc',
                   'rdn_eth', 'rdn_bnb', 'xmr_btc', 'xmr_eth', 'dlt_bnb', 'wtc_bnb', 'dlt_btc', 'dlt_eth', 'amb_btc',
                   'amb_eth', 'amb_bnb', 'bch_eth', 'bch_usdt', 'bch_bnb', 'bat_btc', 'bat_eth', 'bat_bnb', 'bcpt_btc',
                   'bcpt_eth', 'bcpt_bnb', 'arn_btc', 'arn_eth', 'gvt_btc', 'gvt_eth', 'cdt_btc', 'cdt_eth', 'gxs_btc',
                   'gxs_eth', 'neo_usdt', 'neo_bnb', 'poe_btc', 'poe_eth', 'qsp_btc', 'qsp_eth', 'qsp_bnb', 'bts_btc',
                   'bts_eth', 'bts_bnb', 'xzc_btc', 'xzc_eth', 'xzc_bnb', 'lsk_btc', 'lsk_eth', 'lsk_bnb', 'tnt_btc',
                   'tnt_eth', 'fuel_btc', 'fuel_eth', 'mana_btc', 'mana_eth', 'bcd_btc', 'bcd_eth', 'dgd_btc',
                   'dgd_eth', 'iota_bnb', 'adx_btc', 'adx_eth', 'adx_bnb', 'ada_btc', 'ada_eth', 'ppt_btc', 'ppt_eth',
                   'cmt_btc', 'cmt_eth', 'cmt_bnb', 'xlm_btc', 'xlm_eth', 'xlm_bnb', 'cnd_btc', 'cnd_eth', 'cnd_bnb',
                   'lend_btc', 'lend_eth', 'wabi_btc', 'wabi_eth', 'wabi_bnb', 'ltc_eth', 'ltc_usdt', 'ltc_bnb',
                   'tnb_btc', 'tnb_eth', 'waves_btc', 'waves_eth', 'waves_bnb', 'gto_btc', 'gto_eth', 'gto_bnb',
                   'icx_btc', 'icx_eth', 'icx_bnb', 'ost_btc', 'ost_eth', 'ost_bnb', 'elf_btc', 'elf_eth', 'aion_btc',
                   'aion_eth', 'aion_bnb', 'nebl_btc', 'nebl_eth', 'nebl_bnb', 'brd_btc', 'brd_eth', 'brd_bnb',
                   'mco_bnb', 'edo_btc', 'edo_eth', 'wings_btc', 'wings_eth', 'nav_btc', 'nav_eth', 'nav_bnb',
                   'lun_btc', 'lun_eth', 'trig_btc', 'trig_eth', 'trig_bnb', 'appc_btc', 'appc_eth', 'appc_bnb',
                   'vibe_btc', 'vibe_eth', 'rlc_btc', 'rlc_eth', 'rlc_bnb', 'ins_btc', 'ins_eth', 'pivx_btc',
                   'pivx_eth', 'pivx_bnb', 'iost_btc', 'iost_eth', 'chat_btc', 'chat_eth', 'steem_btc', 'steem_eth',
                   'steem_bnb', 'xrb_btc', 'xrb_eth', 'xrb_bnb', 'via_btc', 'via_eth', 'via_bnb', 'blz_btc', 'blz_eth',
                   'blz_bnb', 'ae_btc', 'ae_eth', 'ae_bnb', 'rpx_btc', 'rpx_eth', 'rpx_bnb', 'ncash_btc', 'ncash_eth',
                   'ncash_bnb', 'poa_btc', 'poa_eth', 'poa_bnb', 'zil_btc', 'zil_eth', 'zil_bnb', 'ont_btc', 'ont_eth',
                   'ont_bnb', 'storm_btc', 'storm_eth', 'storm_bnb', 'qtum_bnb', 'qtum_usdt', 'xem_btc', 'xem_eth',
                   'xem_bnb', 'wan_btc', 'wan_eth', 'wan_bnb', 'wpr_btc', 'wpr_eth', 'qlc_btc', 'qlc_eth', 'sys_btc',
                   'sys_eth', 'sys_bnb', 'qlc_bnb', 'grs_btc', 'grs_eth', 'ada_usdt', 'ada_bnb', 'cloak_btc',
                   'cloak_eth', 'gnt_btc', 'gnt_eth', 'gnt_bnb', 'loom_btc', 'loom_eth', 'loom_bnb', 'xrp_usdt',
                   'bcn_btc', 'bcn_eth', 'bcn_bnb', 'rep_btc', 'rep_eth', 'rep_bnb', 'tusd_btc', 'tusd_eth', 'tusd_bnb',
                   'zen_btc', 'zen_eth', 'zen_bnb', 'sky_btc', 'sky_eth', 'sky_bnb', 'eos_usdt', 'eos_bnb', 'cvc_btc',
                   'cvc_eth', 'cvc_bnb']

    # def __init__(self, markets: list):
    #     super().__init__(markets)

    async def connect(self, **kwargs):
        # url params format : "/ws/ethbtc@trade/bnbbtc@trade"
        # todo check https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md#all-market-tickers-stream
        streams = '/'.join([market + '@ticker' for market in self.markets_native]).lower()
        url = self.url + '/ws/' + streams
        await super().connect(url)

    async def subscribe_ticker(self):
        # date streams are passed on cunnect as url params. see subscribe_ticker
        # implemented here to silence the NotImplemented
        pass

    def on_message(self, json_payload):
        if json_payload['e'] == '24hrTicker':
            self.on_ticker(json_payload)

    def on_ticker(self, data):
        symbol = self._market_names_map[data['s']]
        self.update_ticker(
            symbol,
            best_bid=float(data['b']),
            bid_size=float(data['B']),
            best_ask=float(data['a']),
            ask_size=float(data['A']),
            timestamp=int(data['E']),
            last_price=None,
            volume=None,
        )
