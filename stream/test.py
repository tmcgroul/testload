import logging
import requests
import os
import json
import time


log = logging.getLogger(__name__)


class LoadTest(object):
    def __init__(self, gun):
        # portal-0
        self.portal = PortalClient('http://10.233.65.33:8080/datasets/solana-beta')

        # you'll be able to call gun's methods using this field:
        self.gun = gun

    def fetch_all(self, missile):
        with self.gun.measure("fetch_all"):
            for _ in self.run_stream(FETCH_ALL_QUERY, missile):
                pass

    def multiple_instructions(self, missile):
        with self.gun.measure("multiple_instructions"):
            for _ in self.run_stream(MULTIPLE_INS_QUERY, missile):
                pass

    def single_instruction(self, missile):
        with self.gun.measure("single_instruction"):
            for _ in self.run_stream(SINGLE_INS_QUERY, missile):
                pass

    def empty_query(self, missile):
        with self.gun.measure("empty_query"):
            for _ in self.run_stream(EMPTY_QUERY, missile):
                pass

    def run_stream(self, query, missile):
        start_time = time.time()
        from_block = int(missile)
        to_block = from_block + 500_000
        query = {**query, 'fromBlock': from_block, 'toBlock': to_block}
        last_block = None
        total_bytes = 0

        log.info('Starting stream')

        while True:
            if last_block is not None:
                query = {**query, 'fromBlock': last_block + 1}

            for line in self.portal.finalized_stream(query):
                total_bytes += len(line)
                block = json.loads(line)
                last_block = block['header']['number']
                yield block

            if last_block == query['toBlock']:
                end_time = time.time()
                elapsed = round(end_time - start_time, 1)
                progress = round(100_000 / elapsed, 1)
                throughput = round(total_bytes / 1024 / 1024 / elapsed, 1)
                log.info(f'Finished stream. Elapsed: {elapsed}. Speed: {progress} blocks/sec. Throughput: {throughput} MB/s')
                break

            else:
                log.warn('Restarting stream')

    def setup(self, param):
        ''' this will be executed in each worker before the test starts '''

    def teardown(self):
        ''' this will be executed in each worker after the end of the test '''
        # It's mandatory to explicitly stop worker process in teardown
        os._exit(0)


class PortalClient:
    def __init__(self, base_url):
        self._base_url = base_url

    def finalized_stream(self, query):
        url = self._base_url + '/finalized-stream/debug?buffer_size=70'
        while True:
            with requests.post(url, json=query, stream=True) as response:
                if response.status_code in (429, 503):
                    log.warn(f'Got {response.status_code}')
                    time.sleep(1)
                    continue
                elif response.status_code != 200:
                    log.warn(response.text)
                    response.raise_for_status()
                else:
                    for line in response.iter_lines():
                        yield line
                    break


ALL_FIELDS = {
    "balance": {
        "pre": True,
        "post": True
    },
    "log": {
        "programId": True,
        "instructionAddress": True,
        "kind": True,
        "message": True
    },
    "tokenBalance": {
        "preDecimals": True,
        "postDecimals": True,
        "postMint": True,
        "postAmount": True,
        "preAmount": True,
        "preOwner": True,
        "preMint": True,
        "postOwner": True
    },
    "instruction": {
        "accounts": True,
        "isCommitted": True,
        "programId": True,
        "data": True
    },
    "reward": {
        "lamports": True,
        "rewardType": True,
        "postBalance": True,
        "commission": True,
    },
    "transaction": {
        "signatures": True,
        "err": True,
        "version": True,
        "accountKeys": True,
        "addressTableLookups": True,
        "loadedAddresses": True,
        "feePayer": True,
    },
    "block": {
        "parentHash": True,
        "parentNumber": True,
        "number": True,
        "height": True,
        "timestamp": True
    }
}


FETCH_ALL_QUERY = {
    "type": "solana",
    "fields": ALL_FIELDS,
    "instructions": [{}],
    "transactions": [{}],
    "logs": [{}],
    "balances": [{}],
    "tokenBalances": [{}],
    "rewards": [{}],
}


