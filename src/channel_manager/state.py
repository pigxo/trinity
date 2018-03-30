"""Author: Trinity Core Team

MIT License

Copyright (c) 2018 Trinity

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

import os
from crypto import crypto_channel, uncryto_channel
from exception import ChannelDBAddFail, ChannelDBUpdateFail, ChannelExist, QureyRoleNotCorrect, ChannelNotExistInDb
from channel_manager.model import ChannelAddrDataBase, ChannelDatabase, Session, MessageDatabase


class ChannelAddress(object):
    """
    channel address managment
    """

    def __init__(self):
        pass

    def add_address(self, address, ip="NULL", port="NULL", public_key="NULL"):
        try:
            if self.query_address(address):
                print("query_address get %s" % address)
                Session.merge(ChannelAddrDataBase(address=address, ip=ip, port=port, public_key=public_key))
            else:
                Session.add(ChannelAddrDataBase(address=address, ip=ip, port=port, public_key=public_key))
            Session.commit()
        except:
            raise ChannelDBAddFail
        return None

    def delete_address(self, address):
        try:
            Session.query(ChannelAddrDataBase).filter(ChannelAddrDataBase.address == address).delete()
            Session.commit()
        except:
            raise
        return None

    def query_address(self, address):
        try:
            result = Session.query(ChannelAddrDataBase).filter(ChannelAddrDataBase.address == address).one()
        except:
            return None
        return result

    @staticmethod
    def get_publickey(address):
        try:
            result = Session.query(ChannelAddrDataBase).filter(ChannelAddrDataBase.address == address).one()
        except:
            return None
        return result.public_key

    def update_address(self, address, ip, port, public_key="NULL"):
        try:
            Session.merge(ChannelAddrDataBase(address=address, ip=ip, port=port, public_key=public_key))
            Session.commit()
        except:
            raise ChannelDBUpdateFail
        return None


class ChannelState(object):
    """
    Channel state
    """

    def __init__(self, channelname):
        self.match = None
        self.channelname = channelname
        self.qeury_channel()

    def qeury_channel(self):
        try:
            self.match = Session.query(ChannelDatabase).filter(ChannelDatabase.channel_name == self.channelname).one()
            return True
        except:
            return False

    @property
    def stateinDB(self):

        return self.match.state

    @property
    def senderinDB(self):
        return self.match.sender

    @property
    def recieverinDB(self):
        return self.match.receiver

    @property
    def receiver_deposit(self):
        return self.match.receiver_deposit

    @property
    def sender_deposit_cache(self):
        return self.match.sender_deposit_cache

    @property
    def receiver_deposit_cache(self):
        return self.match.receiver_deposit_cache

    @property
    def sender_deposit(self):
        return self.match.sender_deposit

    @property
    def tx_id(self):
        return self.match.tx_id if self.match else None

    @property
    def contract_address(self):
        return self.match.contract_address if self.match else None

    @property
    def contract_hash(self):
        return self.match.contract_hash if self.match else None

    @property
    def tx_data(self):
        return self.match.tx_data if self.match else None

    @property
    def signature(self):
        return self.match.signature if self.match else None

    @property
    def open_block_number(self):
        return self.match.open_block_number

    def add_channel_to_database(self, sender, receiver, state, sender_deposit, receiver_deposit,
                                open_block_number, settle_timeout, sender_deposit_cache, receiver_deposit_cache,
                                contract_address="", contract_hash="", tx_id="", start_block_number=0):
        channel_state = ChannelDatabase(receiver=receiver, sender=sender, channel_name=self.channelname, state=state.value,
                                        sender_deposit=sender_deposit, receiver_deposit=receiver_deposit,
                                        open_block_number=open_block_number, settle_timeout=settle_timeout,
                                        sender_deposit_cache=sender_deposit_cache,
                                        receiver_deposit_cache=receiver_deposit_cache,
                                        start_block_number=start_block_number,
                                        contract_address=contract_address,
                                        contract_hash=contract_hash)
        try:
            Session.add(channel_state)
            Session.commit()
        except:
            raise ChannelDBAddFail
        return None

    @staticmethod
    def query_channel_name(sender, receiver):
        channel1 = Session.query(ChannelDatabase).filter(ChannelDatabase.sender == sender). \
                filter(ChannelDatabase.receiver == receiver).filter(ChannelDatabase.state !=5).all()
        channel2 = Session.query(ChannelDatabase). \
                filter(ChannelDatabase.sender == receiver). \
                filter(ChannelDatabase.receiver == sender).filter(ChannelDatabase.state !=5).all()
        channel = channel1 if channel1 else channel2
        return channel[0].channel_name if channel else None

    def update_channel_to_database(self, **kwargs):
        self.qeury_channel()
        try:
            for key, value in kwargs.items():
                setattr(self.match, key, value)
            Session.commit()
        except:
            raise ChannelDBUpdateFail
        return None

    def update_channel_state(self, state):
        try:
            ch = Session.query(ChannelDatabase).filter(ChannelDatabase.channel_name == self.channelname).one()
            ch.state = state.value
            Session.commit()
            return True
        except:
            raise ChannelDBUpdateFail

    def update_deposit_cache(self, sender_deposit_cache, receiver_deposit_cache):
        try:
            ch = Session.query(ChannelDatabase).filter(ChannelDatabase.channel_name == self.channelname).one()
            ch.sender_deposit_cache = sender_deposit_cache
            ch.receiver_deposit_cache = receiver_deposit_cache
            Session.commit()
            return True
        except:
            raise ChannelDBUpdateFail

    def update_channel_deposit(self, sender_deposit, receiver_deposit):
        try:
            ch = Session.query(ChannelDatabase).filter(ChannelDatabase.channel_name == self.channelname).one()
            ch.sender_deposit = sender_deposit
            ch.receiver_deposit = receiver_deposit
            Session.commit()
            return True
        except:
            raise ChannelDBUpdateFail


    def delete_channel_in_database(self):
        try:
            Session.query(ChannelDatabase).filter(ChannelDatabase.channel_name == self.channelname).delete()
            Session.commit()
        except:
            raise
        return None

    def update_txid(self, tx_id):
        try:
            ch = Session.query(ChannelDatabase).filter(ChannelDatabase.channel_name == self.channelname).one()
            ch.tx_id = tx_id
            Session.commit()
            return True
        except:
            raise ChannelDBUpdateFail

    def update_sender_signature(self, signature):
        try:
            ch = Session.query(ChannelDatabase).filter(ChannelDatabase.channel_name == self.channelname).one()
            ch.sendersignature = signature
            Session.commit()
            return True
        except:
            raise ChannelDBUpdateFail

    def update_receiver_signature(self, signature):
        try:
            ch = Session.query(ChannelDatabase).filter(ChannelDatabase.channel_name == self.channelname).one()
            ch.receiversignature = signature
            Session.commit()
            return True
        except:
            raise ChannelDBUpdateFail

    @property
    def sender_signature(self):
        try:
            ch = Session.query(ChannelDatabase).filter(ChannelDatabase.channel_name == self.channelname).one()
            return ch.sendersignature
        except:
            return None

    @property
    def receiver_signature(self):
        try:
            ch = Session.query(ChannelDatabase).filter(ChannelDatabase.channel_name == self.channelname).one()
            return ch.receiversignature
        except:
            return None



class Message(object):
    """

    """

    @staticmethod
    def push_message(address, type, message, channel_name):
        m = MessageDatabase(address=address, type=type, message=message, channel_name=channel_name, state="pending")
        Session.add(m)
        Session.commit()

    @staticmethod
    def set_message_done(address, channel_name):
        message = Session.query(MessageDatabase).filter(MessageDatabase.address == address).\
            filter(MessageDatabase.channel_name == channel_name).all()
        if message:
            message[0].state = "done"
            Session.commit()
        return None

    @staticmethod
    def pull_message(address):
        message_info = {}
        messages = Session.query(MessageDatabase).filter(MessageDatabase.address == address). \
            filter(MessageDatabase.state == "pending").all()
        for m in messages:
            message_info.setdefault("channel_name", m.channel_name)
            message_info.setdefault("raw_tx", m.message)
        Session.commit()
        return message_info


class ChannelFile(object):
    """

    """
    PATH = os.path.dirname(__file__)

    @property
    def channel_file_name(self):
        return "{}.data".format(os.path.join(self.PATH, self.channel_name))

    def create_channelfile(self, **kwargs):
        if os.path.exists(self.channel_file_name):
            raise ChannelExist
        else:
            self.update_channel(**kwargs)

    def update_channel(self, **kwargs):
        with open(self.channel_file_name, "ab+") as f:
            crypto_channel(f, **kwargs)
        return None

    def read_channel(self):
        with open(self.channel_file_name, "rb") as f:
            return uncryto_channel(f)

    def delete_channel(self):
        return os.remove(self.channel_file_name)

    def has_channel_file(self):
        return os.path.exists(self.channel_file_name)


def query_channel_from_address(address, role="both"):
    if role not in ("both", "sender", "receiver"):
        raise QureyRoleNotCorrect
    if role == "sender":
        return Session.query(ChannelDatabase).filter(ChannelDatabase.sender == address).all()
    elif role == "receiver":
        return Session.query(ChannelDatabase).filter(ChannelDatabase.receiver == address).all()
    else:
        result = Session.query(ChannelDatabase).filter(ChannelDatabase.sender == address).all()
        result.extend(Session.query(ChannelDatabase).filter(ChannelDatabase.receiver == address).all())
        return result


if __name__ == "__main__":
    from channel_manager.channel import State

    channel = ChannelAddress()
    # channel.add_channle_to_database(sender="test_sender", sender_deposit=10, receiver="test_receiver", receiver_deposit=20, channel_name="testchannlenametest",
    #                               open_block_number=1000, settle_timeout=100, state=State.OPENING)
    # channel.add_channle_to_database(sender="test_sender", sender_deposit=10, receiver="test_receiver",
    #                              receiver_deposit=20, channel_name="testchannelname",
    #                               open_block_number=1000, settle_timeout=100, state=State.OPENING)
    result = channel.add_address("test_sender1dt11", "10.10.101.01")
    print(result)
