import hashlib as hasher
import json
from datetime import datetime

import couchdb

user = "admin"
password = "password"
couchserver = couchdb.Server("http://%s:%s@127.0.0.1:5984/" % (user, password))

db = couchserver['blockchain']

TIME_FORMAT = '%Y:%m:%d:%H:%M:%s:%f'

class Block:

    def __init__(self, index, data, timestamp, prev_hash):

        self._index = index

        self._data = data

        self._timestamp = timestamp if isinstance(timestamp, str) else timestamp.strftime(TIME_FORMAT)

        self._prev_hash = prev_hash

        self._hash = self._get_hash()

    @property
    def hash(self):
        return self._hash

    def _get_hash(self):

        sha = hasher.sha256()

        _string = str(self._data) + str(self._prev_hash) + self._timestamp

        sha.update(_string.encode('utf8'))

        return sha.hexdigest()

    def __str__(self):

        return 'Block:%s hash:%s' % (self._index, self.hash)

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        return int(self._index) < int(other._index)

    def __lte__(self, other):
        return int(self._index) <= int(other._index)

    def __gt__(self, other):
        return int(self._index) > int(other._index)

    def __gte__(self, other):
        return int(self._index) >= int(other._index)

    def __eq__(self, other):
        return int(self._index) == int(other._index)

    def __ne__(self, other):
        return int(self._index) != int(other._index)


blocks = []

for item in db.view('block/block_view'):

    document = db.get(item.key)

    blocks.append(
        Block(
            int(item.key), 
            document['data'], 
            document['timestamp'], 
            document['prev_hash']
        )
    )

blocks = sorted(blocks)


if not len(blocks):

    block1 = Block(0, 'Hello, Morty', datetime.now(), '0')

    blocks = [block1, ]

    db[str(block1._index)] = {
        'data': block1._data,
        'timestamp': block1._timestamp, 
        'prev_hash': block1._prev_hash, 
        'hash': block1.hash
    }

_prev_block = blocks[-1]
_chain_length = len(blocks)

for index in range(_chain_length, _chain_length+3):

    data = 'Hello, Rick' if index % 2 else 'Hello, Morty'

    new_block = Block(str(index), data, datetime.now(), _prev_block.hash)

    blocks.append(new_block)

    db[new_block._index] = {
        'data': new_block._data,
        'timestamp': new_block._timestamp, 
        'prev_hash': new_block._prev_hash, 
        'hash': new_block.hash
    }

    _prev_block = new_block


_prev_block = blocks[0]
# проверка целостности блокчейна:
for block in blocks[1:]:

    _hash = _prev_block._get_hash()

    if _hash != block._prev_hash:

        print(_prev_block)
        print('Block is corrupted!')

    _prev_block = block