MULTIPLE_INS_QUERY = {
    "type": "solana",
    "fields": ALL_FIELDS,
    "instructions": [
    {
      "d8": [
        "0x66063d1201daebea",
        "0x33e685a4017f83ad",
        "0x181ec828051c0777",
        "0xb712469c946da122"
      ],
      "programId": [
        "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
      ],
      "innerInstructions": True,
      "isCommitted": True,
      "transactionTokenBalances": True,
      "transaction": True
    },
    {
      "programId": [
        "MoonCVVNZFSYkqNXP6bxHLPL6QQJiMagDL3qcqUQTrG"
      ],
      "transaction": True,
      "transactionTokenBalances": True,
      "logs": True,
      "d8": [
        "0x032ca4b87b0df5b3",
        "0x2ae50ae7bd3ec1ae",
        "0x66063d1201daebea",
        "0x33e685a4017f83ad"
      ],
      "innerInstructions": True,
      "isCommitted": True
    },
    {
      "innerInstructions": True,
      "isCommitted": True,
      "d8": [
        "0xf8c69e91e17587c8",
        "0x2e9cf3760dcdfbb2",
        "0xa026d06f685b2c01",
        "0x5fb40aac54aee828",
        "0xcf2d57f21b3fcc43"
      ],
      "transactionTokenBalances": True,
      "programId": [
        "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc"
      ],
      "transaction": True
    },
    {
      "transactionTokenBalances": True,
      "programId": [
        "FLUXubRmkEi2q6K3Y9kBPg9248ggaZVsoSFhtJHSrm1X"
      ],
      "innerInstructions": True,
      "isCommitted": True,
      "d1": [
        "0x01",
        "0x02",
        "0x03",
        "0x00"
      ],
      "transaction": True
    },
    {
      "d1": [
        "0x09",
        "0x0b",
        "0x03",
        "0x01",
        "0x04"
      ],
      "isCommitted": True,
      "transactionTokenBalances": True,
      "innerInstructions": True,
      "programId": [
        "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
      ],
      "transaction": True
    },
    {
      "programId": [
        "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo"
      ],
      "transactionTokenBalances": True,
      "isCommitted": True,
      "transaction": True,
      "innerInstructions": True,
      "d8": [
        "0xf8c69e91e17587c8",
        "0xb59d59438fb63448",
        "0x1c8cee63e7a21595",
        "0x0703967f94283dc8",
        "0x2905eeaf64e106cd",
        "0x5e9b6797465fdca5",
        "0xa1c26754ab47fa9a",
        "0x5055d14818ceb16c",
        "0x0a333d2370691855",
        "0x1a526698f04a691a",
        "0x2d9aedd2dd0fa65c"
      ]
    },
    {
      "transaction": True,
      "programId": [
        "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB"
      ],
      "d8": [
        "0xf8c69e91e17587c8",
        "0x5454b142feb90afb",
        "0x4f237a54ad0f5dbf",
        "0x04e4d747e1fd77ce",
        "0x76ad299dad486167",
        "0x06874493e552a971",
        "0x856d2cb338ee7221",
        "0xa8e3323ebdab54b0",
        "0x07a68aabceabecf4"
      ],
      "transactionTokenBalances": True,
      "isCommitted": True,
      "innerInstructions": True
    },
    {
      "transactionTokenBalances": True,
      "d1": [
        "0x01",
        "0x02",
        "0x04",
        "0x03",
        "0x05"
      ],
      "transaction": True,
      "innerInstructions": True,
      "isCommitted": True,
      "programId": [
        "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP"
      ]
    }
  ],
}


SINGLE_INS_QUERY = {
    "type": "solana",
    "fields": ALL_FIELDS,
    "instructions": [
    {
      "d8": [
        "0xf8c69e91e17587c8",
        "0xb59d59438fb63448",
        "0x1c8cee63e7a21595",
        "0x0703967f94283dc8",
        "0x2905eeaf64e106cd",
        "0x5e9b6797465fdca5",
        "0xa1c26754ab47fa9a",
        "0x5055d14818ceb16c",
        "0x0a333d2370691855",
        "0x1a526698f04a691a",
        "0x2d9aedd2dd0fa65c"
      ],
      "transaction": True,
      "transactionTokenBalances": True,
      "innerInstructions": True,
      "isCommitted": True,
      "programId": [
        # "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwx1"
        "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo"
      ]
    }
  ],
}


EMPTY_QUERY = {
    "type": "solana",
    "fields": ALL_FIELDS,
    "instructions": [
    {
      "d8": [
        "0xf8c69e91e17587c8",
        "0xb59d59438fb63448",
        "0x1c8cee63e7a21595",
        "0x0703967f94283dc8",
        "0x2905eeaf64e106cd",
        "0x5e9b6797465fdca5",
        "0xa1c26754ab47fa9a",
        "0x5055d14818ceb16c",
        "0x0a333d2370691855",
        "0x1a526698f04a691a",
        "0x2d9aedd2dd0fa65c"
      ],
      "isCommitted": True,
      "programId": [
        "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwx1"
      ]
    }
  ],
}
