import math

import networkx as nx

# silence ccxt import errors.
from mock_import import mock_import
with mock_import():
    from peregrinearb import bellman_ford_multi, calculate_profit_ratio_for_path


def print_profit_opportunity_for_path_multi(graph: nx.Graph, path, print_output=True, round_to=None, shorten=False):
    """
    The only difference between this function and the function in utils/general.py is that the print statement
    specifies the exchange name. It assumes all edges in graph and in path have exchange_name and market_name
    attributes.
    """
    if not path:
        return

    money = 100
    result = ''
    result += "Starting with %(money)i in %(currency)s\n" % {"money": money, "currency": path[0]}

    for i in range(len(path)):
        if i + 1 < len(path):
            start = path[i]
            end = path[i + 1]
            rate = math.exp(-graph[start][end]['weight'])
            money *= rate
            if round_to is None:
                result += "{:4s} to {:4s} at {:18.8f} = {:18.8f}".format(start, end, rate, money)
            else:
                result += "{} to {} at {} = {}".format(start, end, round(rate, round_to), round(money, round_to))
            if not shorten:
                result += " on {:15s} for {}".format(graph[start][end]['exchange_name'], graph[start][end]['market_name'])

            result += '\n'

    if print_output:
        print(result)
    return result


class TickerObserver(object):

    def __init__(self):
        self.exchanges = set()

    def register(self, exchange):
        self.exchanges.add(exchange)

    def notify(self):
        # print(self.__class__.__name__, 'notify:', self.exchanges)
        graph = self.build_graph()
        graph, paths = bellman_ford_multi(graph, 'btc', loop_from_source=False, unique_paths=True, ensure_profit=False)

        for path in paths:
            total = calculate_profit_ratio_for_path(graph, path)
            total_p = (total - 1) * 100.0
            if True: #total_p > 0:
                # print(total, path)
                print('{:5.3}%'.format(total_p), ' -> '.join([p for p in path]))
                print_profit_opportunity_for_path_multi(graph, path)

    def build_graph(self) -> nx.MultiDiGraph:
        graph = nx.MultiDiGraph()

        fee_scalar = 1  # - exchange['fee'] todo add fees

        for exchange in self.exchanges:
            for market, ticker in exchange.ticker.items():
                base_currency, quote_currency = market.split('_')

                bid = ticker.get('best_bid', None)
                ask = ticker.get('best_ask', None)

                if bid is not None and ask is not None:
                    if True:  # TODO
                        graph.add_edge(base_currency, quote_currency,
                                       market_name=market,
                                       exchange_name=exchange.__class__.__name__,
                                       weight=-math.log(fee_scalar * bid))

                        graph.add_edge(quote_currency, base_currency,
                                       market_name=market,
                                       exchange_name=exchange.__class__.__name__,
                                       weight=-math.log(fee_scalar * 1 / ask))
                    else:
                        graph.add_edge(base_currency, quote_currency,
                                       market_name=market,
                                       exchange_name=exchange.__class__.__name__,
                                       weight=-fee_scalar * bid)

                        graph.add_edge(quote_currency, base_currency,
                                       market_name=market,
                                       exchange_name=exchange.__class__.__name__,
                                       weight=-fee_scalar * 1 / ask)

        return graph
