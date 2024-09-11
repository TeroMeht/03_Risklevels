from ibapi.client import EClient
from ibapi.common import OrderId
from ibapi.order import Order
from ibapi.order_state import OrderState
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from threading import Timer
import pandas as pd

class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
    # Initialize an empty DataFrame to store portfolio data
        self.portfolio_df = pd.DataFrame(columns=[
            'Symbol', 'Position', 'AverageCost', 'AuxPrice', 'RiskLevel'
        ])

    def error(self, reqId, errorCode, errorString, advancedOrderReject=""):
        print("Error: ", reqId, " ", errorCode, " ", errorString)

    def nextValidId(self, orderId):
        self.reqAccountUpdates(True, "")
        self.reqAllOpenOrders()


    def updateAccountValue(self, key: str, val: str, currency: str, accountName: str):
        if key == 'TotalCashBalance' and currency == 'BASE':
            print("UpdateAccountValue. Key:", key, "Value:", val, "Currency:", currency, "AccountName:", accountName)
        if key == 'RealizedPnL' and currency == 'BASE':
            print("UpdateAccountValue. Key:", key, "Value:", val, "Currency:", currency, "AccountName:", accountName)


    def updatePortfolio(self, contract: Contract, position: float, marketPrice: float, marketValue: float,
                        averageCost: float, unrealizedPNL: float, realizedPNL: float, accountName: str):
        # print("UpdatePortfolio.", "Symbol:", contract.symbol, "SecType:", contract.secType, "Exchange:", contract.exchange,
        #       "Position:", position, "MarketPrice:", marketPrice, "MarketValue:", marketValue, "AverageCost:", averageCost,
        #       "UnrealizedPNL:", unrealizedPNL, "RealizedPNL:", realizedPNL, "AccountName:", accountName)
       
        # Append the new portfolio data to the DataFrame
        new_data = {
            'Symbol': contract.symbol,  
            'Position': int(position),  # Convert position to an integer
            'AverageCost': round(averageCost, 2),  # Round averageCost to 2 decimal places
        }
        # Append the new data to the portfolio DataFrame
        if contract.symbol != "IBKR":
            self.portfolio_df = self.portfolio_df._append(new_data, ignore_index=True)


    def openOrder(self, orderId: int, contract: Contract, order: Order, orderState: OrderState):
        print(
 
        "Symbol:", contract.symbol, 
        "Action:", order.action,  # SELL tarkoittaa longgiposition stoppia ja BUY shorttiposition stoppia
        "OrderType:", order.orderType, #STP
        "TotalQty:", order.totalQuantity, 
        "LmtPrice:", order.lmtPrice, 
        "AuxPrice:", order.auxPrice) # Triggerihinta
       
        # Find matching position in the portfolio DataFrame
        mask = (self.portfolio_df['Symbol'] == contract.symbol)
        matching_index = self.portfolio_df.index[mask]

        if not matching_index.empty:
            # Update the AuxPrice for the matched position
            self.portfolio_df.at[matching_index[0], 'AuxPrice'] = order.auxPrice
            print(f"Updated AuxPrice for {contract.symbol}: {order.auxPrice}")

        self.portfolio_df["RiskLevel"] = self.portfolio_df["Position"]*abs(self.portfolio_df["AuxPrice"] - self.portfolio_df["AverageCost"])

        print(self.portfolio_df)

def main():
    app = TestApp()
    app.connect("127.0.0.1", 7497, 0)
    app.run()
if __name__ == "__main__":
    main()

    