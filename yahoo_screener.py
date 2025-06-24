import yfscreen as yfs

most_actives = [
  ["eq", ["region", "us"]],
  ["btwn", ["intradaymarketcap", 2e9, 1e11]],
  ["gt", ["dayvolume", 5e6]]
]

day_losers = [
  ["lt", ["percentchange", -2.5]],
  ["gt", ["intradaymarketcap", 2e9]],
  ["gt", ["intradayprice", 5]],
  ["gt", ["dayvolume", 2e3]]
]

query = yfs.create_query(day_losers)

payload = yfs.create_payload("equity", query)
data = yfs.get_data(payload)


print(data["symbol"])
